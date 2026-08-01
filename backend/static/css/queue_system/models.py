from django.db import models
from django.contrib.auth.models import User


class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('Hospital', 'Hospital'),
        ('Bank', 'Bank'),
        ('University', 'University'),
        ('Government', 'Government'),
        ('Service Center', 'Service Center'),
    ]

    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Serving', 'Serving'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    appointment_date = models.DateField()
    token_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token_number} - {self.user.username}"