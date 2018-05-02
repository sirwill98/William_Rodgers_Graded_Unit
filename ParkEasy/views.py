from django.views.generic import ListView
from .models import Customer, Booking
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import BookingCreationFormCustomer, CustomerCreationFormUser
from William_Rodgers_Graded_Unit import settings
import stripe
import datetime
stripe.api_key = settings.STRIPE_SECRET_KEY


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
            request.session['booking'] = newbooking1
            return render(request, 'payment-form.html')
        else:
            return render(request, 'booking.html', {'form': form})
    else:
        form = BookingCreationFormCustomer()

    return render(request, 'booking.html', {'form': form})


def checkout(request):

    booking = request.session.get('booking', None)
    if request.method == "POST":
        token = request.POST.get("stripeToken")

    try:
        charge = stripe.Charge.create(
            amount=2000,
            currency="usd",
            source=token,
            description="The product charged to the user"
        )

        booking.charge_id = charge.id

    except stripe.error.CardError as ce:
        return False, ce

    else:
        booking.save()
        return redirect("home")
        # The payment was successfully processed, the user's card was charged.
        # You can now redirect the user to another page or whatever you want

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


def payment_form(request):

    context = {"stripe_key": settings.STRIPE_PUBLIC_KEY}
    return render(request, "payment-form.html", context)
