from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'user', 'service', 'appointment_date', 'status', 'created_at')
    list_filter = ('status', 'service', 'appointment_date')
    search_fields = ('user__username', 'token_number')
