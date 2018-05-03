# blog/urls.py
from . import views
from django.urls import path, include
from .views import booking_form, signup, payment_form, checkout, edit, view_bookings

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('booking/', booking_form, name="booking"),
    path('signup/', signup, name="signup"),
    path('payment-form/', payment_form, name="payment"),
    path('checkout/', checkout, name="checkout"),
    path('edit/<int:pk>/', views.update_customer.as_view(), name="edit"),
    path('view-bookings/', view_bookings, name="view-bookings")

]