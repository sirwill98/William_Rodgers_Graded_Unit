from django.views.generic import ListView
import xlwt
from .models import Customer, Booking, Prices, Vehicle, Departing, Arriving, Payment
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import BookingCreationFormCustomer, CustomerCreationFormUser, CustomerChangeFormCustomer, \
    BookingEditFormCustomer, VehicleCreationFormCustomer, ArrivingCreationFormCustomer, DepartingCreationFormCustomer, \
    ReportCreationForm
from William_Rodgers_Graded_Unit import settings
from datetime import timedelta, datetime
from django.utils import timezone
import stripe
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
stripe.api_key = settings.STRIPE_SECRET_KEY


def home_page_view(request):
    return render(request, 'home.html')


def delete_all():
    Booking.objects.all().delete()
    Arriving.objects.all().delete()
    Departing.objects.all().delete()
    Vehicle.objects.all().delete()
    Payment.objects.all().delete()
    return True


def staff_home_page_view(request):
    return render(request, 'Staff/Home.html')


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


def vehicle_form(request):
    if request.POST:
        form = VehicleCreationFormCustomer(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                # get vehicle data from form
                reg_no = form.cleaned_data.get('reg_no')
                make = form.cleaned_data.get('make')
                manufacturer = form.cleaned_data.get('manufacturer')
                # get logged in customer
                cust = Customer.objects.get(email=request.user.email)
                # get current prices
                vehicle = Vehicle(reg_no=reg_no, make=make, manufacturer=manufacturer)
                price = Prices.objects.get(is_current=True)
                newbooking1 = Booking(customer=cust, booking_date=request.session['booking_date'],
                                      booking_length=request.session['booking_length'], prices=price, vehicle=vehicle,
                                      vip=request.session['vip'], valet=request.session['valet'],
                                      departing=request.session['departing'], arriving=request.session['arriving'])
                request.session['vehicle'] = vehicle
                request.session['booking'] = newbooking1
                amount = Booking.calc_amount(newbooking1, request.session['booking_length'])
                request.session['num_amount'] = amount
                request.session['amount'] = str(amount) + "00"
                return render(request, 'payment-form.html', {'form': form})
            else:
                return render(request, 'registration/login.html', {'form': form})
        else:
            return render(request, 'vehicle.html', {'form': form})
    else:
        form = VehicleCreationFormCustomer()
    return render(request, 'vehicle.html', {'form': form})


def departing_form(request):
    if request.POST:
        form = DepartingCreationFormCustomer(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                # get vehicle data from form
                departing_flight_number = form.cleaned_data.get('departing_flight_number')
                departing_flight_datetime = form.cleaned_data.get('departing_flight_datetime')
                destination = form.cleaned_data.get('destination')
                # get logged in customer
                cust = Customer.objects.get(email=request.user.email)
                # create departing flight object
                departing = Departing(departing_flight_number=departing_flight_number,  
                                      departing_flight_datetime=departing_flight_datetime,
                                      destination=destination, customer=cust)
                request.session['departing'] = departing
                return redirect("arriving")
            else:
                return render(request, 'registration/login.html', {'form': form})
        else:
            return render(request, 'departing.html', {'form': form})
    else:
        form = DepartingCreationFormCustomer()
    return render(request, 'departing.html', {'form': form})


def arriving_form(request):
    if request.POST:
        form = ArrivingCreationFormCustomer(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                # get vehicle data from form
                arriving_flight_number = form.cleaned_data.get('arriving_flight_number')
                arriving_flight_datetime = form.cleaned_data.get('arriving_flight_datetime')
                # get logged in customer
                cust = Customer.objects.get(email=request.user.email)
                # create arriving flight object
                arriving = Arriving(arriving_flight_number=arriving_flight_number,
                                    arriving_flight_datetime=arriving_flight_datetime, customer=cust)
                request.session['arriving'] = arriving
         #       print(arriving.id)
          #      test = arriving.save()
           #     print(arriving.id)
                return redirect("vehicle")
            else:
                return render(request, 'registration/login.html', {'form': form})
        else:
            return render(request, 'arriving.html', {'form': form})
    else:
        form = ArrivingCreationFormCustomer()
    return render(request, 'arriving.html', {'form': form})


def booking_form(request):
    if request.POST:
        form = BookingCreationFormCustomer(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                start = form.cleaned_data.get('Start')
                end = form.cleaned_data.get('End')
                vip = form.cleaned_data.get('Vip')
                valet = form.cleaned_data.get('Valet')
                length = end - start
                length = length.days
                if length <= 0:
                    messages.add_message(request, messages.INFO, 'Bookings must be more than 0 days')
                    return render(request, 'booking.html', {'form': form})
                request.session['booking_date'] = start
                request.session['booking_length'] = length
                request.session['vip'] = vip
                request.session['valet'] = valet
                days = length
                request.session['days'] = days
                if Booking.objects.count() == 2000:
                    messages.add_message(request, messages.INFO, 'There are no spaces currently available')
                    return render(request, 'booking.html', {'form': form})
                form = VehicleCreationFormCustomer()
                return redirect("departing")
            else:
                return render(request, 'registration/login.html', {'form': form})
        else:
            return render(request, 'booking.html', {'form': form})
    else:
        form = BookingCreationFormCustomer()

    return render(request, 'booking.html', {'form': form})

# clear session variables???


def checkout(request):
    new_booking = request.session['booking']
    vehicle = request.session['vehicle']
    arriving = request.session['arriving']
    departing = request.session['departing']

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
        departing.save()
        arriving.save()
        vehicle.save()
        new_booking.vehicle = vehicle
        new_booking.arriving = arriving
        new_booking.departing = departing
        new_booking.date_booked = timezone.now()
        new_booking.save()
        payment = Payment(
            booking=new_booking,
            date_paid=timezone.now(),
            paid=True,
            amount=request.session['num_amount']
        )
        payment.save()

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
        book = Booking.objects.get(id=id)
        form = BookingEditFormCustomer(request.POST, book.booking_length, book.booking_date)
        if form.is_valid():
            form.save()
            query_results = Booking.objects.filter(customer=request.user)
            context = {"query_results": query_results}
            return render(request, 'view-bookings.html', context)
    else:
        form = BookingEditFormCustomer()
    return render(request, 'ParkEasy/edit_form.html', {'form': form})


def view_bookings(request):
    query_results = Booking.objects.filter(customer=request.user)
    context = {"query_results": query_results}
    return render(request, 'view-bookings.html', context)


def delete_booking(request, id):
    booking = Booking.objects.get(id=id)
    booking.delete()
    query_results = Booking.objects.filter(customer=request.user)
    context = {"query_results": query_results}
    messages.add_message(request, messages.INFO, 'Booking successfully deleted')
    return render(request, 'view-bookings.html', context)


def delete_account(request):
    cust = request.user
    cust.delete()
    logout(request)
    messages.add_message(request, messages.INFO, 'Customer successfully deleted')
    return render(request, 'home.html')


def report_init(request):
    if request.method == 'POST':
        if request.POST.get("booking_report"):
            return redirect("add-dates")
        elif request.POST.get("occupancy_report"):
            request.session['occupancy'] = "foo"
            return redirect("add-dates")
        elif request.POST.get("weeks_bookings"):
            request.session['start'] = datetime.today()
            generate_reports(request)
            return redirect("Home")
    else:
        return render(request, 'Staff/Reports.html')
    return render(request, 'Staff/Reports.html')


def add_dates(request):
    if request.POST:
        form = ReportCreationForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data.get('Start')
            end = form.cleaned_data.get('End')
            request.session['start'] = start
            request.session['end'] = end
            generate_reports(request)
            return redirect("home")
    else:
        form = ReportCreationForm()
    return render(request, 'Staff/Report_Dates.html', {'form': form})


def generate_reports(request):
    if 'start' in request.session:
        if 'end' in request.session:
            start = request.session['start']
            end = request.session['end']
            booking_set = Booking.objects.filter(date_created__gte=start, date_created__lte=end)
            wb = xlwt.Workbook()
            ws = wb.add_sheet('bookings ' + str(start) + 'to' + str(end))
            i = 1
            ws.write(0, 0, 'booking')
            ws.write(0, 1, 'customer')
            ws.write(0, 2, 'vehicle')
            ws.write(0, 3, 'date')
            ws.write(0, 4, 'length')
            ws.write(0, 5, 'date created')
            ws.write(0, 6, 'total')
            for i, booking in enumerate(booking_set):
                ws.write(i+1, 0, str(booking.id))
                ws.write(i+1, 1, str(booking.customer))
                ws.write(i+1, 2, str(booking.vehicle))
                ws.write(i+1, 3, str(booking.booking_date))
                ws.write(i+1, 4, str(booking.booking_length))
                ws.write(i+1, 5, str(booking.date_created))
                ws.write(i+1, 6, str(booking.calc_amount(booking.booking_length)))
            wb.save('C:/Users/Billy/Documents/django_reports/' + 'Bookings from ' + str(start) + 'to'
                    + str(end) + '.xls')
            del request.session['start']
            del request.session['end']
            return
        elif 'end' in request.session and 'occupancy' in request.session:
            start = request.session['start']
            end = request.session['end']
            booking_set = Booking.objects.filter(date_created__gte=start, date_created__lte=end)
            wb = xlwt.Workbook()
            ws = wb.add_sheet('occupancy from ' + str(start) + 'to' + str(end))
            ws.write(0, 0, 'booking id')
            ws.write(0, 1, 'customer')
            ws.write(0, 2, 'date')
            ws.write(0, 3, 'length')
            ws.write(0, 4, 'date created')
            test = 0
            for i, booking in enumerate(booking_set):
                ws.write(i+1, 0, str(booking.id))
                ws.write(i+1, 1, str(booking.customer))
                ws.write(i+1, 3, str(booking.booking_date))
                ws.write(i+1, 4, str(booking.booking_length))
                ws.write(i+1, 5, str(booking.date_created))
                test = i
            ws.write(test+2, 0, str(booking_set.count()))
            wb.save('C:/Users/Billy/Documents/django_reports/' + 'occupancy ' + str(start) + 'to'
                    + str(end) + '.xls')
            del request.session['start']
            del request.session['end']
            del request.session['occupancy']
            return
        else:
            today = datetime.today()
            weekday = today.weekday()
            start_delta = timedelta(days=weekday, weeks=1)
            start_of_week = request.session['start'] - start_delta
            end_of_week = start_of_week + timedelta(days=6)
            booking_set = Booking.objects.filter(date_created__gte=start_of_week.date(), date_created__lte=end_of_week.date())
            #define the excel document
            wb = xlwt.Workbook()
            ws = wb.add_sheet('Bookings for week ' + str(start_of_week.date()))
            ws.write(0, 0, 'booking id')
            ws.write(0, 1, 'customer')
            ws.write(0, 2, 'vehicle')
            ws.write(0, 3, 'date')
            ws.write(0, 4, 'length')
            ws.write(0, 5, 'date created')
            ws.write(0, 6, 'total')
            for i, booking in enumerate(booking_set):
                ws.write(i+1, 0, str(booking.id))
                ws.write(i+1, 1, str(booking.customer))
                ws.write(i+1, 2, str(booking.vehicle))
                ws.write(i+1, 3, str(booking.booking_date))
                ws.write(i+1, 4, str(booking.booking_length))
                ws.write(i+1, 5, str(booking.date_created))
                ws.write(i+1, 6, str(booking.calc_amount(booking.booking_length)))
            wb.save\
                ('C:/Users/Billy/Documents/django_reports/' + 'Bookings for week ' + str(start_of_week.date()) + '.xls')
            del request.session['start']
            return
