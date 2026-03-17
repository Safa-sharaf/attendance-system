from django.contrib import admin
from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display  = ['user_id', 'user_name', 'date', 'checkin_time', 'checkout_time']
    list_filter   = ['date', 'user_id']
    search_fields = ['user_id', 'user_name']
    ordering      = ['-date']

# Register your models here.
