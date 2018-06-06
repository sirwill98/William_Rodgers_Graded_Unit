from django.views.generic import ListView
import xlwt
from .models import Customer, Booking, Prices, Vehicle, Departing, Arriving, Payment
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import BookingCreationFormCustomer, CustomerCreationFormUser, CustomerChangeFormCustomer, \
    BookingEditFormCustomer, VehicleCreationFormCustomer, ArrivingCreationFormCustomer, DepartingCreationFormCustomer, \
    ReportCreationForm, DateTriggerStaff
from William_Rodgers_Graded_Unit import settings
from datetime import timedelta, datetime
from django.utils import timezone
import stripe
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
stripe.api_key = settings.STRIPE_SECRET_KEY


# this view initialises the home page for the user
def home_page_view(request):
    storage = messages.get_messages(request)
    storage.used = True
    # returns the request along with the html for the home page
    return render(request, 'home.html')


# this is a function that is only run to clear the database for any changes to the models that requires new objects or
# attributes
def delete_all():
    # these lines delete all entries of the objects in the database
    Booking.objects.all().delete()
    Arriving.objects.all().delete()
    Departing.objects.all().delete()
    Vehicle.objects.all().delete()
    Payment.objects.all().delete()
    return True


# this view initialises the home page for the Staff
def staff_home_page_view(request):
    # returns the request along with the html for the Staff home page
    return render(request, 'Staff/Home.html')


# this view is used to allow users to change their password and stay logged in
def change_password(request):
    # this line is used to check if the data was securely posted to the server
    if request.method == 'POST':
        # sets the form to the password form and uses the posted request as a parameter
        form = PasswordChangeForm(request.user, request.POST)
        # this line checks if the form is valid using djangos inbuilt validation
        if form.is_valid():
            # sets the user to the form data
            user = form.save()
            # updates the hashed password in the session to the new password
            update_session_auth_hash(request, user)
            # sends a success message to the user
            messages.success(request, 'Your password was successfully updated!')
            # send the user to the password page again but with the success message this time
            return render(request, 'registration/change_password.html', {
                'form': form
            })
        else:
            # sends the user an error message if the password is invalid
            messages.error(request, 'Please correct the error below.')
    else:
        # set the form to the default if there was no post, this is used for when the for is first opened
        form = PasswordChangeForm(request.user)
    #return the password page to the user
    return render(request, 'registration/change_password.html', {
        'form': form
    })


# this view is used to initialise the booking view before any data is entered
class BookingView(ListView):
    #sets the model of the view to the booking model
    model = Booking
    #set the template to the booking html page
    template_name = 'booking.html'


# this view is used to allow the user to create a vehicle and then send the user to the payment page
def vehicle_form(request):
    # check if the request data was posted
    if request.POST:
        # set the form to the customer vehicle cration form
        form = VehicleCreationFormCustomer(request.POST)
        #check if the form data is valid
        if form.is_valid():
            # check if the user is authenticated before allowing them to create vehicle
            if request.user.is_authenticated:
                # get vehicle data from form
                reg_no = form.cleaned_data.get('reg_no')
                make = form.cleaned_data.get('make')
                manufacturer = form.cleaned_data.get('manufacturer')
                # get logged in customer
                cust = Customer.objects.get(email=request.user.email)
                # create vehicle from data in form
                vehicle = Vehicle(reg_no=reg_no, make=make, manufacturer=manufacturer)
                # get current prices
                price = Prices.objects.get(is_current=True)
                # create a new booking using data from previous forms and from this
                newbooking1 = Booking(customer=cust, booking_date=request.session['booking_date'],
                                      booking_length=request.session['booking_length'], prices=price, vehicle=vehicle,
                                      vip=request.session['vip'], valet=request.session['valet'],
                                      departing=request.session['departing'], arriving=request.session['arriving'])
                newbooking1.assigned_space = Booking.space_check(newbooking1)
                # add the vehicle and booking to the session so it can be saved later
                request.session['vehicle'] = vehicle
                request.session['booking'] = newbooking1
                # calculate the amount to be paid for the payment phase
                amount = Booking.calc_amount(newbooking1, request.session['booking_length'])
                # add the amount to the session
                request.session['num_amount'] = amount
                # add a string amount to the session for stripe to display
                request.session['amount'] = str(amount) + "00"
                #send user to the payment form
                return render(request, 'payment-form.html', {'form': form})
            else:
                # if the user is not logged in then they are sent to the login page
                return render(request, 'registration/login.html', {'form': form})
        else:
            # if the form was not valid the form is returned
            return render(request, 'vehicle.html', {'form': form})
    else:
        # if the form was not posted then set the form to an empty instance
        form = VehicleCreationFormCustomer()
    # return the page to the user
    return render(request, 'vehicle.html', {'form': form})


# this view is used for selecting the departing flight
def departing_form(request):
    # check if the data was posted to the form
    if request.POST:
        # set the form to the customer departing form with the post data
        form = DepartingCreationFormCustomer(request.POST)
        # check if the data in the form is valid
        if form.is_valid():
            #check if the ser is logged in
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
                # add departing object to the session
                request.session['departing'] = departing
                # send user to the arriving flights page
                return redirect("arriving")
            else:
                # send the user to the login page if they are not logged in
                return render(request, 'registration/login.html', {'form': form})
        else:
            # send the user to the page again if the form was invalid 
            return render(request, 'departing.html', {'form': form})
    else:
        # if the form was not posted then set the form to an empty instance
        form = DepartingCreationFormCustomer()
    # return the page to the user
    return render(request, 'departing.html', {'form': form})


def arriving_form(request):
    # check if the form was posted
    if request.POST:
        # set the form to the customer arriving form with the post data
        form = ArrivingCreationFormCustomer(request.POST)
        # check if the form data is valid
        if form.is_valid():
            # check if the user us logged in
            if request.user.is_authenticated:
                # get vehicle data from form
                arriving_flight_number = form.cleaned_data.get('arriving_flight_number')
                arriving_flight_datetime = form.cleaned_data.get('arriving_flight_datetime')
                # get logged in customer
                cust = Customer.objects.get(email=request.user.email)
                # create arriving flight object
                arriving = Arriving(arriving_flight_number=arriving_flight_number,
                                    arriving_flight_datetime=arriving_flight_datetime, customer=cust)
                # add the arriving flight to the session
                request.session['arriving'] = arriving
                # send the user to the vehicle page
                return redirect("vehicle")
            else:
                # if the user is not logged in send them to the login page
                return render(request, 'registration/login.html', {'form': form})
        else:
            # send the user to the arriving page
            return render(request, 'arriving.html', {'form': form})
    else:
        # set the form to the arriing flight form
        form = ArrivingCreationFormCustomer()
    # send the user to the arriving page
    return render(request, 'arriving.html', {'form': form})


def booking_form(request):
    # check if the form data was posted
    if request.POST:
        # set the form to the customer booking form with the post data
        form = BookingCreationFormCustomer(request.POST)
        # check if the form data is valid
        if form.is_valid():
            # check if the user is logged in
            if request.user.is_authenticated:
                # get the data from the form
                start = form.cleaned_data.get('Start')
                end = form.cleaned_data.get('End')
                vip = form.cleaned_data.get('Vip')
                valet = form.cleaned_data.get('Valet')
                # calculate the length of booking then check that it is more than 0 days
                length = end - start
                length = length.days
                if length <= 0:
                    messages.add_message(request, messages.INFO, 'Bookings must be more than 0 days')
                    return render(request, 'booking.html', {'form': form})
                # add the form variables to the session
                request.session['booking_date'] = start
                request.session['booking_length'] = length
                request.session['vip'] = vip
                request.session['valet'] = valet
                days = length
                request.session['days'] = days
                # send the user to the departing page
                return redirect("departing")
            else:
                # if the user is not logged in send them to the login page
                return render(request, 'registration/login.html', {'form': form})
        else:
            # send the user to the booking page
            return render(request, 'booking.html', {'form': form})
    else:
        # set the form the the customer booking form
        form = BookingCreationFormCustomer()
    # send the user to the booking page
    return render(request, 'booking.html', {'form': form})

# clear session variables???


def checkout(request):
    # get required variables out of the session
    new_booking = request.session['booking']
    vehicle = request.session['vehicle']
    arriving = request.session['arriving']
    departing = request.session['departing']
    # check of the data was posted
    if request.method == "POST":
        # get the stripe token from the request
        token = request.POST.get("stripeToken")

    try:
        # create a new charge that strip will display to the user
        charge = stripe.Charge.create(
            # set the amount to the amount string created in the booking view
            amount=request.session['amount'],
            currency="gbp",
            # set the source to the stripe token
            source=token,
            description="The product charged to the user"
        )
        # set charge id to charge id
        new_booking.charge_id = charge.id
    # return an error for invalid dard
    except stripe.error.CardError as ce:
        return False, ce

    else:
        #save the bookings now that the payment has went through
        departing.save()
        arriving.save()
        vehicle.save()
        new_booking.vehicle = vehicle
        new_booking.arriving = arriving
        new_booking.departing = departing
        new_booking.date_booked = timezone.now()
        new_booking.space_check()
        new_booking.save()
        payment = Payment(
            booking=new_booking,
            date_paid=timezone.now(),
            paid=True,
            amount=request.session['num_amount']
        )
        payment.save()
        # send a verification email to the users email address
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
        # send user back to home page
        return redirect("home")


def signup(request):
    # check if the data was posted
    if request.method == 'POST':
        # set the form to the customer creation form with the posted data
        form = CustomerCreationFormUser(request.POST)
        # check the form is valid
        if form.is_valid():
            # save the form
            form.save()
            # set the email to the cleaned data email
            email = form.cleaned_data.get('email')
            # set the password to the form password
            raw_password = form.cleaned_data.get('password1')
            # set the user to the email and password
            user = authenticate(email=email, password=raw_password)
            # log the user in now they have registered
            login(request, user)
            # send the user to the home page
            return redirect('home')
    else:
        # set the form to the customer creation form
        form = CustomerCreationFormUser()
    # send the user to the registration page
    return render(request, 'registration/signup.html', {'form': form})


def payment_form(request):
    # set the context to the settings public key
    context = {"stripe_key": settings.STRIPE_PUBLIC_KEY}
    # send the user to the payment form
    return render(request, "payment-form.html")


def edit(request):
    # check if the data was posted
    if request.method == 'POST':
        # set the form to the customer change form and sent the 
        form = CustomerChangeFormCustomer(request.POST, instance=request.user)
        # check if the form is valid
        if form.is_valid():
            # save the form
            form.save()
            # send the user to the home page
            return redirect('home')
    else:
        # set the form to the customer change form
        form = CustomerChangeFormCustomer(instance=request.user)
    # send the user to the edit customer page
    return render(request, 'ParkEasy/edit_form_customer.html', {'form': form})


def edit_booking(request, id):
    # check if the data was posted
    if request.method == 'POST':
        # set the booking to the booking sent by the url
        book = Booking.objects.get(id=id)
        # set the form to the booking edit form
        form = BookingEditFormCustomer(request.POST, book.booking_length, book.booking_date)
        # check if the form is valid
        if form.is_valid():
            # save the form
            form.save()
            # create a query  that will contain all of the bookings the customer has made
            query_results = Booking.objects.filter(customer=request.user)
            # add it to a dictionary
            context = {"query_results": query_results}
            # return the view bookings page with the dictionary
            return render(request, 'view-bookings.html', context)
    else:
        # set the form to the booking edit form
        form = BookingEditFormCustomer()
    # send the user to the edit form
    return render(request, 'ParkEasy/edit_form.html', {'form': form})


def view_bookings(request):
    # create a query  that will contain all of the bookings the customer has made
    query_results = Booking.objects.filter(customer=request.user)
    # add it to a dictionary called context
    context = {"query_results": query_results}
    # send the user to the view bookings page
    return render(request, 'view-bookings.html', context)


def check_in_page(request):
    # create a query list of all of the bookings
    query_results = Booking.objects.all
    # add the query toa disctionary called context
    context = {"query_results": query_results}
    # send the user to the check in page
    return render(request, 'Staff/Check_In.html', context)


def check_in(request, id):
    # set the booking to the id passed in
    booking = Booking.objects.get(id=id)
    # set the booking checked in to true
    booking.checked_in = True
    # save the booking
    booking.save()
    # add a success message to the page
    messages.add_message(request, messages.INFO, 'Booking successfully checked in')
    # create a query list of all of the bookings
    query_results = Booking.objects.all
    # add the query to the variable context
    context = {"query_results": query_results}
    # send the user to the check in page
    return render(request, 'Staff/Check_In.html', context)


def check_out(request, id):
    # set the booking to the id passed in
    booking = Booking.objects.get(id=id)
    # set booking check ed out to true
    booking.checked_out = True
    booking.assigned_space = False
    # save the booking
    booking.save()
    # assign new space
    booking.check_out()
    # add a success message to the page
    messages.add_message(request, messages.INFO, 'Booking successfully checked out')
    # create a query list of all of the bookings
    query_results = Booking.objects.all
    # add the query to the variable context
    context = {"query_results": query_results}
    # send the user to the check in page
    return render(request, 'Staff/Check_In.html', context)


def delete_booking(request, id):
    # get the booking from the id passed in
    booking = Booking.objects.get(id=id)
    # delete the booking
    booking.delete()
    # create a queryset of all the bookings a customer has made
    query_results = Booking.objects.filter(customer=request.user)
    # add the query to the context dict
    context = {"query_results": query_results}
    # add a success message to the page
    messages.add_message(request, messages.INFO, 'Booking successfully deleted')
    # send user to the view bookings page
    return render(request, 'view-bookings.html', context)


def delete_account(request):
    # set the customer to the customer that sent the request
    cust = request.user
    # delete the customer
    cust.delete()
    # log the customer out
    logout(request)
    # add a success message
    messages.add_message(request, messages.INFO, 'Customer successfully deleted')
    # send user to home page
    return render(request, 'home.html')


def report_init(request):
    # check if the request method is post
    if request.method == 'POST':
        # check if the request has booking report in it 
        if request.POST.get("booking_report"):
            # send the user to the add dates page
            return redirect("add-dates")
        # check if request has occupancy report in it
        elif request.POST.get("occupancy_report"):
            # add occupancy entry to session, value dosent matter, all we need it it to exist
            request.session['occupancy'] = "foo"
            # send user to add dates page
            return redirect("add-dates")
        # check if weeks bookings is in request
        elif request.POST.get("weeks_bookings"):
            # set start session variable to today
            request.session['start'] = datetime.today()
            # run generate reports function
            generate_reports(request)
            # send user to home page
            return redirect("staff-home")
    else:
        # send user to reports page
        return render(request, 'Staff/Reports.html')
    #send user to reports page
    return render(request, 'Staff/Reports.html')


def add_dates(request):
    # check if reequest data was posted
    if request.POST:
        # set form to report form
        form = ReportCreationForm(request.POST)
        # check if form is valid
        if form.is_valid():
            # get data from form
            start = form.cleaned_data.get('Start')
            end = form.cleaned_data.get('End')
            length = end - start
            length = length.days
            if length <= 0:
                messages.add_message(request, messages.INFO, 'Reports must be more than 0 days')
                return render(request, 'Staff/Report_Dates.html', {'form': form})
            # add the form variables to the session
            # add data to session
            request.session['start'] = start
            request.session['end'] = end
            # run generate reports method
            generate_reports(request)
            #send user to home
            return redirect("staff-home")
    else:
        # set form to report form
        form = ReportCreationForm()
    #send user to reports date form
    return render(request, 'Staff/Report_Dates.html', {'form': form})


def generate_reports(request):
    # check if start was in session
    if 'start' in request.session:
        # check if end was in session
        if 'end' in request.session:
            # set start to start session variable
            start = request.session['start']
            # set end to end to session variable
            end = request.session['end']
            # create queryset for specific bookings
            booking_set = Booking.objects.filter(date_created__gte=start, date_created__lte=end)
            # create new workbook
            wb = xlwt.Workbook()
            # create new worksheet
            ws = wb.add_sheet('bookings ' + str(start) + 'to' + str(end))
            i = 1
            # write headings to table
            ws.write(0, 0, 'booking')
            ws.write(0, 1, 'customer')
            ws.write(0, 2, 'vehicle')
            ws.write(0, 3, 'date')
            ws.write(0, 4, 'length')
            ws.write(0, 5, 'date created')
            ws.write(0, 6, 'total')
            #loop through bookings in queryset
            for i, booking in enumerate(booking_set):
                # write all values to correct colums
                ws.write(i+1, 0, str(booking.id))
                ws.write(i+1, 1, str(booking.customer))
                ws.write(i+1, 2, str(booking.vehicle))
                ws.write(i+1, 3, str(booking.booking_date))
                ws.write(i+1, 4, str(booking.booking_length))
                ws.write(i+1, 5, str(booking.date_created))
                ws.write(i+1, 6, str(booking.calc_amount(booking.booking_length)))
            # save the workbook
            wb.save('C:/Users/Billy/Documents/django_reports/' + 'Bookings from ' + str(start) + 'to'
                    + str(end) + '.xls')
            # delete session variables
            del request.session['start']
            del request.session['end']
            # return
            return
        # check if end and occupancy are in session
        elif 'end' in request.session and 'occupancy' in request.session:
            # set start to start session variable
            start = request.session['start']
            # set end to end variable
            end = request.session['end']
            # create booking set
            booking_set = Booking.objects.filter(date_created__gte=start, date_created__lte=end)
            # create new workbook
            wb = xlwt.Workbook()
            # create new worksheet
            ws = wb.add_sheet('occupancy from ' + str(start) + 'to' + str(end))
            # add headingt to first row
            ws.write(0, 0, 'booking id')
            ws.write(0, 1, 'customer')
            ws.write(0, 2, 'date')
            ws.write(0, 3, 'length')
            ws.write(0, 4, 'date created')
            test = 0
            # loop through all bookings in queryset
            for i, booking in enumerate(booking_set):
                # write all values to colums
                ws.write(i+1, 0, str(booking.id))
                ws.write(i+1, 1, str(booking.customer))
                ws.write(i+1, 3, str(booking.booking_date))
                ws.write(i+1, 4, str(booking.booking_length))
                ws.write(i+1, 5, str(booking.date_created))
                test = i
            # write total number of bookings to report
            ws.write(test+2, 0, str(booking_set.count()))
            # save form
            wb.save('C:/Users/Billy/Documents/django_reports/' + 'occupancy ' + str(start) + 'to'
                    + str(end) + '.xls')
            #delete sesion variables
            del request.session['start']
            del request.session['end']
            del request.session['occupancy']
            return
        else:
            # set today variable to today value
            today = datetime.today()
            # set weekday to the current weekday
            weekday = today.weekday()#
            # set start delta to a timedelta of 1 week
            start_delta = timedelta(days=weekday, weeks=1)
            # set start of week to last week
            start_of_week = request.session['start'] - start_delta
            # set end of week to end of last week
            end_of_week = start_of_week + timedelta(days=6)
            # create queryset of bookings
            booking_set = Booking.objects.filter(date_created__gte=start_of_week.date(), date_created__lte=end_of_week.date())
            # define the excel document
            wb = xlwt.Workbook()
            ws = wb.add_sheet('Bookings for week ' + str(start_of_week.date()))
            # add headings to colums
            ws.write(0, 0, 'booking id')
            ws.write(0, 1, 'customer')
            ws.write(0, 2, 'vehicle')
            ws.write(0, 3, 'date')
            ws.write(0, 4, 'length')
            ws.write(0, 5, 'date created')
            ws.write(0, 6, 'total')
            #loop through all bookings in set
            for i, booking in enumerate(booking_set):
                # write all data
                ws.write(i+1, 0, str(booking.id))
                ws.write(i+1, 1, str(booking.customer))
                ws.write(i+1, 2, str(booking.vehicle))
                ws.write(i+1, 3, str(booking.booking_date))
                ws.write(i+1, 4, str(booking.booking_length))
                ws.write(i+1, 5, str(booking.date_created))
                ws.write(i+1, 6, str(booking.calc_amount(booking.booking_length)))
            # save workbook
            wb.save\
                ('C:/Users/Billy/Documents/django_reports/' + 'Bookings for week ' + str(start_of_week.date()) + '.xls')
            del request.session['start']
            return


def day_input(request):
    # check if data was posted to view
    if request.method == 'POST':
        # set form to date trigger staff form
        form = DateTriggerStaff(request.POST)
        # check if form is valid
        if form.is_valid():
            # check if departures is in post
            if '_Departures' in request.POST:
                # get day value from form
                date = form.cleaned_data.get('Day')
                # create queryset of booking objects set to leave on selected day
                query_results = Booking.objects.filter(booking_date=date, checked_in=False)
                # add query to context
                context = {"query_results": query_results}
                # send user to departures page
                return render(request, 'Staff/Departures.html', context)
            # check if landings is in post
            elif '_Landings' in request.POST:
                # get day value from form
                date = form.cleaned_data.get('Day')
                # create queryset of booking objects set to land on selected day
                query_results = Booking.objects.filter(arriving__arriving_flight_datetime=date, checked_out=False)
                # add query to context
                context = {"query_results": query_results}
                # send user to landings page
                return render(request, 'Staff/Landings.html', context)
    else:
        # set form to datetriggerstaff
        form = DateTriggerStaff()
    #  send user to day input page
    return render(request, 'Staff/Day_Input.html', {'form': form})


def assigned_bookings(request):
    # create queryset of booking objects set to land on selected day
    query_results = Booking.objects.filter(assigned_space=False)
    # add query to context
    context = {"query_results": query_results}
    # send user to landings page
    return render(request, 'Staff/Spaces.html', context)
