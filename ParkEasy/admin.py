from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomerCreationFormAdmin, CustomerChangeFormAdmin, \
    BookingCreationFormAdmin, BookingChangeFormAdmin, \
    DepartingCreationFormAdmin, DepartingChangeFormAdmin, \
    ArrivingCreationFormAdmin, ArrivingChangeFormAdmin, \
    PriceCreationFormAdmin, PriceChangeFormAdmin,\
    VehicleCreationFormAdmin, VehicleChangeFormAdmin
from .models import Customer, Booking, Departing, Arriving, Prices, Vehicle


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
    list_display = ['id', 'customer', 'prices', 'vehicle', 'booking_date', 'booking_length', 'checked_in', 'checked_out'
                    , 'departing', 'arriving', 'vip', 'valet', 'assigned_space']
    fieldsets = (
        (None, {'fields': ('booking_date', 'customer', 'prices', 'vehicle', 'booking_length', 'checked_in',
                           'checked_out', 'departing', 'arriving', 'vip', 'valet',  'assigned_space',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('customer', 'prices', 'vehicle', 'booking_date', 'booking_length', 'checked_in', 'checked_out',
                       'departing', 'arriving', 'vip', 'valet',  'assigned_space')}
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


class PriceAdmin(ModelAdmin):
    add_form = PriceCreationFormAdmin
    form = PriceChangeFormAdmin
    model = Prices
    list_display = ['id', 'vip', 'valet', 'day', 'base', 'after_five', 'is_current']
    fieldsets = (
        (None,
         {'fields': ('vip', 'valet', 'day', 'base', 'after_five', 'is_current')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('vip', 'valet', 'day', 'base', 'after_five', 'is_current')}
         ),
    )

class VehicleAdmin(ModelAdmin):
    add_form = VehicleCreationFormAdmin
    form = VehicleChangeFormAdmin
    model = Vehicle
    list_display = ['id', 'reg_no', 'make', 'manufacturer']
    fieldsets = (
        (None,
         {'fields': ('reg_no', 'make', 'manufacturer')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('reg_no', 'make', 'manufacturer')}
         ),
    )


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Departing, DepartingAdmin)
admin.site.register(Arriving, ArrivingAdmin)
admin.site.register(Prices, PriceAdmin)
admin.site.register(Vehicle, VehicleAdmin)
