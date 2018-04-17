from django.views.generic import ListView
from .models import Customer, Booking
from django.http import HttpResponseRedirect


class HomePageView(ListView):
    model = Customer
    template_name = 'home.html'

    def make_booking(self, request):
        start = request.POST['start']
        end = request.POST['end']
        length = end - start
        user = request.user
        newbooking = Booking(customer=user, booking_date=start, booking_length=length)
        return HttpResponseRedirect('/')


class BookingView(ListView):
    model = Customer
    template_name = 'booking.html'


