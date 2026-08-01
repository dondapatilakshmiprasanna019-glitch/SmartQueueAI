from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment
from .forms import AppointmentForm


@login_required
def book_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user

            count = Appointment.objects.count() + 1
            appointment.token_number = f"A-{count:03d}"

            appointment.save()

            return redirect("dashboard")

    else:
        form = AppointmentForm()

    return render(
        request,
        "queue_system/book.html",
        {"form": form}
    )