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
        
        cursor.execute("SELECT COUNT(*) FROM AIRCRAFT")
        active_aircraft = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM AIRPORT")
        total_airports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM COUNTRY")
        total_countries = cursor.fetchone()[0]
    
    # Get recent flights
    recent_flights = Flight.objects.select_related(
        'airlineid', 'departureairportcode', 'arrivalairportcode'
    ).order_by('-scheduleddeparture')[:5]
    
    context = {
        'total_flights': total_flights,
        'active_aircraft': active_aircraft,
        'total_airports': total_airports,
        'total_countries': total_countries,
        'database_size': '4.2 GB',
        'recent_flights': recent_flights,
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

def edit_flight(request, flight_id):
    """Edit an existing flight"""
    flight = get_object_or_404(Flight, flightid=flight_id)
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Handle optional datetime fields
            actual_departure = request.POST.get('actualdeparture') or None
            actual_arrival = request.POST.get('actualarrival') or None
            
            cursor.execute("""
                UPDATE FLIGHT SET
                    FlightNumber = %s,
                    ScheduledDeparture = %s,
                    ScheduledArrival = %s,
                    ActualDeparture = %s,
                    ActualArrival = %s,
                    FlightStatus = %s,
                    AirlineID = %s,
                    AircraftID = %s,
                    DepartureAirportCode = %s,
                    ArrivalAirportCode = %s,
                    DepartureTerminalID = %s,
                    ArrivalTerminalID = %s,
                    DepartureGateNumber = %s,
                    ArrivalGateNumber = %s
                WHERE FlightID = %s
            """, [
                request.POST.get('flightnumber'),
                request.POST.get('scheduleddeparture'),
                request.POST.get('scheduledarrival'),
                actual_departure,
                actual_arrival,
                request.POST.get('flightstatus'),
                request.POST.get('airlineid'),
                request.POST.get('aircraftid'),
                request.POST.get('departureairportcode'),
                request.POST.get('arrivalairportcode'),
                request.POST.get('departureterminalid'),
                request.POST.get('arrivalterminalid'),
                request.POST.get('departuregatenumber'),
                request.POST.get('arrivalgatenumber'),
                flight_id,
            ])
        messages.success(request, 'Flight updated successfully!')
        return redirect('flights_list')
    
    # Get reference data for form
    airlines = Airline.objects.all()
    airports = Airport.objects.all()
    aircraft = Aircraft.objects.all()
    
    context = {
        'flight': flight,
        'airlines': airlines,
        'airports': airports,
        'aircraft': aircraft,
    }
    return render(request, 'aviation/edit_flight.html', context)

def delete_flight(request, flight_id):
    """Delete a flight"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM FLIGHT WHERE FlightID = %s", [flight_id])
        messages.success(request, 'Flight deleted successfully!')
    return redirect('flights_list')

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
# Additional CRUD views for remaining tables

# ============================================================================
# PASSENGER EDIT/DELETE
# ============================================================================

def edit_passenger(request, passenger_id):
    """Edit an existing passenger"""
    passenger = get_object_or_404(Passenger, passengerid=passenger_id)
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PASSENGER SET
                    FirstName = %s,
                    LastName = %s,
                    Email = %s,
                    Phone = %s,
                    DateOfBirth = %s,
                    PassportNumber = %s,
                    CountryCode = %s,
                    Nationality = %s
                WHERE PassengerID = %s
            """, [
                request.POST.get('firstname'),
                request.POST.get('lastname'),
                request.POST.get('email'),
                request.POST.get('phone'),
                request.POST.get('dateofbirth'),
                request.POST.get('passportnumber'),
                request.POST.get('countrycode'),
                request.POST.get('nationality'),
                passenger_id,
            ])
        messages.success(request, 'Passenger updated successfully!')
        return redirect('passengers_list')
    
    countries = Country.objects.all()
    context = {
        'passenger': passenger,
        'countries': countries,
    }
    return render(request, 'aviation/edit_passenger.html', context)

def delete_passenger(request, passenger_id):
    """Delete a passenger"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM PASSENGER WHERE PassengerID = %s", [passenger_id])
        messages.success(request, 'Passenger deleted successfully!')
    return redirect('passengers_list')

# ============================================================================
# BOOKING EDIT/DELETE
# ============================================================================

def edit_booking(request, booking_id):
    """Edit an existing booking"""
    booking = get_object_or_404(Booking, bookingid=booking_id)
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE BOOKING SET
                    BookingDate = %s,
                    TotalAmount = %s,
                    BookingStatus = %s,
                    BookingChannel = %s,
                    PassengerID = %s,
                    CurrencyCode = %s
                WHERE BookingID = %s
            """, [
                request.POST.get('bookingdate'),
                request.POST.get('totalamount'),
                request.POST.get('bookingstatus'),
                request.POST.get('bookingchannel'),
                request.POST.get('passengerid'),
                request.POST.get('currencycode'),
                booking_id,
            ])
        messages.success(request, 'Booking updated successfully!')
        return redirect('bookings_list')
    
    passengers = Passenger.objects.all()
    currencies = Currency.objects.all()
    context = {
        'booking': booking,
        'passengers': passengers,
        'currencies': currencies,
    }
    return render(request, 'aviation/edit_booking.html', context)

def delete_booking(request, booking_id):
    """Delete a booking"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM BOOKING WHERE BookingID = %s", [booking_id])
        messages.success(request, 'Booking deleted successfully!')
    return redirect('bookings_list')

# ============================================================================
# AIRLINE CRUD
# ============================================================================

from .models import Alliance, City

def add_airline(request):
    """Add a new airline"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO AIRLINE (AirlineID, AirlineName, AirlineICAO, 
                HeadquartersCityID, FoundedYear, AllianceID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                request.POST.get('airlineid'),
                request.POST.get('airlinename'),
                request.POST.get('airlineicao'),
                request.POST.get('headquarterscityid'),
                request.POST.get('foundedyear'),
                request.POST.get('allianceid'),
            ])
        messages.success(request, 'Airline added successfully!')
        return redirect('airlines_list')
    
    cities = City.objects.all()
    alliances = Alliance.objects.all()
    context = {
        'cities': cities,
        'alliances': alliances,
    }
    return render(request, 'aviation/add_airline.html', context)

def edit_airline(request, airline_id):
    """Edit an existing airline"""
    airline = get_object_or_404(Airline, airlineid=airline_id)
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE AIRLINE SET
                    AirlineName = %s,
                    AirlineICAO = %s,
                    HeadquartersCityID = %s,
                    FoundedYear = %s,
                    AllianceID = %s
                WHERE AirlineID = %s
            """, [
                request.POST.get('airlinename'),
                request.POST.get('airlineicao'),
                request.POST.get('headquarterscityid'),
                request.POST.get('foundedyear'),
                request.POST.get('allianceid'),
                airline_id,
            ])
        messages.success(request, 'Airline updated successfully!')
        return redirect('airlines_list')
    
    cities = City.objects.all()
    alliances = Alliance.objects.all()
    context = {
        'airline': airline,
        'cities': cities,
        'alliances': alliances,
    }
    return render(request, 'aviation/edit_airline.html', context)

def delete_airline(request, airline_id):
    """Delete an airline"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM AIRLINE WHERE AirlineID = %s", [airline_id])
        messages.success(request, 'Airline deleted successfully!')
    return redirect('airlines_list')

# ============================================================================
# AIRPORT CRUD
# ============================================================================

def add_airport(request):
    """Add a new airport"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO AIRPORT (AirportCode, AirportName, Latitude, 
                Longitude, Timezone, CityID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                request.POST.get('airportcode'),
                request.POST.get('airportname'),
                request.POST.get('latitude'),
                request.POST.get('longitude'),
                request.POST.get('timezone'),
                request.POST.get('cityid'),
            ])
        messages.success(request, 'Airport added successfully!')
        return redirect('airports_list')
    
    cities = City.objects.all()
    context = {'cities': cities}
    return render(request, 'aviation/add_airport.html', context)

def edit_airport(request, airport_code):
    """Edit an existing airport"""
    airport = get_object_or_404(Airport, airportcode=airport_code)
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE AIRPORT SET
                    AirportName = %s,
                    Latitude = %s,
                    Longitude = %s,
                    Timezone = %s,
                    CityID = %s
                WHERE AirportCode = %s
            """, [
                request.POST.get('airportname'),
                request.POST.get('latitude'),
                request.POST.get('longitude'),
                request.POST.get('timezone'),
                request.POST.get('cityid'),
                airport_code,
            ])
        messages.success(request, 'Airport updated successfully!')
        return redirect('airports_list')
    
    cities = City.objects.all()
    context = {
        'airport': airport,
        'cities': cities,
    }
    return render(request, 'aviation/edit_airport.html', context)

def delete_airport(request, airport_code):
    """Delete an airport"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM AIRPORT WHERE AirportCode = %s", [airport_code])
        messages.success(request, 'Airport deleted successfully!')
    return redirect('airports_list')

# ============================================================================
# AIRCRAFT, ROUTES, CREW, MAINTENANCE, COUNTRIES - STUB VIEWS
# ============================================================================

# Note: Route, CrewMember, MaintenanceRecord models need to be added to models.py
# from .models import Route, CrewMember, MaintenanceRecord, AircraftType

def aircraft_list(request):
    """List all aircraft"""
    aircraft = Aircraft.objects.select_related('airlineid', 'aircrafttypecode').all()
    return render(request, 'aviation/aircraft_list.html', {'aircraft': aircraft})

def add_aircraft(request):
    """Add new aircraft"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO AIRCRAFT (AircraftID, ManufactureYear, LastMaintenanceDate, 
                AirlineID, AircraftTypeCode)
                VALUES (%s, %s, %s, %s, %s)
            """, [
                request.POST.get('aircraftid'),
                request.POST.get('manufactureyear'),
                request.POST.get('lastmaintenancedate'),
                request.POST.get('airlineid'),
                request.POST.get('aircrafttypecode'),
            ])
        messages.success(request, 'Aircraft added successfully!')
        return redirect('aircraft_list')
    
    airlines = Airline.objects.all()
    aircraft_types = AircraftType.objects.all()
    context = {'airlines': airlines, 'aircraft_types': aircraft_types}
    return render(request, 'aviation/add_aircraft.html', context)

def edit_aircraft(request, aircraft_id):
    """Edit aircraft"""
    aircraft = get_object_or_404(Aircraft, aircraftid=aircraft_id)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE AIRCRAFT SET ManufactureYear = %s, LastMaintenanceDate = %s,
                AirlineID = %s, AircraftTypeCode = %s WHERE AircraftID = %s
            """, [
                request.POST.get('manufactureyear'),
                request.POST.get('lastmaintenancedate'),
                request.POST.get('airlineid'),
                request.POST.get('aircrafttypecode'),
                aircraft_id,
            ])
        messages.success(request, 'Aircraft updated successfully!')
        return redirect('aircraft_list')
    
    airlines = Airline.objects.all()
    aircraft_types = AircraftType.objects.all()
    context = {'aircraft': aircraft, 'airlines': airlines, 'aircraft_types': aircraft_types}
    return render(request, 'aviation/edit_aircraft.html', context)

def delete_aircraft(request, aircraft_id):
    """Delete aircraft"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM AIRCRAFT WHERE AircraftID = %s", [aircraft_id])
        messages.success(request, 'Aircraft deleted successfully!')
    return redirect('aircraft_list')

# Routes
def routes_list(request):
    """List all routes"""
    # Using raw SQL since Route model doesn't exist in models.py yet
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.RouteID, r.DistanceKM, r.EstimatedDurationMins, r.RouteType,
                   o.AirportName as OriginName, d.AirportName as DestName
            FROM ROUTE r
            JOIN AIRPORT o ON r.OriginAirportCode = o.AirportCode
            JOIN AIRPORT d ON r.DestinationAirportCode = d.AirportCode
        """)
        columns = [col[0] for col in cursor.description]
        routes = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return render(request, 'aviation/routes_list.html', {'routes': routes})

def add_route(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ROUTE (RouteID, DistanceKM, EstimatedDurationMins, RouteType,
                OriginAirportCode, DestinationAirportCode)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                request.POST.get('routeid'),
                request.POST.get('distancekm'),
                request.POST.get('estimateddurationmins'),
                request.POST.get('routetype'),
                request.POST.get('originairportcode'),
                request.POST.get('destinationairportcode'),
            ])
        messages.success(request, 'Route added successfully!')
        return redirect('routes_list')
    airports = Airport.objects.all()
    return render(request, 'aviation/add_route.html', {'airports': airports})

def edit_route(request, route_id):
    route = get_object_or_404(Route, routeid=route_id)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ROUTE SET DistanceKM = %s, EstimatedDurationMins = %s, RouteType = %s,
                OriginAirportCode = %s, DestinationAirportCode = %s WHERE RouteID = %s
            """, [
                request.POST.get('distancekm'),
                request.POST.get('estimateddurationmins'),
                request.POST.get('routetype'),
                request.POST.get('originairportcode'),
                request.POST.get('destinationairportcode'),
                route_id,
            ])
        messages.success(request, 'Route updated successfully!')
        return redirect('routes_list')
    airports = Airport.objects.all()
    return render(request, 'aviation/edit_route.html', {'route': route, 'airports': airports})

def delete_route(request, route_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ROUTE WHERE RouteID = %s", [route_id])
        messages.success(request, 'Route deleted successfully!')
    return redirect('routes_list')

# Crew
def crew_list(request):
    """List all crew members"""
    # Using raw SQL since CrewMember model doesn't exist in models.py yet
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.CrewID, c.FirstName, c.LastName, c.CrewType, c.HireDate,
                   a.AirlineName, ap.AirportName
            FROM CREW_MEMBER c
            JOIN AIRLINE a ON c.AirlineID = a.AirlineID
            JOIN AIRPORT ap ON c.AirportCode = ap.AirportCode
        """)
        columns = [col[0] for col in cursor.description]
        crew = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return render(request, 'aviation/crew_list.html', {'crew': crew})

def add_crew(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO CREW_MEMBER (CrewID, FirstName, LastName, DateOfBirth, HireDate,
                CrewType, AirlineID, AirportCode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                request.POST.get('crewid'),
                request.POST.get('firstname'),
                request.POST.get('lastname'),
                request.POST.get('dateofbirth'),
                request.POST.get('hiredate'),
                request.POST.get('crewtype'),
                request.POST.get('airlineid'),
                request.POST.get('airportcode'),
            ])
        messages.success(request, 'Crew member added successfully!')
        return redirect('crew_list')
    airlines = Airline.objects.all()
    airports = Airport.objects.all()
    return render(request, 'aviation/add_crew.html', {'airlines': airlines, 'airports': airports})

def edit_crew(request, crew_id):
    crew = get_object_or_404(CrewMember, crewid=crew_id)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE CREW_MEMBER SET FirstName = %s, LastName = %s, DateOfBirth = %s,
                HireDate = %s, CrewType = %s, AirlineID = %s, AirportCode = %s WHERE CrewID = %s
            """, [
                request.POST.get('firstname'),
                request.POST.get('lastname'),
                request.POST.get('dateofbirth'),
                request.POST.get('hiredate'),
                request.POST.get('crewtype'),
                request.POST.get('airlineid'),
                request.POST.get('airportcode'),
                crew_id,
            ])
        messages.success(request, 'Crew member updated successfully!')
        return redirect('crew_list')
    airlines = Airline.objects.all()
    airports = Airport.objects.all()
    return render(request, 'aviation/edit_crew.html', {'crew': crew, 'airlines': airlines, 'airports': airports})

def delete_crew(request, crew_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM CREW_MEMBER WHERE CrewID = %s", [crew_id])
        messages.success(request, 'Crew member deleted successfully!')
    return redirect('crew_list')

# Maintenance
# Note: Technician, MaintenanceType models need to be added to models.py
# from .models import Technician, MaintenanceType

def maintenance_list(request):
    """List all maintenance records"""
    # Using raw SQL since MaintenanceRecord model doesn't exist in models.py yet
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.MaintenanceID, m.MaintenanceDate, m.Cost, m.NextDueDate, m.Description,
                   a.AircraftID, mt.MaintenanceType
            FROM MAINTENANCE_RECORD m
            JOIN AIRCRAFT a ON m.AircraftID = a.AircraftID
            JOIN MAINTENANCE_TYPE mt ON m.MaintenanceTypeID = mt.MaintenanceTypeID
        """)
        columns = [col[0] for col in cursor.description]
        maintenance = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return render(request, 'aviation/maintenance_list.html', {'maintenance': maintenance})

def add_maintenance(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO MAINTENANCE_RECORD (MaintenanceID, MaintenanceDate, Description,
                Cost, NextDueDate, TechnicianID, AircraftID, MaintenanceTypeID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                request.POST.get('maintenanceid'),
                request.POST.get('maintenancedate'),
                request.POST.get('description'),
                request.POST.get('cost'),
                request.POST.get('nextduedate'),
                request.POST.get('technicianid'),
                request.POST.get('aircraftid'),
                request.POST.get('maintenancetypeid'),
            ])
        messages.success(request, 'Maintenance record added successfully!')
        return redirect('maintenance_list')
    technicians = Technician.objects.all()
    aircraft = Aircraft.objects.all()
    maintenance_types = MaintenanceType.objects.all()
    return render(request, 'aviation/add_maintenance.html', {
        'technicians': technicians, 'aircraft': aircraft, 'maintenance_types': maintenance_types
    })

def edit_maintenance(request, maintenance_id):
    maintenance = get_object_or_404(MaintenanceRecord, maintenanceid=maintenance_id)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE MAINTENANCE_RECORD SET MaintenanceDate = %s, Description = %s, Cost = %s,
                NextDueDate = %s, TechnicianID = %s, AircraftID = %s, MaintenanceTypeID = %s
                WHERE MaintenanceID = %s
            """, [
                request.POST.get('maintenancedate'),
                request.POST.get('description'),
                request.POST.get('cost'),
                request.POST.get('nextduedate'),
                request.POST.get('technicianid'),
                request.POST.get('aircraftid'),
                request.POST.get('maintenancetypeid'),
                maintenance_id,
            ])
        messages.success(request, 'Maintenance record updated successfully!')
        return redirect('maintenance_list')
    technicians = Technician.objects.all()
    aircraft = Aircraft.objects.all()
    maintenance_types = MaintenanceType.objects.all()
    return render(request, 'aviation/edit_maintenance.html', {
        'maintenance': maintenance, 'technicians': technicians, 
        'aircraft': aircraft, 'maintenance_types': maintenance_types
    })

def delete_maintenance(request, maintenance_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM MAINTENANCE_RECORD WHERE MaintenanceID = %s", [maintenance_id])
        messages.success(request, 'Maintenance record deleted successfully!')
    return redirect('maintenance_list')

# Countries
def countries_list(request):
    """List all countries"""
    countries = Country.objects.all()
    return render(request, 'aviation/countries_list.html', {'countries': countries})

def add_country(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO COUNTRY (CountryCode, CountryName)
                VALUES (%s, %s)
            """, [
                request.POST.get('countrycode'),
                request.POST.get('countryname'),
            ])
        messages.success(request, 'Country added successfully!')
        return redirect('countries_list')
    return render(request, 'aviation/add_country.html')

def edit_country(request, country_code):
    country = get_object_or_404(Country, countrycode=country_code)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE COUNTRY SET CountryName = %s WHERE CountryCode = %s
            """, [
                request.POST.get('countryname'),
                country_code,
            ])
        messages.success(request, 'Country updated successfully!')
        return redirect('countries_list')
    return render(request, 'aviation/edit_country.html', {'country': country})

def delete_country(request, country_code):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM COUNTRY WHERE CountryCode = %s", [country_code])
        messages.success(request, 'Country deleted successfully!')
    return redirect('countries_list')
