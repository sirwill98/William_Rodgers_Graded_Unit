# blog/urls.py
from . import views
from django.urls import path, include
from .views import booking_form, signup

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('booking/', booking_form, name="booking"),
    path('signup/', signup, name="signup"),
]