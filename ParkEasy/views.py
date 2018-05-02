from django.views.generic import ListView
from .models import Customer, Booking
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import BookingCreationFormCustomer, CustomerCreationFormUser, CustomerChangeFormCustomer
from William_Rodgers_Graded_Unit import settings
from django.template import RequestContext
import stripe
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
        if form.is_valid():
            if request.user.is_authenticated:
                start = form.cleaned_data.get('Start')
                end = form.cleaned_data.get('End')
                length = end - start
                length = length.days
                cust = Customer.objects.get(email=request.user.email)
                newbooking1 = Booking(customer=cust, booking_date=start, booking_length=length)
                request.session['booking'] = newbooking1
                days = length
                request.session['days'] = days
                amount = 0
                if days == 1:
                    amount = amount + 27
                elif days == 2:
                    amount = amount + 39
                elif days == 3:
                    amount = amount + 44
                elif days == 4:
                    amount = amount + 50
                elif days == 5:
                    amount = amount + 55
                elif days > 5:
                    amount = amount + 55
                    while days > 0:
                        amount = amount + 10
                        days = days - 1
                request.session['num_amount'] = amount
                amount = str(amount) + "00"
                request.session['amount'] = amount
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


#amount = 0


def payment_form(request):
    context = {"stripe_key": settings.STRIPE_PUBLIC_KEY}
    return render(request, "payment-form.html")


def edit(request):
    if request.method == 'POST':
        form = CustomerChangeFormCustomer(request.POST)
        if form.is_valid():
            cust = Customer.objects.get(email=request.user.email, first_name=request.user.first_name,
                                        last_name=request.user.last_name, address_line1=request.user.address_line1,
                                        address_line2=request.user.address_line2, postcode=request.user.postcode,
                                        tel_no=request.user.tel_no)
            return redirect('home')
    else:
        form = CustomerChangeFormCustomer()
    return render(request, 'registration/signup.html', {'form': form})
