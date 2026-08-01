from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('book/', views.book_appointment, name='book'),
    path('admin-queue/', views.admin_queue_view, name='admin_queue'),
    path('call-next/<int:appointment_id>/', views.call_next_view, name='call_next'),
    path('approve-booking/<int:appointment_id>/', views.approve_booking_view, name='approve_booking'),
    path('cancel-booking/<int:appointment_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('delay-booking/<int:appointment_id>/', views.delay_booking_view, name='delay_booking'),
    path('ml-playground/', views.ml_playground_view, name='ml_playground'),
]
