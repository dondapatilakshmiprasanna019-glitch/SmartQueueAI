from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, Notification
from .forms import AppointmentForm
from .ai_predictor import predictor
import datetime
import json

@login_required
def book_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            count = Appointment.objects.count() + 1
            appointment.token_number = f"A-{count:03d}"
            
            # Setup dynamic priority logic and reasons
            if appointment.priority == 'Emergency':
                appointment.priority_reason = "Critical emergency bypass routing assigned."
            elif appointment.priority == 'Senior Citizen':
                appointment.priority_reason = "Automatic priority lane for elder assistance (60+)."
            elif appointment.priority == 'VIP':
                appointment.priority_reason = "VIP client routing privilege."
            else:
                appointment.priority_reason = "Standard regular queue sequencing rule."
                
            # Calculate wait predictions using scikit-learn random forest
            avg_service_time = {
                'Hospital': 15, 'Bank': 8, 'University': 12, 'Government': 22, 'Service Center': 10
            }.get(appointment.service, 10)
            
            # Temporarily save to get created_at for query filtering, or just count existing
            people_ahead = Appointment.objects.filter(
                status='Waiting',
                appointment_date=appointment.appointment_date
            ).count()
            
            # Day of week
            day_of_week = appointment.appointment_date.weekday()
            
            pred, conf, crowd = predictor.predict(
                people_ahead=people_ahead,
                avg_service_time=avg_service_time,
                department=appointment.service,
                priority=appointment.priority,
                hour=10.0, # default morning hour
                day_of_week=day_of_week
            )
            
            appointment.estimated_wait_time = pred
            appointment.confidence_score = conf
            appointment.save()
            
            # Create a notification in the database
            Notification.objects.create(
                user=request.user,
                message=f"Appointment Booked! Token: {appointment.token_number} at {appointment.organization_name}. Predicted wait: {pred} mins (Confidence: {conf}%)."
            )
            
            messages.success(
                request, 
                f"Booking confirmed! Token: {appointment.token_number} generated. "
                f"ML-Predicted wait: {pred} mins (Confidence: {conf}%, Crowd: {crowd})."
            )
            return redirect("dashboard")
    else:
        service_param = request.GET.get('service')
        if service_param in ['Hospital', 'Bank', 'University', 'Government', 'Service Center']:
            form = AppointmentForm(initial={'service': service_param})
        else:
            form = AppointmentForm()
        
    # Calculate recommended slots for display
    hours = [9, 10, 11, 12, 13, 14, 15, 16]
    hour_loads = {9: 2, 10: 5, 11: 9, 12: 4, 13: 3, 14: 6, 15: 8, 16: 11}
    services = ['Hospital', 'Bank', 'University', 'Government', 'Service Center']
    
    recommendations = {}
    for service in services:
        slot_predictions = []
        for h in hours:
            avg_time = {'Hospital': 15, 'Bank': 8, 'University': 12, 'Government': 22, 'Service Center': 10}.get(service, 10)
            pred, conf, crowd = predictor.predict(
                people_ahead=hour_loads[h],
                avg_service_time=avg_time,
                department=service,
                priority='Regular',
                hour=h,
                day_of_week=1 # Tuesday
            )
            time_str = f"{h if h <= 12 else h-12}:00 {'AM' if h < 12 else 'PM'}"
            slot_predictions.append((time_str, pred))
            
        slot_predictions.sort(key=lambda x: x[1])
        recommendations[service] = [
            {"time": time_str, "wait": f"{pred} mins"} for time_str, pred in slot_predictions[:3]
        ]
        
    context = {
        'form': form,
        'recommendations_json': json.dumps(recommendations)
    }
    return render(request, "queue_system/book.html", context)

@login_required
def dashboard_view(request):
    total = Appointment.objects.count()
    waiting = Appointment.objects.filter(status='Waiting').count()
    serving = Appointment.objects.filter(status='Serving').count()
    completed = Appointment.objects.filter(status='Completed').count()
    cancelled = Appointment.objects.filter(status='Cancelled').count()

    latest_appointment = Appointment.objects.filter(user=request.user).order_by('-created_at').first()
    current_serving = Appointment.objects.filter(status='Serving').first()
    
    # Retrieve user notifications
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:6]
    
    # Defaults
    people_ahead = 0
    wait_time = 0
    confidence = 94
    crowd_level = "Low"
    is_crowded = False
    suggested_slot = "2:30 PM"
    suggested_wait = "5 Minutes"
    
    if latest_appointment and latest_appointment.status in ['Waiting', 'Serving']:
        people_ahead = Appointment.objects.filter(
            status='Waiting',
            appointment_date=latest_appointment.appointment_date,
            created_at__lt=latest_appointment.created_at
        ).count()
        
        avg_time = {'Hospital': 15, 'Bank': 8, 'University': 12, 'Government': 22, 'Service Center': 10}.get(latest_appointment.service, 10)
        hour = latest_appointment.created_at.hour if latest_appointment.created_at else 10.0
        day = latest_appointment.appointment_date.weekday()
        
        wait_time, confidence, crowd_level = predictor.predict(
            people_ahead=people_ahead,
            avg_service_time=avg_time,
            department=latest_appointment.service,
            priority=latest_appointment.priority,
            hour=hour,
            day_of_week=day
        )
        
        # If crowded, enable smart slot recommendations
        if wait_time > 15:
            is_crowded = True
            
    # Gather database distribution map for charts
    services = ['Hospital', 'Bank', 'University', 'Government', 'Service Center']
    chart_distribution = {s: Appointment.objects.filter(service=s).count() for s in services}
    
    # If no data, populate some synthetic values for charts to render nicely
    if sum(chart_distribution.values()) == 0:
        chart_distribution = {'Hospital': 14, 'Bank': 25, 'University': 18, 'Government': 9, 'Service Center': 12}
        
    # Fetch upcoming and previous lists for user dashboard blocks
    upcoming_appointments = Appointment.objects.filter(user=request.user, status__in=['Waiting', 'Serving']).order_by('appointment_date')
    previous_appointments = Appointment.objects.filter(user=request.user, status__in=['Completed', 'Cancelled']).order_by('-appointment_date')
        
    context = {
        'total': total,
        'waiting': waiting,
        'serving': serving,
        'completed': completed,
        'cancelled': cancelled,
        'latest_appointment': latest_appointment,
        'current_serving': current_serving,
        'people_ahead': people_ahead,
        'wait_time': wait_time,
        'confidence': confidence,
        'crowd_level': crowd_level,
        'is_crowded': is_crowded,
        'suggested_slot': suggested_slot,
        'suggested_wait': suggested_wait,
        'notifications': user_notifications,
        'upcoming_appointments': upcoming_appointments,
        'previous_appointments': previous_appointments,
        'chart_distribution_json': json.dumps(chart_distribution)
    }
    return render(request, 'accounts/dashboard.html', context)

def admin_queue_view(request):
    # Enable priority-based ordering (Emergency first, Senior Citizen second, VIP third, Regular last)
    appointments = Appointment.objects.all().order_by('appointment_date', 'status', 'priority', 'token_number')
    
    # Stats for admin report
    total = Appointment.objects.count()
    completed = Appointment.objects.filter(status='Completed').count()
    waiting = Appointment.objects.filter(status='Waiting').count()
    
    context = {
        'appointments': appointments,
        'total': total,
        'completed': completed,
        'waiting': waiting
    }
    return render(request, 'queue_system/admin_queue.html', context)

def call_next_view(request, appointment_id):
    Appointment.objects.filter(status='Serving').update(status='Completed')
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Serving'
    appointment.save()
    
    # Notify customer that it's their turn
    Notification.objects.create(
        user=appointment.user,
        message=f"It's your turn! Token {appointment.token_number} has been called. Please proceed to the counter."
    )
    
    messages.info(
        request, 
        f"Token {appointment.token_number} is now active! "
        f"Alert dispatched to {appointment.user.username}'s contact number."
    )
    return redirect('admin_queue')

def approve_booking_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.is_approved = True
    appointment.save()
    
    Notification.objects.create(
        user=appointment.user,
        message=f"Your booking for token {appointment.token_number} has been approved by admin."
    )
    
    messages.success(request, f"Booking {appointment.token_number} has been approved.")
    return redirect('admin_queue')

def cancel_booking_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Cancelled'
    appointment.save()
    
    Notification.objects.create(
        user=appointment.user,
        message=f"Your booking for token {appointment.token_number} was cancelled."
    )
    
    messages.warning(request, f"Booking {appointment.token_number} has been cancelled.")
    return redirect('admin_queue')

def delay_booking_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.estimated_wait_time = appointment.estimated_wait_time + 15
    appointment.priority_reason = f"Delayed by admin. New wait time estimate updated."
    appointment.save()
    
    Notification.objects.create(
        user=appointment.user,
        message=f"Your appointment for token {appointment.token_number} has been delayed by 15 minutes."
    )
    
    messages.warning(request, f"Booking {appointment.token_number} has been delayed by 15 minutes.")
    return redirect('admin_queue')

def ml_playground_view(request):
    from django.http import JsonResponse
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        people_ahead = int(request.GET.get('people_ahead', 0))
        avg_service_time = float(request.GET.get('avg_service_time', 10.0))
        department = request.GET.get('department', 'Hospital')
        priority = request.GET.get('priority', 'Regular')
        hour = float(request.GET.get('hour', 10.0))
        day_of_week = int(request.GET.get('day_of_week', 1))
        
        pred, conf, crowd = predictor.predict(
            people_ahead=people_ahead,
            avg_service_time=avg_service_time,
            department=department,
            priority=priority,
            hour=hour,
            day_of_week=day_of_week
        )
        return JsonResponse({
            'wait_time': pred,
            'confidence': conf,
            'crowd_level': crowd
        })
        
    return render(request, 'queue_system/ml_playground.html')
# force reload comment
