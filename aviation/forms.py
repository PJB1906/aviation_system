from django import forms
from .models import Flight, Passenger, Booking, Airline, Airport, Aircraft

class FlightForm(forms.Form):
    flightid = forms.IntegerField(label='Flight ID')
    flightnumber = forms.CharField(max_length=20, label='Flight Number')
    scheduleddeparture = forms.DateTimeField(label='Scheduled Departure', 
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    scheduledarrival = forms.DateTimeField(label='Scheduled Arrival',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    flightstatus = forms.ChoiceField(choices=[
        ('Scheduled', 'Scheduled'),
        ('In-Flight', 'In-Flight'),
        ('Completed', 'Completed'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled')
    ])
    airlineid = forms.IntegerField(label='Airline ID')
    aircraftid = forms.IntegerField(label='Aircraft ID')
    departureairportcode = forms.IntegerField(label='Departure Airport Code')
    arrivalairportcode = forms.IntegerField(label='Arrival Airport Code')
    departureterminalid = forms.IntegerField(label='Departure Terminal ID')
    arrivalterminalid = forms.IntegerField(label='Arrival Terminal ID')
    departuregatenumber = forms.IntegerField(label='Departure Gate Number')
    arrivalgatenumber = forms.IntegerField(label='Arrival Gate Number')

class PassengerForm(forms.Form):
    passengerid = forms.IntegerField(label='Passenger ID')
    firstname = forms.CharField(max_length=50, label='First Name')
    lastname = forms.CharField(max_length=50, label='Last Name')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=20, label='Phone')
    dateofbirth = forms.DateField(label='Date of Birth',
        widget=forms.DateInput(attrs={'type': 'date'}))
    passportnumber = forms.CharField(max_length=50, label='Passport Number')
    countrycode = forms.IntegerField(label='Country Code')
    nationality = forms.CharField(max_length=50, label='Nationality')

class BookingForm(forms.Form):
    bookingid = forms.IntegerField(label='Booking ID')
    bookingdate = forms.DateTimeField(label='Booking Date',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    totalamount = forms.DecimalField(max_digits=10, decimal_places=2, label='Total Amount')
    bookingstatus = forms.ChoiceField(choices=[
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled')
    ])
    bookingchannel = forms.ChoiceField(choices=[
        ('Website', 'Website'),
        ('Mobile App', 'Mobile App'),
        ('Call Center', 'Call Center'),
        ('Travel Agent', 'Travel Agent')
    ])
    passengerid = forms.IntegerField(label='Passenger ID')
    currencycode = forms.IntegerField(label='Currency Code')