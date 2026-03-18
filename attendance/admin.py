from django.contrib import admin
from .models import Attendance, Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ['user_id', 'user_name', 'email', 'created_at']
    search_fields = ['user_id', 'user_name', 'email']
    ordering      = ['-created_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display  = ['user_id', 'user_name', 'date', 'checkin_time', 'checkout_time', 'face_verified']
    list_filter   = ['date', 'face_verified']
    search_fields = ['user_id', 'user_name']
    ordering      = ['-date']