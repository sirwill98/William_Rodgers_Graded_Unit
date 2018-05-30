# blog/urls.py
from . import views
from django.urls import path
from .views import booking_form, signup, payment_form, checkout, view_bookings, delete_booking, edit_booking, \
    change_password, delete_account, vehicle_form, report_init, add_dates, staff_home_page_view, departing_form, \
    arriving_form

urlpatterns = [
    path('', views.home_page_view, name='home'),
    path('booking/', booking_form, name="booking"),
    path('vehicle/', vehicle_form, name="vehicle"),
    path('departing/', departing_form, name="departing"),
    path('arriving/', arriving_form, name="arriving"),
    path('signup/', signup, name="signup"),
    path('payment-form/', payment_form, name="payment"),
    path('checkout/', checkout, name="checkout"),
    path('edit_form_customer/', views.edit, name="edit"),
    path('view-bookings/', view_bookings, name="view-bookings"),
    path('edit-form/<id>/', edit_booking, name="edit-form"),
    path('delete-booking/<id>/', delete_booking, name="delete-booking"),
    path('password-change/', change_password, name="password-change"),
    path('delete-account/', delete_account, name="delete-account"),
    path('Staff/Reports/', report_init, name='generate-reports'),
    path('Staff/Report_Dates', add_dates, name='add-dates'),
    path('Staff/Home', staff_home_page_view, name='staff-home')
]
