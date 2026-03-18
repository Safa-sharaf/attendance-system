from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('',            views.login_view,     name='login'),
    path('register/',   views.register_view,  name='register'),
    path('dashboard/',  views.dashboard_view, name='dashboard'),
    path('history/',    views.history_view,   name='history'),
    path('logout/',     views.logout_view,    name='logout'),

    # API endpoints
    path('attendance/checkin/',                  views.checkin_view,      name='checkin'),
    path('attendance/checkout/',                 views.checkout_view,     name='checkout'),
    path('attendance/today/<str:user_id>/',      views.today_status_view, name='today_status'),
    path('attendance/user/<str:user_id>/',       views.user_records_view, name='user_records'),
]