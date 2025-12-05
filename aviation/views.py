from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from .models import (Flight, Passenger, Booking, Airline, Airport, 
                     Aircraft, Country, Ticket, AircraftType, Currency, Alliance, City,
                     Route, CrewMember, MaintenanceType, MaintenanceRecord, Technician)
from .forms import FlightForm, PassengerForm, BookingForm

# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'aviation/login.html')

def signup_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'aviation/signup.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'aviation/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'aviation/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'aviation/signup.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')
    
    return render(request, 'aviation/signup.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# ============================================================================
# DASHBOARD HOME
# ============================================================================

@login_required
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

@login_required
def flights_list(request):
    """List all flights"""
    flights = Flight.objects.select_related(
        'airlineid', 'departureairportcode', 'arrivalairportcode'
    ).all()
    return render(request, 'aviation/flights_list.html', {'flights': flights})

@login_required
def flight_detail(request, flight_id):
    """View details of a specific flight"""
    flight = get_object_or_404(Flight, flightid=flight_id)
    tickets = Ticket.objects.filter(flightid=flight_id).select_related('passengerid')
    
    context = {
        'flight': flight,
        'tickets': tickets,
    }
    return render(request, 'aviation/flight_detail.html', context)

@login_required
def add_flight(request):
    """Add a new flight"""
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            try:
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
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle foreign key constraint errors with specific messages
                if 'foreign key constraint' in error_msg:
                    if 'arrivalgate' in error_msg or 'flight_ibfk_8' in error_msg:
                        messages.error(request, 'Invalid arrival gate. The selected gate number does not exist for the arrival terminal. Please verify the gate and terminal combination.')
                    elif 'departuregate' in error_msg or 'flight_ibfk_7' in error_msg:
                        messages.error(request, 'Invalid departure gate. The selected gate number does not exist for the departure terminal. Please verify the gate and terminal combination.')
                    elif 'airline' in error_msg:
                        messages.error(request, 'Invalid airline selected. Please choose a valid airline from the list.')
                    elif 'aircraft' in error_msg:
                        messages.error(request, 'Invalid aircraft selected. Please choose a valid aircraft from the list.')
                    elif 'airport' in error_msg:
                        messages.error(request, 'Invalid airport selected. Please choose valid departure and arrival airports.')
                    else:
                        messages.error(request, 'Cannot add flight due to invalid reference data. Please check all selected values (gates, terminals, airline, aircraft, airports).')
                elif 'duplicate' in error_msg or 'unique' in error_msg:
                    messages.error(request, 'A flight with this ID already exists. Please use a different Flight ID.')
                else:
                    messages.error(request, f'Error adding flight: {str(e)}')
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

@login_required
def edit_flight(request, flight_id):
    """Edit an existing flight"""
    flight = get_object_or_404(Flight, flightid=flight_id)
    
    if request.method == 'POST':
        try:
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
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle foreign key constraint errors with specific messages
            if 'foreign key constraint' in error_msg:
                if 'arrivalgate' in error_msg or 'flight_ibfk_8' in error_msg:
                    messages.error(request, 'Invalid arrival gate. The selected gate number does not exist for the arrival terminal. Please verify the gate and terminal combination.')
                elif 'departuregate' in error_msg or 'flight_ibfk_7' in error_msg:
                    messages.error(request, 'Invalid departure gate. The selected gate number does not exist for the departure terminal. Please verify the gate and terminal combination.')
                elif 'airline' in error_msg:
                    messages.error(request, 'Invalid airline selected. Please choose a valid airline from the list.')
                elif 'aircraft' in error_msg:
                    messages.error(request, 'Invalid aircraft selected. Please choose a valid aircraft from the list.')
                elif 'airport' in error_msg:
                    messages.error(request, 'Invalid airport selected. Please choose valid departure and arrival airports.')
                else:
                    messages.error(request, 'Cannot update flight due to invalid reference data. Please check all selected values (gates, terminals, airline, aircraft, airports).')
            else:
                messages.error(request, f'Error updating flight: {str(e)}')
            
            # Return to the edit form with the error message
            # Don't redirect, so user can see their input and fix it
    
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

@login_required
def delete_flight(request, flight_id):
    """Delete a flight"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM FLIGHT WHERE FlightID = %s", [flight_id])
            messages.success(request, 'Flight deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this flight because it has associated tickets or other records. Please delete those first.')
            else:
                messages.error(request, f'Error deleting flight: {str(e)}')
    return redirect('flights_list')

# ============================================================================
# PASSENGER VIEWS
# ============================================================================

@login_required
def passengers_list(request):
    """List all passengers"""
    passengers = Passenger.objects.select_related('countrycode').all()
    return render(request, 'aviation/passengers_list.html', {'passengers': passengers})

@login_required
def passenger_detail(request, passenger_id):
    """View details of a specific passenger"""
    passenger = get_object_or_404(Passenger, passengerid=passenger_id)
    bookings = Booking.objects.filter(passengerid=passenger_id)
    
    context = {
        'passenger': passenger,
        'bookings': bookings,
    }
    return render(request, 'aviation/passenger_detail.html', context)

@login_required
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

@login_required
def bookings_list(request):
    """List all bookings"""
    bookings = Booking.objects.select_related('passengerid', 'currencycode').all()
    return render(request, 'aviation/bookings_list.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    """View details of a specific booking"""
    booking = get_object_or_404(Booking, bookingid=booking_id)
    tickets = Ticket.objects.filter(bookingid=booking_id).select_related('flightid')
    
    context = {
        'booking': booking,
        'tickets': tickets,
    }
    return render(request, 'aviation/booking_detail.html', context)

@login_required
def add_booking(request):
    """Add a new booking"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
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
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle foreign key constraint errors with specific messages
                if 'foreign key constraint' in error_msg:
                    if 'passenger' in error_msg:
                        messages.error(request, 'Invalid passenger selected. Please choose a valid passenger from the list.')
                    elif 'currency' in error_msg:
                        messages.error(request, 'Invalid currency selected. Please choose a valid currency from the list.')
                    else:
                        messages.error(request, 'Cannot add booking due to invalid reference data. Please check the passenger and currency selections.')
                elif 'duplicate' in error_msg or 'unique' in error_msg:
                    messages.error(request, 'A booking with this ID already exists. Please use a different Booking ID.')
                else:
                    messages.error(request, f'Error adding booking: {str(e)}')
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

@login_required
def airlines_list(request):
    """List all airlines"""
    airlines = Airline.objects.select_related('headquarterscityid', 'allianceid').all()
    return render(request, 'aviation/airlines_list.html', {'airlines': airlines})

@login_required
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

@login_required
def airports_list(request):
    """List all airports"""
    airports = Airport.objects.select_related('cityid').all()
    return render(request, 'aviation/airports_list.html', {'airports': airports})

@login_required
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
# PASSENGER EDIT/DELETE
# ============================================================================

@login_required
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

@login_required
def delete_passenger(request, passenger_id):
    """Delete a passenger"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM PASSENGER WHERE PassengerID = %s", [passenger_id])
            messages.success(request, 'Passenger deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this passenger because they have associated bookings or tickets. Please delete those first.')
            else:
                messages.error(request, f'Error deleting passenger: {str(e)}')
    return redirect('passengers_list')

# ============================================================================
# BOOKING EDIT/DELETE
# ============================================================================

@login_required
def edit_booking(request, booking_id):
    """Edit an existing booking"""
    booking = get_object_or_404(Booking, bookingid=booking_id)
    
    if request.method == 'POST':
        try:
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
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle foreign key constraint errors with specific messages
            if 'foreign key constraint' in error_msg:
                if 'passenger' in error_msg:
                    messages.error(request, 'Invalid passenger selected. Please choose a valid passenger from the list.')
                elif 'currency' in error_msg:
                    messages.error(request, 'Invalid currency selected. Please choose a valid currency from the list.')
                else:
                    messages.error(request, 'Cannot update booking due to invalid reference data. Please check the passenger and currency selections.')
            else:
                messages.error(request, f'Error updating booking: {str(e)}')
    
    passengers = Passenger.objects.all()
    currencies = Currency.objects.all()
    context = {
        'booking': booking,
        'passengers': passengers,
        'currencies': currencies,
    }
    return render(request, 'aviation/edit_booking.html', context)

@login_required
def delete_booking(request, booking_id):
    """Delete a booking"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM BOOKING WHERE BookingID = %s", [booking_id])
            messages.success(request, 'Booking deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this booking because it has associated tickets. Please delete those first.')
            else:
                messages.error(request, f'Error deleting booking: {str(e)}')
    return redirect('bookings_list')

# ============================================================================
# AIRLINE CRUD
# ============================================================================

@login_required
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

@login_required
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

@login_required
def delete_airline(request, airline_id):
    """Delete an airline"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM AIRLINE WHERE AirlineID = %s", [airline_id])
            messages.success(request, 'Airline deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this airline because it has associated flights, aircraft, or crew members. Please delete those first.')
            else:
                messages.error(request, f'Error deleting airline: {str(e)}')
    return redirect('airlines_list')

# ============================================================================
# AIRPORT CRUD
# ============================================================================

@login_required
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

@login_required
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

@login_required
def delete_airport(request, airport_code):
    """Delete an airport"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM AIRPORT WHERE AirportCode = %s", [airport_code])
            messages.success(request, 'Airport deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this airport because it has associated flights, routes, or crew members. Please delete those first.')
            else:
                messages.error(request, f'Error deleting airport: {str(e)}')
    return redirect('airports_list')

# ============================================================================
# AIRCRAFT, ROUTES, CREW, MAINTENANCE, COUNTRIES - STUB VIEWS
# ============================================================================

# Note: Route, CrewMember, MaintenanceRecord models need to be added to models.py
# from .models import Route, CrewMember, MaintenanceRecord, AircraftType

@login_required
def aircraft_list(request):
    """List all aircraft"""
    aircraft = Aircraft.objects.select_related('airlineid', 'aircrafttypecode').all()
    return render(request, 'aviation/aircraft_list.html', {'aircraft': aircraft})

@login_required
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

@login_required
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

@login_required
def delete_aircraft(request, aircraft_id):
    """Delete aircraft"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM AIRCRAFT WHERE AircraftID = %s", [aircraft_id])
            messages.success(request, 'Aircraft deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this aircraft because it has associated flights or maintenance records. Please delete those first.')
            else:
                messages.error(request, f'Error deleting aircraft: {str(e)}')
    return redirect('aircraft_list')

# Routes
@login_required
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

@login_required
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

@login_required
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

@login_required
def delete_route(request, route_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ROUTE WHERE RouteID = %s", [route_id])
            messages.success(request, 'Route deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this route because it has associated flights. Please delete those first.')
            else:
                messages.error(request, f'Error deleting route: {str(e)}')
    return redirect('routes_list')

# Crew
@login_required
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

@login_required
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

@login_required
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

@login_required
def delete_crew(request, crew_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM CREW_MEMBER WHERE CrewID = %s", [crew_id])
            messages.success(request, 'Crew member deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this crew member because they are assigned to flights. Please remove those assignments first.')
            else:
                messages.error(request, f'Error deleting crew member: {str(e)}')
    return redirect('crew_list')

# Maintenance
# Note: Technician, MaintenanceType models need to be added to models.py
# from .models import Technician, MaintenanceType

@login_required
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

@login_required
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

@login_required
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

@login_required
def delete_maintenance(request, maintenance_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM MAINTENANCE_RECORD WHERE MaintenanceID = %s", [maintenance_id])
            messages.success(request, 'Maintenance record deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this maintenance record due to database constraints.')
            else:
                messages.error(request, f'Error deleting maintenance record: {str(e)}')
    return redirect('maintenance_list')

# Countries
@login_required
def countries_list(request):
    """List all countries"""
    countries = Country.objects.all()
    return render(request, 'aviation/countries_list.html', {'countries': countries})

@login_required
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

@login_required
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

@login_required
def delete_country(request, country_code):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM COUNTRY WHERE CountryCode = %s", [country_code])
            messages.success(request, 'Country deleted successfully!')
        except Exception as e:
            if 'foreign key constraint' in str(e).lower():
                messages.error(request, 'Cannot delete this country because it has associated cities, passengers, or other records. Please delete those first.')
            else:
                messages.error(request, f'Error deleting country: {str(e)}')
    return redirect('countries_list')

# ============================================================================
# SEARCH FUNCTIONALITY
# ============================================================================

@login_required
def search_flights(request):
    """Search for flights by flight number, airline, or airport"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search in flights
        flights = Flight.objects.filter(
            flightnumber__icontains=query
        ).select_related('airlineid', 'departureairportcode', 'arrivalairportcode')[:10]
        
        for flight in flights:
            results.append({
                'type': 'Flight',
                'title': f'Flight {flight.flightnumber}',
                'subtitle': f'{flight.airlineid.airlinename} - {flight.departureairportcode.airportname} to {flight.arrivalairportcode.airportname}',
                'url': f'/flights/{flight.flightid}/',
                'status': flight.flightstatus
            })
        
        # Search in airlines
        airlines = Airline.objects.filter(airlinename__icontains=query)[:5]
        for airline in airlines:
            results.append({
                'type': 'Airline',
                'title': airline.airlinename,
                'subtitle': f'ICAO: {airline.airlineicao}',
                'url': f'/airlines/{airline.airlineid}/',
                'status': None
            })
        
        # Search in airports
        airports = Airport.objects.filter(airportname__icontains=query)[:5]
        for airport in airports:
            results.append({
                'type': 'Airport',
                'title': airport.airportname,
                'subtitle': f'{airport.cityid.cityname}, {airport.cityid.countrycode.countryname}',
                'url': f'/airports/{airport.airportcode}/',
                'status': None
            })
        
        # Search in passengers
        passengers = Passenger.objects.filter(
            firstname__icontains=query
        ) | Passenger.objects.filter(
            lastname__icontains=query
        )
        passengers = passengers[:5]
        
        for passenger in passengers:
            results.append({
                'type': 'Passenger',
                'title': f'{passenger.firstname} {passenger.lastname}',
                'subtitle': f'Email: {passenger.email}',
                'url': f'/passengers/{passenger.passengerid}/',
                'status': None
            })
    
    context = {
        'query': query,
        'results': results,
        'result_count': len(results)
    }
    return render(request, 'aviation/search_results.html', context)
