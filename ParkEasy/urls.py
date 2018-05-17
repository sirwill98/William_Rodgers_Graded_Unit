# blog/urls.py
from . import views
from django.urls import path
from .views import booking_form, signup, payment_form, checkout, view_bookings, delete_booking, edit_booking, \
    change_password, delete_account

urlpatterns = [
    path('', views.HomePageView, name='home'),
    path('booking/', booking_form, name="booking"),
    path('signup/', signup, name="signup"),
    path('payment-form/', payment_form, name="payment"),
    path('checkout/', checkout, name="checkout"),
    path('edit_form_customer/', views.edit, name="edit"),
    path('view-bookings/', view_bookings, name="view-bookings"),
    path('edit-form/<id>/', edit_booking, name="edit-form"),
    path('delete-booking/<id>/', delete_booking, name="delete-booking"),
    path('password-change/', change_password, name="password-change"),
    path('delete-account/', delete_account, name="delete-account")
]
