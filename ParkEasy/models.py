from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta


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


# this is the vehicle model, every booking must have a vehicle, thr bookings need to have a valid registration
# number to be booked
class Vehicle(models.Model):
    reg_no_regex = RegexValidator(regex=r'^[A-Z]{2}[0-9]{2} [A-Z]{3}$',
                                  message="Registration must be entered in the format: 'AB12 CDE'.",
                                  code='invalid_registration')
    reg_no = models.CharField(max_length=8, validators=[reg_no_regex])
    make = models.CharField(max_length=64)
    manufacturer = models.CharField(max_length=64)

    # used to name the objects
    def __str__(self):
        return 'Vehicle: ' + self.manufacturer + ' ' + self.make


# used to define the prices that the whole system works off of
class Prices(models.Model):
    vip = models.IntegerField(default=0)
    valet = models.IntegerField(default=0)
    day = models.FloatField(default=1.2)
    base = models.IntegerField(default=27)
    after_five = models.IntegerField(default=10)
    is_current = models.BooleanField(default=False)
    quantity = models.IntegerField(default=3)


class Customer(AbstractUser):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    password = models.CharField(max_length=100, default="")
    email = models.EmailField(max_length=100, default="", unique=True)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into this site.',
    )
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100)
    postcode_regex = RegexValidator(regex=r'([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|'
                                          r'(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z]'
                                          r'[A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))\s?[0-9][A-Za-z]{2})',
                                    message="postcode must be a valid uk postcode")
    postcode = models.CharField(max_length=16, validators=[postcode_regex])
    tel_no_regex = RegexValidator(regex=r'^\+?l?\d{9,15}$',
                                  message="Phone number must be entered in the format: '+999999999'. Up to 15 digits "
                                          "allowed.")
    tel_no = models.CharField(validators=[tel_no_regex], max_length=17)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    # because the username is not used it is overridden by email

    def get_username(self):
        return self.email


class Departing(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    flight_no_validator = RegexValidator(r'^([a-z][a-z]|[a-z][0-9]|[0-9][a-z])[a-z]?[0-9]{1,4}[a-z]?$',
                                         message='please enter a valid flight number')
    departing_flight_number = models.CharField(max_length=16)
    departing_flight_datetime = models.DateTimeField()
    # list of every location glasgow airport flies to
    destination_choices = (
        ("AMSTERDAM", "amsterdam"),
        ("ANTALYA-TURKEY", "antalya-turkey"),
        ("BARCELONA", "barcelona"),
        ("BARRA", "barra"),
        ("BELFAST", "belfast"),
        ("BENBECULA", "benbecula"),
        ("BERGEN", "bergen"),
        ("BERLIN", "berlin"),
        ("BIRMINGHAM", "birmingham"),
        ("BODRUM-TURKEY", "bodrum-turkey"),
        ("BORDEAUX", "bordeaux"),
        ("BOURGAS-BULGARIA", "bourgas-bulgaria"),
        ("BRIDGETOWN-BARBADOS", "bridgetown-barbados"),
        ("BRISTOL", "bristol"),
        ("BRUSSELS", "brussels"),
        ("BUCHAREST", "bucharest"),
        ("BUDAPEST", "budapest"),
        ("BYDGOSZCZ", "bydgoszcz"),
        ("CAMPBELTOWN", "campbeltown"),
        ("CANCUN", "cancun"),
        ("CAPE-VERDE-SAL", "cape-verde-sal"),
        ("CARCASSONNE", "carcassonne"),
        ("CARDIFF", "cardiff"),
        ("CAYO-COCO", "cayo-coco"),
        ("CHAMBERY", "chambery"),
        ("CHANIA-CRETE", "chania-crete"),
        ("CORFU", "corfu"),
        ("CORK", "cork"),
        ("COSTA-BLANCA-ALICANTE", "costa-blanca-alicante"),
        ("COSTA-BRAVA-GIRONA", "costa-brava-girona"),
        ("COSTA-DEL-SOL-MALAGA", "costa-del-sol-malaga"),
        ("COSTA-DORADA-REUS", "costa-dorada-reus"),
        ("DALAMAN-TURKEY", "dalaman-turkey"),
        ("DERRY", "derry"),
        ("DONEGAL", "donegal"),
        ("DUBAI", "dubai"),
        ("DUBLIN", "dublin"),
        ("DUBROVNIK", "dubrovnik"),
        ("DUESSELDORF", "duesseldorf"),
        ("EAST-MIDLANDS", "east-midlands"),
        ("EXETER", "exeter"),
        ("FARO-ALGARVE", "faro-algarve"),
        ("FRANKFURT", "frankfurt"),
        ("FUERTEVENTURA", "fuerteventura"),
        ("GDANSK", "gdansk"),
        ("GENEVA", "geneva"),
        ("GRAN-CANARIA", "gran-canaria"),
        ("GRENOBLE", "grenoble"),
        ("HALIFAX", "halifax"),
        ("HALKIDIKI", "halkidiki"),
        ("HERAKLION-CRETE", "heraklion-crete"),
        ("HURGHADA", "hurghada"),
        ("IBIZA", "ibiza"),
        ("ISLAY", "islay"),
        ("ISLE-OF-MAN", "isle-of-man"),
        ("IZMIR", "izmir"),
        ("JERSEY", "jersey"),
        ("KATOWICE", "katowice"),
        ("KEFALONIA", "kefalonia"),
        ("KIRKWALL", "kirkwall"),
        ("KITTILAE", "kittilae"),
        ("KOS", "kos"),
        ("KRAKOW", "krakow"),
        ("LANZAROTE", "lanzarote"),
        ("LARNACA-CYPRUS", "larnaca-cyprus"),
        ("LAS-VEGAS", "las-vegas"),
        ("LISBON", "lisbon"),
        ("LONDON", "london"),
        ("MADEIRA", "madeira"),
        ("MADRID", "madrid"),
        ("MALTA", "malta"),
        ("MANCHESTER", "manchester"),
        ("MARSEILLE", "marseille"),
        ("MENORCA", "menorca"),
        ("MILAN", "milan"),
        ("MONTEGO-BAY-JAMAICA", "montego-bay-jamaica"),
        ("MUNICH", "munich"),
        ("NAPLES", "naples"),
        ("NEW-YORK", "new-york"),
        ("NEWQUAY", "newquay"),
        ("NORWICH", "norwich"),
        ("ORLANDO", "orlando"),
        ("PALANGA", "palanga"),
        ("PALMA-DE-MALLORCA", "palma-de-mallorca"),
        ("PAPHOS-CYPRUS", "paphos-cyprus"),
        ("PARIS", "paris"),
        ("PHILADELPHIA", "philadelphia"),
        ("PRAGUE", "prague"),
        ("REYKJAVIK", "reykjavik"),
        ("RHODES", "rhodes"),
        ("RIGA", "riga"),
        ("ROME", "rome"),
        ("ROVANIEMI", "rovaniemi"),
        ("SALZBURG", "salzburg"),
        ("SOFIA", "sofia"),
        ("SOUTHAMPTON", "southampton"),
        ("SPLIT", "split"),
        ("STORNOWAY", "stornoway"),
        ("SUMBURGH", "sumburgh"),
        ("TENERIFE", "tenerife"),
        ("TIREE", "tiree"),
        ("TORONTO", "toronto"),
        ("TUNISIA-ENFIDHA", "tunisia-enfidha"),
        ("TURIN", "turin"),
        ("VALENCIA", "valencia"),
        ("VANCOUVER", "vancouver"),
        ("VERONA", "verona"),
        ("WARSAW", "warsaw"),
        ("WROCLAW", "wroclaw"),
        ("ZANTE", "zante ")
    )
    destination = models.CharField(max_length=64, choices=destination_choices)

    # used to name the objects
    def __str__(self):
        return 'Flight: ' + self.departing_flight_number + ' ' + str(self.departing_flight_datetime.date())


class Arriving(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    flight_no_validator = RegexValidator(r'^([a-z][a-z]|[a-z][0-9]|[0-9][a-z])[a-z]?[0-9]{1,4}[a-z]?$',
                                         message='please enter a valid flight number')
    arriving_flight_number = models.CharField(max_length=16)
    arriving_flight_datetime = models.DateTimeField()

    # used to name the objects
    def __str__(self):
        return 'Flight: ' + self.arriving_flight_number + ' ' + str(self.arriving_flight_datetime.date())


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    prices = models.ForeignKey(Prices, on_delete=models.CASCADE, default=1)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    departing = models.ForeignKey(Departing, on_delete=models.CASCADE)
    arriving = models.ForeignKey(Arriving, on_delete=models.CASCADE)
    vip = models.BooleanField(default=False)
    valet = models.BooleanField(default=False)
    booking_date = models.DateField(default=timezone.now)
    booking_length = models.IntegerField(default=0)
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)
    date_created = models.DateField(default=timezone.now)
    assigned_space = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)

    # used to check for availability of spaces based on quantity
    def space_check(self):
        if Booking.objects.filter(checked_out=False, assigned_space=True).count() >= \
                Prices.objects.get(is_current=True).quantity:
            self.assigned_space = False
        else:
            self.assigned_space = True

    # used to check bookings out and to give the new available space to the first booking waiting for it
    def check_out(self):
        if Booking.objects.filter(assigned_space=True).count() < Prices.objects.get(is_current=True).quantity:
            Checkset = Booking.objects.filter(checked_in=False, checked_out=False, assigned_space=False, refunded=False)
            if Checkset:
                next_space = Checkset.first()
                next_space.assigned_space = True
                next_space.save()
                return
            else:
                return

    # calculates the end date of the booking
    def calc_end(self):
        end = self.booking_date + timedelta(days=self.booking_length+1)
        return end

    # returns the total cost of the booking
    def calc_amount(self, days):
        prices = Prices.objects.get(id=self.prices.id)
        amount = prices.base
        if days == 2:
            amount = amount * prices.day
        elif days == 3:
            amount = amount * prices.day ** 2
        elif days == 4:
            amount = amount * prices.day ** 3
        elif days == 5:
            amount = amount * prices.day ** 4
        elif days > 5:
            amount = amount * prices.day ** 5
            days = days - 5
            while days > 0:
                amount = amount + prices.after_five
                days = days - 1

        if self.vip and self.valet:
            amount = amount + prices.vip + prices.valet
        elif self.vip:
            amount = amount + prices.vip
        elif self.valet:
            amount = amount + prices.valet
        return int(amount)


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    date_paid = models.DateTimeField(default=timezone.now)
    paid = models.BooleanField(default=False)
    amount = models.IntegerField()
    charge_id = models.CharField(max_length=64)


# class Space(models.Model):

