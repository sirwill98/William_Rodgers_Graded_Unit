from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Customer, Booking, Departing, Arriving, Payment, Prices, Vehicle
import datetime

# this is the user creation form that inherits from the base one and allows users to create an account
class CustomerCreationFormUser(UserCreationForm):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'telephont_invalid': "The Phone Number was invalid"
    }
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput,
                                help_text="Enter the same password as above, for verification.")

    class Meta:
        model = Customer
        fields = ('email', 'password1', 'password2',
                  'first_name', 'last_name', 'postcode', 'address_line1', 'address_line2', 'tel_no')

    def save(self, commit=True):
        customer = super(UserCreationForm, self).save(commit=False)
        customer.set_password(self.cleaned_data["password1"])
        if commit:
            customer.save()
        return customer


# this is the user creation form that inherits from the base one and allows admins to create user accounts
class CustomerCreationFormAdmin(UserCreationForm):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput,
                                help_text="Enter the same password as above, for verification.")

    class Meta:
        model = Customer
        fields = ('email',)

    def save(self, commit=True):
        customer = super(UserCreationForm, self).save(commit=False)
        customer.set_password(self.cleaned_data["password1"])
        if commit:
            customer.save()
        return customer


# this is the form for changing/editing the customers as an admin
class CustomerChangeFormAdmin(UserChangeForm):
    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')


# this is the form for creating bookings as an admin for testing purposes
class BookingCreationFormAdmin(forms.ModelForm):

    booking_date = forms.DateTimeField(label="Date Booked", widget=forms.DateInput)

    class Meta:
        model = Customer
        fields = ('email',)


# this is the form for editing bookings as an admin
class BookingChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


# this is the form for creating vehicles as an admin
class VehicleCreationFormAdmin(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ('id',)


# this is the form for editing vehicles as an admin
class VehicleChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'


# this is the form for creating departing flights as an admin
class DepartingCreationFormAdmin(forms.ModelForm):

    departing_flight_datetime = forms.DateTimeField(label="Departure Date", widget=forms.DateTimeInput)
    departing_flight_number = forms.TextInput()
    destination = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


# this is the form for editing departing flights as an admin
class DepartingChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Departing
        fields = '__all__'


# this is the form for creating arriving flights as an admin
class ArrivingCreationFormAdmin(forms.ModelForm):

    arriving_flight_datetime = forms.DateTimeField(label="Departure Date", widget=forms.DateTimeInput)
    arriving_flight_number = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


# this is the form for editing arriving flights as an admin
class ArrivingChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Arriving
        fields = '__all__'


# this is the form for creating price schemas as an admin
class PriceCreationFormAdmin(forms.ModelForm):

    vip = forms.IntegerField()
    valet = forms.IntegerField()
    day = forms.FloatField()
    base = forms.IntegerField()
    after_five = forms.IntegerField()

    class Meta:
        model = Prices
        fields = ('id',)


# this is the form for editing prices as an admin
class PriceChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Prices
        fields = '__all__'


# this is the form for editing customer details as that customer
class CustomerChangeFormCustomer(UserChangeForm):
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'address_line1', 'address_line2', 'postcode', 'tel_no', 'password')
        exclude = {'email', 'password1', 'password2'}

    def save(self, commit=True):
        customer = super(CustomerChangeFormCustomer, self).save(commit=False)
        if commit:
            customer.save()
        return customer


# this is the form for creating bookings as a customer
class BookingCreationFormCustomer(forms.ModelForm):
    Start = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())
    End = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())
    Vip = forms.BooleanField(initial=False, required=False)
    Valet = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = Booking
        fields = ('Start', 'End', 'Vip', 'Valet')


# this is the form for creating vehicles as a customer
class VehicleCreationFormCustomer(forms.ModelForm):
    reg_no = forms.TextInput()
    make = forms.TextInput()
    manufacturer = forms.TextInput()

    class Meta:
        model = Vehicle
        fields = ('reg_no', 'make', 'manufacturer')


# this is the form for viewing bookings as a customer
class BookingViewForm(forms.ModelForm):
    booking_end = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Booking
        fields = ('booking_date', 'booking_end')


# this is the form for editing bookings as a customer
class BookingEditFormCustomer(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ('booking_date', 'booking_length', 'vip', 'valet')

    # this is ths initialising function for the form
    def __init__(self, booking_date, booking_length, *args, **kwargs):
        super(BookingEditFormCustomer, self).__init__(*args, **kwargs)

        # set the user_id as an attribute of the form
        self.booking_date = booking_date
        self.booking_length = booking_length

    # this is the function for allowing access to the booking date data
    def clean_booking_date(self):
        bk_date = self.cleaned_data.get("booking_date")

        if bk_date < datetime.date.today():
            raise forms.ValidationError("The date cannot be in the past!")
        return bk_date


# this is the form for creating bookings as a customer
class DepartingCreationFormCustomer(forms.ModelForm):
    departing_flight_number = forms.TextInput()
    departing_flight_datetime = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())
    destination = forms.TextInput()

    class Meta:
        model = Departing
        fields = ('departing_flight_number', 'departing_flight_datetime', 'destination')


# this form is used to allow customers to create arriving flights
class ArrivingCreationFormCustomer(forms.ModelForm):
    arriving_flight_number = forms.TextInput()
    arriving_flight_datetime = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())

    class Meta:
        model = Arriving
        fields = ('arriving_flight_number', 'arriving_flight_datetime')


# this is the form for staff to create reports
class ReportCreationForm(forms.ModelForm):
    Start = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())
    End = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())

    class Meta:
        model = Booking
        fields = ('Start', 'End')


# this form is used to get dates to see bookings due on certain days
class DateTriggerStaff(forms.ModelForm):
    Day = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())

    class Meta:
        model = Booking
        fields = 'Day',
