from django.views.generic import ListView
from .models import Customer, Booking, Prices
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import BookingCreationFormCustomer, CustomerCreationFormUser, CustomerChangeFormCustomer
from William_Rodgers_Graded_Unit import settings
from datetime import timedelta
import stripe
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
stripe.api_key = settings.STRIPE_SECRET_KEY


def HomePageView(request):
    if request.POST:
        form = BookingCreationFormCustomer(request.POST)
    else:
        form = BookingCreationFormCustomer()

    return render(request, 'home.html', {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


class BookingView(ListView):
    model = Booking
    template_name = 'booking.html'


def booking_form(request):
    if request.POST:
        form = BookingCreationFormCustomer(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                start = form.cleaned_data.get('Start')
                end = form.cleaned_data.get('End')
                length = end - start
                length = length.days
                if length < 0:
                    return render(request, 'booking.html', {'form': form})
                    #ADD ERROR MESSAGE
                cust = Customer.objects.get(email=request.user.email)
                price = Prices.objects.get(is_current=True)
                newbooking1 = Booking(customer=cust, booking_date=start, booking_length=length, prices=price)
                request.session['booking'] = newbooking1
                days = length
                request.session['days'] = days
                amount = Booking.calc_amount(newbooking1, length)
                request.session['num_amount'] = amount
                request.session['amount'] = str(amount) + "00"
                return render(request, 'payment-form.html', {'form': form})
            else:
                return render(request, 'registration/login.html', {'form': form})
        else:
            return render(request, 'booking.html', {'form': form})
    else:
        form = BookingCreationFormCustomer()

    return render(request, 'booking.html', {'form': form})


def checkout(request):
    new_booking = request.session['booking']

    if request.method == "POST":
        token = request.POST.get("stripeToken")

    try:
        charge = stripe.Charge.create(
            amount=request.session['amount'],
            currency="gbp",
            source=token,
            description="The product charged to the user"
        )

        new_booking.charge_id = charge.id

    except stripe.error.CardError as ce:
        return False, ce

    else:
        new_booking.save()
        send_mail(
            'ParkEasy Parking Booking',
            'thank you '+request.user.email+' for creating a booking with ParkEasy below are details of your booking'
            + "\n" +
            'Price : £' + request.session['amount'][:-2] + "\n" +
            'Beginning date : ' + str(request.session['booking'].booking_date) + "\n" +
            'End date : ' +
            str(request.session['booking'].booking_date + timedelta(days=request.session['booking'].booking_length)),
            'ParkEasyAirportParking@gmail.com',
            ['billyboy2410@gmail.com'],
            fail_silently=False,
        )
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
    return render(request, "payment-form.html")


def edit(request):
    if request.method == 'POST':
        form = CustomerChangeFormCustomer(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomerChangeFormCustomer(instance=request.user)
    return render(request, 'ParkEasy/edit_form_customer.html', {'form': form})


def edit_booking(request, id):
    if request.method == 'POST':
        form = BookingCreationFormCustomer(instance=Booking.objects.get(id=id))
        if form.is_valid():
            form.save()
            query_results = Booking.objects.filter(customer=request.user)
            context = {"query_results": query_results}
            return render(request, 'view-bookings.html', context)
        else:
            form = BookingCreationFormCustomer()
            obj = Booking.objects.get(id=id)
            context = obj.booking_length
            return render(request, 'ParkEasy/edit_form.html', {'form': form}, context)
    else:
        #form = BookingCreationFormCustomer(instance=Booking.objects.get(id=id))
        query_results = Booking.objects.filter(customer=request.user)
        context = {"query_results": query_results}
        return render(request, 'view-bookings.html', context)


def view_bookings(request):
    query_results = Booking.objects.filter(customer=request.user)
    context = {"query_results": query_results}
    return render(request, 'view-bookings.html', context)


def delete_booking(request, id):
    booking = Booking.objects.get(id=id)
    booking.delete()
    query_results = Booking.objects.filter(customer=request.user)
    context = {"query_results": query_results}
    return render(request, 'view-bookings.html', context)


def delete_account(request):
    cust = request.user
    cust.delete()
    logout(request)
    return render(request, 'home.html')
