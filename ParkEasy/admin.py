from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomerCreationFormAdmin, CustomerChangeFormAdmin, \
    BookingCreationFormAdmin, BookingChangeFormAdmin, \
    DepartingCreationFormAdmin, DepartingChangeFormAdmin, \
    ArrivingCreationFormAdmin, ArrivingChangeFormAdmin, \
    PaymentCreationFormAdmin, PaymentChangeFormAdmin, \
    PriceCreationFormAdmin, PriceChangeFormAdmin
from .models import Customer, Booking, Departing, Arriving, Payment, Prices


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
    readonly_fields = ('payment',)

    def payment(self, booking):
        payment = 0
        if booking.booking_length == 1:
            payment = payment + 27
        elif booking.booking_length == 2:
            payment = payment + 39
        elif booking.booking_length == 3:
            payment = payment + 44
        elif booking.booking_length == 4:
            payment = payment + 50
        elif booking.booking_length == 5:
            payment = payment + 55
        elif booking.booking_length > 5:
            payment = payment + 55
            days = booking.booking_length - 5
            while days > 0:
                payment = payment + 10
                days = days - 1
        return payment
    list_display = ['id', 'customer', 'booking_date', 'booking_length', 'payment']
    fieldsets = (
        (None, {'fields': ('booking_date', 'customer', 'booking_length', 'payment',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('customer', 'booking_date', 'booking_length', 'payment')}
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
    list_display = ['booking', 'date_paid', 'amount', 'paid']
    fieldsets = (
        (None,
         {'fields': ('booking', 'date_paid', 'amount', 'paid')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('booking', 'date_paid', 'amount', 'paid')}
         ),
    )


class PriceAdmin(ModelAdmin):
    add_form = PriceCreationFormAdmin
    form = PriceChangeFormAdmin
    model = Prices
    list_display = ['id', 'vip', 'valet', 'day', 'base', 'after_five']
    fieldsets = (
        (None,
         {'fields': ('vip', 'valet', 'day', 'base', 'after_five')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('vip', 'valet', 'day', 'base', 'after_five')}
         ),
    )


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Departing, DepartingAdmin)
admin.site.register(Arriving, ArrivingAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Prices, PriceAdmin)
