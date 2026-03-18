import math
import os
from datetime import date

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import Attendance, Employee
from .face_utils import compare_faces


# ── Helper ──────────────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    R  = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a  = math.sin(dp / 2) * 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) * 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_today_record(user_id):
    return Attendance.objects.filter(user_id=user_id, date=date.today()).first()


# ── Page Views ───────────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        user_id   = request.POST.get('user_id', '').strip()
        user_name = request.POST.get('user_name', '').strip()

        if not user_id or not user_name:
            return render(request, 'attendance/login.html',
                          {'error': 'Please fill in both fields.'})

        # Check if employee is registered
        try:
            employee = Employee.objects.get(user_id=user_id)
            if employee.user_name.lower() != user_name.lower():
                return render(request, 'attendance/login.html',
                              {'error': 'Name does not match our records.'})
        except Employee.DoesNotExist:
            return render(request, 'attendance/login.html',
                          {'error': 'Employee not registered. Please contact admin.',
                           'show_register': True})

        request.session['user_id']   = user_id
        request.session['user_name'] = user_name
        return redirect('dashboard')

    return render(request, 'attendance/login.html')


def register_view(request):
    """Employee registration with face photo."""
    if request.method == 'POST':
        user_id   = request.POST.get('user_id', '').strip()
        user_name = request.POST.get('user_name', '').strip()
        email     = request.POST.get('email', '').strip()
        face_img  = request.FILES.get('face_image')

        if not user_id or not user_name or not email or not face_img:
            return render(request, 'attendance/register.html',
                          {'error': 'All fields are required.'})

        # Check duplicate
        if Employee.objects.filter(user_id=user_id).exists():
            return render(request, 'attendance/register.html',
                          {'error': 'Employee ID already registered.'})

        if Employee.objects.filter(email=email).exists():
            return render(request, 'attendance/register.html',
                          {'error': 'Email already registered.'})

        Employee.objects.create(
            user_id    = user_id,
            user_name  = user_name,
            email      = email,
            face_image = face_img,
        )

        return render(request, 'attendance/register.html',
                      {'success': f'Employee {user_name} registered successfully! You can now login.'})

    return render(request, 'attendance/register.html')


def dashboard_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id   = request.session['user_id']
    user_name = request.session['user_name']
    record    = get_today_record(user_id)

    if record and record.checkout_time:
        status = 'checked_out'
    elif record and record.checkin_time:
        status = 'checked_in'
    else:
        status = 'not_checked_in'

    return render(request, 'attendance/dashboard.html', {
        'user_id':   user_id,
        'user_name': user_name,
        'status':    status,
        'record':    record,
        'shop_lat':  settings.SHOP_LATITUDE,
        'shop_lng':  settings.SHOP_LONGITUDE,
        'max_dist':  settings.MAX_DISTANCE_METERS,
    })


def history_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id   = request.session['user_id']
    user_name = request.session['user_name']
    records   = Attendance.objects.filter(user_id=user_id).order_by('-date')

    total     = records.count()
    completed = records.filter(checkout_time__isnull=False).count()

    records_data = []
    for r in records:
        records_data.append({
            'id':                 r.id,
            'date':               str(r.date),
            'checkin_time':       r.checkin_time.strftime('%d/%m/%Y %H:%M') if r.checkin_time else None,
            'checkout_time':      r.checkout_time.strftime('%d/%m/%Y %H:%M') if r.checkout_time else None,
            'checkin_lat':        r.checkin_lat,
            'checkin_lng':        r.checkin_lng,
            'checkin_image_url':  r.checkin_image.url if r.checkin_image else None,
            'checkout_image_url': r.checkout_image.url if r.checkout_image else None,
            'duration':           r.duration,
            'face_verified':      r.face_verified,
        })

    return render(request, 'attendance/history.html', {
        'user_id':   user_id,
        'user_name': user_name,
        'records':   records_data,
        'total':     total,
        'completed': completed,
        'pending':   total - completed,
    })


def logout_view(request):
    request.session.flush()
    return redirect('login')


# ── API Views ────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def checkin_view(request):
    user_id   = request.POST.get('user_id', '').strip()
    user_name = request.POST.get('user_name', '').strip()
    image     = request.FILES.get('image')

    try:
        lat = float(request.POST.get('latitude'))
        lng = float(request.POST.get('longitude'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid GPS coordinates.'}, status=400)

    if not user_id or not user_name or not image:
        return JsonResponse({'success': False, 'error': 'Missing required fields.'}, status=400)

    # GPS distance check
    distance = haversine(lat, lng, settings.SHOP_LATITUDE, settings.SHOP_LONGITUDE)
    if distance > settings.MAX_DISTANCE_METERS:
        return JsonResponse({
            'success': False,
            'error': f'You are not near the shop. Please move closer. (Distance: {distance:.1f}m)'
        }, status=400)

    # Duplicate check
    today = date.today()
    if Attendance.objects.filter(user_id=user_id, date=today).exists():
        return JsonResponse({'success': False, 'error': 'You have already checked in today.'}, status=400)

    # ── Face Verification ──
    try:
        employee = Employee.objects.get(user_id=user_id)
        registered_image_path = os.path.join(settings.MEDIA_ROOT, str(employee.face_image))

        # Read selfie bytes
        selfie_bytes = image.read()
        image.seek(0)  # Reset file pointer after reading

        face_match, confidence, face_message = compare_faces(
            registered_image_path,
            selfie_bytes
        )

        if not face_match:
            return JsonResponse({
                'success': False,
                'error': f'Face verification failed! {face_message}'
            }, status=400)

    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee not registered. Please contact admin.'
        }, status=400)

    # Save record
    now = timezone.now()
    record = Attendance.objects.create(
        user_id       = user_id,
        user_name     = user_name,
        date          = today,
        checkin_time  = now,
        checkin_lat   = lat,
        checkin_lng   = lng,
        checkin_image = image,
        face_verified = True,
    )

    return JsonResponse({
        'success':      True,
        'message':      f'Check-in successful! Face verified ({confidence}% match)',
        'record_id':    record.id,
        'checkin_time': now.strftime('%H:%M:%S'),
        'distance':     round(distance, 2),
        'confidence':   confidence,
    })


@csrf_exempt
@require_POST
def checkout_view(request):
    user_id = request.POST.get('user_id', '').strip()
    image   = request.FILES.get('image')

    try:
        lat = float(request.POST.get('latitude'))
        lng = float(request.POST.get('longitude'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid GPS coordinates.'}, status=400)

    if not user_id or not image:
        return JsonResponse({'success': False, 'error': 'Missing required fields.'}, status=400)

    # GPS check
    distance = haversine(lat, lng, settings.SHOP_LATITUDE, settings.SHOP_LONGITUDE)
    if distance > settings.MAX_DISTANCE_METERS:
        return JsonResponse({
            'success': False,
            'error': 'You are not near the shop. Please move closer.'
        }, status=400)

    # ── Face Verification ──
    try:
        employee = Employee.objects.get(user_id=user_id)
        registered_image_path = os.path.join(settings.MEDIA_ROOT, str(employee.face_image))

        selfie_bytes = image.read()
        image.seek(0)

        face_match, confidence, face_message = compare_faces(
            registered_image_path,
            selfie_bytes
        )

        if not face_match:
            return JsonResponse({
                'success': False,
                'error': f'Face verification failed! {face_message}'
            }, status=400)

    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee not registered.'
        }, status=400)

    # Find today's active check-in
    record = Attendance.objects.filter(
        user_id=user_id,
        date=date.today(),
        checkin_time__isnull=False,
        checkout_time__isnull=True
    ).first()

    if not record:
        return JsonResponse({
            'success': False,
            'error': 'No active check-in found. Please check in first.'
        }, status=400)

    now = timezone.now()
    record.checkout_time  = now
    record.checkout_lat   = lat
    record.checkout_lng   = lng
    record.checkout_image = image
    record.face_verified  = True
    record.save()

    return JsonResponse({
        'success':       True,
        'message':       f'Check-out successful! Face verified ({confidence}% match)',
        'checkout_time': now.strftime('%H:%M:%S'),
        'distance':      round(distance, 2),
        'confidence':    confidence,
    })


@require_GET
def today_status_view(request, user_id):
    record = get_today_record(user_id)
    if not record:
        return JsonResponse({'status': 'not_checked_in', 'checkin_time': None, 'checkout_time': None})
    return JsonResponse({
        'status':        'checked_out' if record.checkout_time else 'checked_in',
        'checkin_time':  record.checkin_time.strftime('%H:%M')  if record.checkin_time  else None,
        'checkout_time': record.checkout_time.strftime('%H:%M') if record.checkout_time else None,
    })


@require_GET
def user_records_view(request, user_id):
    records = Attendance.objects.filter(user_id=user_id).order_by('-date')
    data = []
    for r in records:
        data.append({
            'id':                r.id,
            'date':              str(r.date),
            'checkin_time':      r.checkin_time.strftime('%H:%M')  if r.checkin_time  else None,
            'checkout_time':     r.checkout_time.strftime('%H:%M') if r.checkout_time else None,
            'checkin_lat':       r.checkin_lat,
            'checkin_lng':       r.checkin_lng,
            'checkin_image_url': r.checkin_image.url  if r.checkin_image  else None,
            'checkout_image_url':r.checkout_image.url if r.checkout_image else None,
            'duration':          r.duration,
            'face_verified':     r.face_verified,
        })
    return JsonResponse({'user_id': user_id, 'total': len(data), 'records': data})