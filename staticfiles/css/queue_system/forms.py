from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'appointment_date']

        widgets = {
            'appointment_date': forms.DateInput(
                attrs={'type': 'date'}
            )
        }