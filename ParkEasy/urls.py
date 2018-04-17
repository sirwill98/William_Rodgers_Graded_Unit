# blog/urls.py
from django.conf.urls import url
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('booking/', views.BookingView.as_view(), name="booking"),
]