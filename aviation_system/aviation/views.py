from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from .models import (Flight, Passenger, Booking, Airline, Airport, 
                     Aircraft, Country, Currency, Ticket)
from .forms import FlightForm, PassengerForm, BookingForm

def home(request):
    """Home page with dashboard statistics"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM FLIGHT")
        total_flights = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM PASSENGER")
        total_passengers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM BOOKING WHERE BookingStatus='Confirmed'")
        total_bookings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM AIRLINE")
        total_airlines = cursor.fetchone()[0]
    
    context = {
        'total_flights': total_flights,
        'total_passengers': total_passengers,
        'total_bookings': total_bookings,
        'total_airlines': total_airlines,
    }
    return render(request, 'aviation/home.html', context)

# ============================================================================
# FLIGHT VIEWS
# ============================================================================

def flights_list(request):
    """List all flights"""
    flights = Flight.objects.select_related(
        'airlineid', 'departureairportcode', 'arrivalairportcode'
    ).all()
    return render(request, 'aviation/flights_list.html', {'flights': flights})

def flight_detail(request, flight_id):
    """View details of a specific flight"""
    flight = get_object_or_404(Flight, flightid=flight_id)
    tickets = Ticket.objects.filter(flightid=flight_id).select_related('passengerid')
    
    context = {
        'flight': flight,
        'tickets': tickets,
    }
    return render(request, 'aviation/flight_detail.html', context)

def add_flight(request):
    """Add a new flight"""
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO FLIGHT (FlightID, FlightNumber, ScheduledDeparture, 
                    ScheduledArrival, FlightStatus, AirlineID, AircraftID, 
                    DepartureAirportCode, ArrivalAirportCode, DepartureTerminalID, 
                    ArrivalTerminalID, DepartureGateNumber, ArrivalGateNumber)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    form.cleaned_data['flightid'],
                    form.cleaned_data['flightnumber'],
                    form.cleaned_data['scheduleddeparture'],
                    form.cleaned_data['scheduledarrival'],
                    form.cleaned_data['flightstatus'],
                    form.cleaned_data['airlineid'],
                    form.cleaned_data['aircraftid'],
                    form.cleaned_data['departureairportcode'],
                    form.cleaned_data['arrivalairportcode'],
                    form.cleaned_data['departureterminalid'],
                    form.cleaned_data['arrivalterminalid'],
                    form.cleaned_data['departuregatenumber'],
                    form.cleaned_data['arrivalgatenumber'],
                ])
            messages.success(request, 'Flight added successfully!')
            return redirect('flights_list')
    else:
        form = FlightForm()
    
    # Get reference data for form
    airlines = Airline.objects.all()
    airports = Airport.objects.all()
    aircraft = Aircraft.objects.all()
    
    context = {
        'form': form,
        'airlines': airlines,
        'airports': airports,
        'aircraft': aircraft,
    }
    return render(request, 'aviation/add_flight.html', context)

# ============================================================================
# PASSENGER VIEWS
# ============================================================================

def passengers_list(request):
    """List all passengers"""
    passengers = Passenger.objects.select_related('countrycode').all()
    return render(request, 'aviation/passengers_list.html', {'passengers': passengers})

def passenger_detail(request, passenger_id):
    """View details of a specific passenger"""
    passenger = get_object_or_404(Passenger, passengerid=passenger_id)
    bookings = Booking.objects.filter(passengerid=passenger_id)
    
    context = {
        'passenger': passenger,
        'bookings': bookings,
    }
    return render(request, 'aviation/passenger_detail.html', context)

def add_passenger(request):
    """Add a new passenger"""
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO PASSENGER (PassengerID, FirstName, LastName, Email, 
                    Phone, DateOfBirth, PassportNumber, CountryCode, Nationality)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    form.cleaned_data['passengerid'],
                    form.cleaned_data['firstname'],
                    form.cleaned_data['lastname'],
                    form.cleaned_data['email'],
                    form.cleaned_data['phone'],
                    form.cleaned_data['dateofbirth'],
                    form.cleaned_data['passportnumber'],
                    form.cleaned_data['countrycode'],
                    form.cleaned_data['nationality'],
                ])
            messages.success(request, 'Passenger added successfully!')
            return redirect('passengers_list')
    else:
        form = PassengerForm()
    
    countries = Country.objects.all()
    context = {
        'form': form,
        'countries': countries,
    }
    return render(request, 'aviation/add_passenger.html', context)

# ============================================================================
# BOOKING VIEWS
# ============================================================================

def bookings_list(request):
    """List all bookings"""
    bookings = Booking.objects.select_related('passengerid', 'currencycode').all()
    return render(request, 'aviation/bookings_list.html', {'bookings': bookings})

def booking_detail(request, booking_id):
    """View details of a specific booking"""
    booking = get_object_or_404(Booking, bookingid=booking_id)
    tickets = Ticket.objects.filter(bookingid=booking_id).select_related('flightid')
    
    context = {
        'booking': booking,
        'tickets': tickets,
    }
    return render(request, 'aviation/booking_detail.html', context)

def add_booking(request):
    """Add a new booking"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO BOOKING (BookingID, BookingDate, TotalAmount, 
                    BookingStatus, BookingChannel, PassengerID, CurrencyCode)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [
                    form.cleaned_data['bookingid'],
                    form.cleaned_data['bookingdate'],
                    form.cleaned_data['totalamount'],
                    form.cleaned_data['bookingstatus'],
                    form.cleaned_data['bookingchannel'],
                    form.cleaned_data['passengerid'],
                    form.cleaned_data['currencycode'],
                ])
            messages.success(request, 'Booking added successfully!')
            return redirect('bookings_list')
    else:
        form = BookingForm()
    
    passengers = Passenger.objects.all()
    currencies = Currency.objects.all()
    
    context = {
        'form': form,
        'passengers': passengers,
        'currencies': currencies,
    }
    return render(request, 'aviation/add_booking.html', context)

# ============================================================================
# AIRLINE VIEWS
# ============================================================================

def airlines_list(request):
    """List all airlines"""
    airlines = Airline.objects.select_related('headquarterscityid', 'allianceid').all()
    return render(request, 'aviation/airlines_list.html', {'airlines': airlines})

def airline_detail(request, airline_id):
    """View details of a specific airline"""
    airline = get_object_or_404(Airline, airlineid=airline_id)
    flights = Flight.objects.filter(airlineid=airline_id)
    aircraft = Aircraft.objects.filter(airlineid=airline_id)
    
    context = {
        'airline': airline,
        'flights': flights,
        'aircraft': aircraft,
    }
    return render(request, 'aviation/airline_detail.html', context)

# ============================================================================
# AIRPORT VIEWS
# ============================================================================

def airports_list(request):
    """List all airports"""
    airports = Airport.objects.select_related('cityid').all()
    return render(request, 'aviation/airports_list.html', {'airports': airports})

def airport_detail(request, airport_code):
    """View details of a specific airport"""
    airport = get_object_or_404(Airport, airportcode=airport_code)
    departures = Flight.objects.filter(departureairportcode=airport_code)
    arrivals = Flight.objects.filter(arrivalairportcode=airport_code)
    
    context = {
        'airport': airport,
        'departures': departures,
        'arrivals': arrivals,
    }
    return render(request, 'aviation/airport_detail.html', context)

# ============================================================================
# SEARCH VIEW
# ============================================================================

def search_flights(request):
    """Search flights by various criteria"""
    results = []
    query = request.GET.get('q', '')
    
    if query:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT f.FlightID, f.FlightNumber, f.ScheduledDeparture, 
                       f.ScheduledArrival, f.FlightStatus, 
                       al.AirlineName, 
                       dep.AirportName as DepartureAirport,
                       arr.AirportName as ArrivalAirport
                FROM FLIGHT f
                JOIN AIRLINE al ON f.AirlineID = al.AirlineID
                JOIN AIRPORT dep ON f.DepartureAirportCode = dep.AirportCode
                JOIN AIRPORT arr ON f.ArrivalAirportCode = arr.AirportCode
                WHERE f.FlightNumber LIKE %s OR al.AirlineName LIKE %s
            """, [f'%{query}%', f'%{query}%'])
            
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {
        'results': results,
        'query': query,
    }
    return render(request, 'aviation/search_results.html', context)
