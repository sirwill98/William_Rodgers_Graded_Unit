from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Customer, Booking, Departing, Arriving, Payment


class CustomerCreationForm(UserCreationForm):
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


class CustomerChangeForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')


class BookingCreationForm(forms.ModelForm):

    booking_date = forms.DateTimeField(label="Date Booked", widget=forms.DateInput)

    class Meta:
        model = Customer
        fields = ('email',)


class BookingChangeForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


class DepartingCreationForm(forms.ModelForm):

    departing_flight_datetime = forms.DateTimeField(label="Departure Date", widget=forms.DateInput)
    departing_flight_number = forms.TextInput()
    destination = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


class DepartingChangeForm(forms.ModelForm):
    class Meta:
        model = Departing
        fields = '__all__'


class ArrivingCreationForm(forms.ModelForm):

    arriving_flight_datetime = forms.DateTimeField(label="Departure Date", widget=forms.DateInput)
    arriving_flight_number = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


class ArrivingChangeForm(forms.ModelForm):
    class Meta:
        model = Arriving
        fields = '__all__'


class PaymentCreationForm(forms.ModelForm):

    date_paid = forms.DateTimeField(label="Date of Payment", widget=forms.DateInput)
    card_type = forms.TextInput()
    card_number = forms.TextInput()
    amount = forms.IntegerField()
    expiry_date = forms.DateTimeField(label="Card Expiry Date", widget=forms.DateInput)
    security_number = forms.TextInput()

    class Meta:
        model = Customer
        fields = ('email',)


class PaymentChangeForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'

