from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
from datetime import date


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Prices(models.Model):
    vip = models.IntegerField(default=0)
    valet = models.IntegerField(default=0)
    day = models.FloatField(default=1.2)
    base = models.IntegerField(default=27)
    after_five = models.IntegerField(default=10)
    start_date = models.DateField(default=timezone.now)
    length = models.IntegerField(default=365)

    def calc_start_date(self, Prices):
        for e in Prices.objects.all():
            max_date = date.min
            if e.start_date + timedelta(days=e.length) > max_date:
                max_date = e.start_date + timedelta(days=e.length)
                print(max_date)
                return e.id

class Customer(AbstractUser):
    password = models.TextField(max_length=100, default="")
    email = models.EmailField(max_length=100, default="", unique=True)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into this site.',
    )
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100)
    postcode = models.CharField(max_length=16)
    tel_no = models.CharField(max_length=20)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_username(self):
        return self.email


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    prices = models.ForeignKey(Prices, on_delete=models.CASCADE, default=90)
    booking_date = models.DateField(default=timezone.now)
    booking_length = models.IntegerField(default=0)
    def getprice(self, prices):
        Prices.calc_start_date()
    #def getprice(self, Prices):
     #   priceset = Prices.objects.get()
      #  for index, Prices in enumerate(priceset, start=0):
       #     if (index, priceset).prices.calc_start_date() == 1:
        #        print("bleh")  #add logic

class Departing(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    departing_flight_number = models.TextField(max_length=16)
    departing_flight_datetime = models.DateTimeField()
    destination = models.TextField(max_length=64)


class Arriving(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    arriving_flight_number = models.TextField(max_length=16)
    arriving_flight_datetime = models.DateTimeField()


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    date_paid = models.DateTimeField(default=timezone.now)
    paid = models.BooleanField(default=False)
    amount = models.IntegerField()
