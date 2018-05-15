from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Customer, Booking, Departing, Arriving, Payment, Prices
import datetime


class CustomerCreationFormUser(UserCreationForm):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
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


class CustomerChangeFormAdmin(UserChangeForm):
    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')


class BookingCreationFormAdmin(forms.ModelForm):

    booking_date = forms.DateTimeField(label="Date Booked", widget=forms.DateInput)

    class Meta:
        model = Customer
        fields = ('email',)


class BookingChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


class DepartingCreationFormAdmin(forms.ModelForm):

    departing_flight_datetime = forms.DateTimeField(label="Departure Date", widget=forms.DateInput)
    departing_flight_number = forms.TextInput()
    destination = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


class DepartingChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Departing
        fields = '__all__'


class ArrivingCreationFormAdmin(forms.ModelForm):

    arriving_flight_datetime = forms.DateTimeField(label="Departure Date", widget=forms.DateInput)
    arriving_flight_number = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


class ArrivingChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Arriving
        fields = '__all__'


class PaymentCreationFormAdmin(forms.ModelForm):

    date_paid = forms.DateTimeField(label="Date of Payment", widget=forms.DateInput)
    card_type = forms.TextInput()
    card_number = forms.TextInput()
    amount = forms.IntegerField()
    expiry_date = forms.DateTimeField(label="Card Expiry Date", widget=forms.DateInput)
    security_number = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


class PaymentChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'


class PriceCreationFormAdmin(forms.ModelForm):

    vip = forms.IntegerField()
    valet = forms.IntegerField()
    day = forms.FloatField()
    base = forms.IntegerField()
    after_five = forms.IntegerField()

    class Meta:
        model = Prices
        fields = ('id',)


class PriceChangeFormAdmin(forms.ModelForm):
    class Meta:
        model = Prices
        fields = '__all__'


class CustomerChangeFormCustomer(UserChangeForm):
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'address_line1', 'address_line2', 'postcode', 'tel_no')
        exclude = {'email', 'password1', 'password', 'password2'}

    def save(self, commit=True):
        customer = super(CustomerChangeFormCustomer, self).save(commit=False)
        if commit:
            customer.save()
        return customer


class BookingCreationFormCustomer(forms.ModelForm):
    Start = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())
    End = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())

    class Meta:
        model = Booking
        fields = ('Start', 'End')


class BaseForm(forms.Form):
    Start = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())
    End = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today())


class BookingViewForm(forms.ModelForm):
    booking_end = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Booking
        fields = ('booking_date', 'booking_end')
