from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomerCreationFormAdmin, CustomerChangeFormAdmin, \
    BookingCreationFormAdmin, BookingChangeFormAdmin, \
    DepartingCreationFormAdmin, DepartingChangeFormAdmin, \
    ArrivingCreationFormAdmin, ArrivingChangeFormAdmin, \
    PaymentCreationFormAdmin, PaymentChangeFormAdmin
from .models import Customer, Booking, Departing, Arriving, Payment


class CustomerAdmin(UserAdmin):
    add_form = CustomerCreationFormAdmin
    form = CustomerChangeFormAdmin
    model = Customer
    list_display = ['id', 'email', 'address_line1', 'address_line2', 'postcode', 'tel_no']
    fieldsets = (
        (None,
            {'fields': ('email', 'password', 'date_joined')}),
        ('Personal info',
            {'fields': ('first_name', 'last_name', 'address_line1', 'address_line2', 'postcode', 'tel_no')}),
        ('Permissions',
            {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class BookingAdmin(ModelAdmin):
    add_form = BookingCreationFormAdmin
    form = BookingChangeFormAdmin
    model = Booking
    list_display = ['id', 'customer', 'booking_date']
    fieldsets = (
        (None, {'fields': ('booking_date', 'customer',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('customer', 'booking_date')}
         ),
    )


class DepartingAdmin(ModelAdmin):
    add_form = DepartingCreationFormAdmin
    form = DepartingChangeFormAdmin
    model = Departing
    list_display = ['id', 'customer', 'departing_flight_number', 'departing_flight_datetime', 'destination']
    fieldsets = (
        (None, {'fields': ('customer', 'departing_flight_number', 'departing_flight_datetime', 'destination',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('customer', 'departing_flight_number', 'departing_flight_datetime', 'destination')}
         ),
    )


class ArrivingAdmin(ModelAdmin):
    add_form = ArrivingCreationFormAdmin
    form = ArrivingChangeFormAdmin
    model = Arriving
    list_display = ['id', 'customer', 'arriving_flight_number', 'arriving_flight_datetime']
    fieldsets = (
        (None, {'fields': ('customer', 'arriving_flight_number', 'arriving_flight_datetime',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('customer', 'arriving_flight_number', 'arriving_flight_datetime')}
         ),
    )


class PaymentAdmin(ModelAdmin):
    add_form = PaymentCreationFormAdmin
    form = PaymentChangeFormAdmin
    model = Payment
    list_display = ['customer', 'date_paid', 'card_type', 'card_number', 'amount', 'expiry_date',
                    'security_number']
    fieldsets = (
        (None,
         {'fields': ('customer', 'date_paid', 'amount')}),
        ('Card info',
         {'fields': ('card_type', 'card_number', 'expiry_date', 'security_number')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('customer', 'date_paid', 'card_type', 'card_number', 'amount', 'expiry_date', 'security_number')}
         ),
    )


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Departing, DepartingAdmin)
admin.site.register(Arriving, ArrivingAdmin)
admin.site.register(Payment, PaymentAdmin)
