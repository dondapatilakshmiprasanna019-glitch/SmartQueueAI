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
    path('services/hospital/', views.hospital_service_view, name='hospital_service'),
    path('services/bank/', views.bank_service_view, name='bank_service'),
    path('services/university/', views.university_service_view, name='university_service'),
    path('services/government/', views.government_service_view, name='government_service'),
    path('services/service-center/', views.service_center_service_view, name='service_center_service'),
]
