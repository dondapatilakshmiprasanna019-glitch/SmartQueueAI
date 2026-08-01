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
        ('Cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('Emergency', 'Emergency'),
        ('Senior Citizen', 'Senior Citizen'),
        ('VIP', 'VIP'),
        ('Regular', 'Regular'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    organization_name = models.CharField(max_length=100, default='City General Hospital')
    department = models.CharField(max_length=100, default='General Medicine')
    doctor_or_counter = models.CharField(max_length=100, default='Counter 1', blank=True, null=True)
    estimated_wait_time = models.IntegerField(default=15)
    confidence_score = models.IntegerField(default=95)
    distance = models.CharField(max_length=20, default='1.2 km')
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=10, default='09:00 AM')
    token_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Regular')
    priority_reason = models.CharField(max_length=255, default='Standard regular queuing rule')
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token_number} - {self.user.username} ({self.service})"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"
