from django.views.generic import ListView
from .models import Customer, Booking
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import BookingCreationFormCustomer, TestForm


class HomePageView(ListView):
    model = Customer
    template_name = 'home.html'


class BookingView(ListView):
    model = Booking
    template_name = 'booking.html'


def booking_form(request):
    if request.method == 'POST':
        form = BookingCreationFormCustomer(request.POST)
        start = form.POST['start']
        end = form.POST['end']
        length = end - start
        user = form.user
        newbooking = Booking(customer=user, booking_date=start, booking_length=length)
    else:
        form = BookingCreationFormCustomer()

    return render(request, 'booking.html', {'form': form})
