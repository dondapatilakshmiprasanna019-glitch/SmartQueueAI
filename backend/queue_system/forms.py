from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'appointment_date', 'appointment_time', 'priority', 'organization_name', 'department', 'doctor_or_counter', 'estimated_wait_time', 'confidence_score', 'distance']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'input-box'}),
            'appointment_time': forms.TextInput(attrs={'placeholder': 'e.g., 09:30 AM', 'class': 'input-box'}),
            'priority': forms.Select(attrs={'class': 'input-box'}),
            'service': forms.Select(attrs={'class': 'input-box'}),
            'organization_name': forms.TextInput(attrs={'class': 'input-box'}),
            'department': forms.TextInput(attrs={'class': 'input-box'}),
            'doctor_or_counter': forms.TextInput(attrs={'class': 'input-box'}),
            'estimated_wait_time': forms.NumberInput(attrs={'class': 'input-box'}),
            'confidence_score': forms.NumberInput(attrs={'class': 'input-box'}),
            'distance': forms.TextInput(attrs={'class': 'input-box'}),
        }
