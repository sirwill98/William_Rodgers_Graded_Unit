from django.views.generic import ListView
from .models import Customer, Booking
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import BookingCreationFormCustomer, CustomerCreationFormUser


class HomePageView(ListView):
    model = Customer
    template_name = 'home.html'


class BookingView(ListView):
    model = Booking
    template_name = 'booking.html'


def booking_form(request):
    if request.POST:
        form = BookingCreationFormCustomer(request.POST)
        if form.is_valid() & request.user.is_authenticated:
            start = form.cleaned_data.get('Start')
            end = form.cleaned_data.get('End')
            length = end - start
            length = length.days
            cust = Customer.objects.get(email=request.user.email)
            newbooking1 = Booking(customer=cust, booking_date=start, booking_length=length)
            newbooking1.save()
        else:
            return render(request, 'booking.html', {'form': form})
    else:
        form = BookingCreationFormCustomer()

    return render(request, 'booking.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = CustomerCreationFormUser(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = CustomerCreationFormUser()
    return render(request, 'registration/signup.html', {'form': form})

