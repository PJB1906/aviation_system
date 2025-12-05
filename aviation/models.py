from django.db import models

class Country(models.Model):
    countrycode = models.IntegerField(db_column='CountryCode', primary_key=True)
    countryname = models.CharField(db_column='CountryName', max_length=100)
    
    class Meta:
        managed = False
        db_table = 'COUNTRY'
    
    def __str__(self):
        return self.countryname

class Currency(models.Model):
    currencycode = models.IntegerField(db_column='CurrencyCode', primary_key=True)
    currencyname = models.CharField(db_column='CurrencyName', max_length=50)
    currencysymbol = models.CharField(db_column='CurrencySymbol', max_length=3)
    
    class Meta:
        managed = False
        db_table = 'CURRENCY'
    
    def __str__(self):
        return f"{self.currencyname} ({self.currencysymbol})"

class City(models.Model):
    cityid = models.IntegerField(db_column='CityID', primary_key=True)
    cityname = models.CharField(db_column='CityName', max_length=100)
    countrycode = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='CountryCode')
    
    class Meta:
        managed = False
        db_table = 'CITY'
    
    def __str__(self):
        return self.cityname

class Airport(models.Model):
    airportcode = models.IntegerField(db_column='AirportCode', primary_key=True)
    airportname = models.CharField(db_column='AirportName', max_length=150)
    latitude = models.DecimalField(db_column='Latitude', max_digits=10, decimal_places=6)
    longitude = models.DecimalField(db_column='Longitude', max_digits=10, decimal_places=6)
    timezone = models.CharField(db_column='Timezone', max_length=50)
    cityid = models.ForeignKey(City, on_delete=models.CASCADE, db_column='CityID')
    
    class Meta:
        managed = False
        db_table = 'AIRPORT'
    
    def __str__(self):
        return self.airportname

class Alliance(models.Model):
    allianceid = models.IntegerField(db_column='AllianceID', primary_key=True)
    alliancename = models.CharField(db_column='AllianceName', max_length=100)
    allianceheadquarters = models.ForeignKey(City, on_delete=models.CASCADE, db_column='AllianceHeadquarters')
    
    class Meta:
        managed = False
        db_table = 'ALLIANCE'
    
    def __str__(self):
        return self.alliancename

class Airline(models.Model):
    airlineid = models.IntegerField(db_column='AirlineID', primary_key=True)
    airlinename = models.CharField(db_column='AirlineName', max_length=100)
    airlineicao = models.CharField(db_column='AirlineICAO', max_length=10)
    headquarterscityid = models.ForeignKey(City, on_delete=models.CASCADE, db_column='HeadquartersCityID')
    foundedyear = models.IntegerField(db_column='FoundedYear')
    allianceid = models.ForeignKey(Alliance, on_delete=models.CASCADE, db_column='AllianceID')
    
    class Meta:
        managed = False
        db_table = 'AIRLINE'
    
    def __str__(self):
        return self.airlinename

class AircraftType(models.Model):
    aircrafttypecode = models.IntegerField(db_column='AircraftTypeCode', primary_key=True)
    typename = models.CharField(db_column='TypeName', max_length=100)
    maxpassengers = models.IntegerField(db_column='MaxPassengers')
    maintenancetypeid = models.IntegerField(db_column='MaintenanceTypeID')
    
    class Meta:
        managed = False
        db_table = 'AIRCRAFT_TYPE'
    
    def __str__(self):
        return self.typename

class Aircraft(models.Model):
    aircraftid = models.IntegerField(db_column='AircraftID', primary_key=True)
    manufactureyear = models.IntegerField(db_column='ManufactureYear')
    lastmaintenancedate = models.DateField(db_column='LastMaintenanceDate')
    airlineid = models.ForeignKey(Airline, on_delete=models.CASCADE, db_column='AirlineID')
    aircrafttypecode = models.ForeignKey(AircraftType, on_delete=models.CASCADE, db_column='AircraftTypeCode')
    
    class Meta:
        managed = False
        db_table = 'AIRCRAFT'
    
    def __str__(self):
        return f"Aircraft {self.aircraftid} - {self.aircrafttypecode}"

class Terminal(models.Model):
    terminalid = models.IntegerField(db_column='TerminalID', primary_key=True)
    terminalname = models.CharField(db_column='TerminalName', max_length=50)
    isinternational = models.BooleanField(db_column='IsInternational')
    airportcode = models.ForeignKey(Airport, on_delete=models.CASCADE, db_column='AirportCode')
    
    class Meta:
        managed = False
        db_table = 'TERMINAL'
    
    def __str__(self):
        return f"{self.terminalname} - {self.airportcode}"

class Gate(models.Model):
    gatenumber = models.IntegerField(db_column='GateNumber', primary_key=True)
    gatetype = models.IntegerField(db_column='GateType')
    isactive = models.BooleanField(db_column='IsActive')
    airportcode = models.ForeignKey(Airport, on_delete=models.CASCADE, db_column='AirportCode')
    terminalid = models.ForeignKey(Terminal, on_delete=models.CASCADE, db_column='TerminalID')
    
    class Meta:
        managed = False
        db_table = 'GATE'
        unique_together = (('gatenumber', 'terminalid'),)
    
    def __str__(self):
        return f"Gate {self.gatenumber}"

class Flight(models.Model):
    flightid = models.IntegerField(db_column='FlightID', primary_key=True)
    flightnumber = models.CharField(db_column='FlightNumber', max_length=20)
    scheduleddeparture = models.DateTimeField(db_column='ScheduledDeparture')
    scheduledarrival = models.DateTimeField(db_column='ScheduledArrival')
    actualdeparture = models.DateTimeField(db_column='ActualDeparture', null=True, blank=True)
    actualarrival = models.DateTimeField(db_column='ActualArrival', null=True, blank=True)
    flightstatus = models.CharField(db_column='FlightStatus', max_length=20)
    airlineid = models.ForeignKey(Airline, on_delete=models.CASCADE, db_column='AirlineID')
    aircraftid = models.ForeignKey(Aircraft, on_delete=models.CASCADE, db_column='AircraftID')
    departureairportcode = models.ForeignKey(Airport, on_delete=models.CASCADE, db_column='DepartureAirportCode', related_name='departures')
    arrivalairportcode = models.ForeignKey(Airport, on_delete=models.CASCADE, db_column='ArrivalAirportCode', related_name='arrivals')
    departureterminalid = models.ForeignKey(Terminal, on_delete=models.CASCADE, db_column='DepartureTerminalID', related_name='dep_terminal')
    arrivalterminalid = models.ForeignKey(Terminal, on_delete=models.CASCADE, db_column='ArrivalTerminalID', related_name='arr_terminal')
    departuregatenumber = models.IntegerField(db_column='DepartureGateNumber')
    arrivalgatenumber = models.IntegerField(db_column='ArrivalGateNumber')
    
    class Meta:
        managed = False
        db_table = 'FLIGHT'
    
    def __str__(self):
        return f"{self.flightnumber} - {self.flightstatus}"

class Passenger(models.Model):
    passengerid = models.IntegerField(db_column='PassengerID', primary_key=True)
    firstname = models.CharField(db_column='FirstName', max_length=50)
    lastname = models.CharField(db_column='LastName', max_length=50)
    email = models.CharField(db_column='Email', max_length=100)
    phone = models.CharField(db_column='Phone', max_length=20)
    dateofbirth = models.DateField(db_column='DateOfBirth')
    passportnumber = models.CharField(db_column='PassportNumber', max_length=50, unique=True)
    countrycode = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='CountryCode')
    nationality = models.CharField(db_column='Nationality', max_length=50)
    
    class Meta:
        managed = False
        db_table = 'PASSENGER'
    
    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class SeatClass(models.Model):
    seatclass = models.IntegerField(db_column='SeatClass', primary_key=True)
    basefare = models.IntegerField(db_column='BaseFare')
    baggageallowance = models.IntegerField(db_column='BaggageAllowance')
    
    class Meta:
        managed = False
        db_table = 'SEAT_CLASS'
    
    def __str__(self):
        return f"Class {self.seatclass}"

class Booking(models.Model):
    bookingid = models.IntegerField(db_column='BookingID', primary_key=True)
    bookingdate = models.DateTimeField(db_column='BookingDate')
    totalamount = models.DecimalField(db_column='TotalAmount', max_digits=10, decimal_places=2)
    bookingstatus = models.CharField(db_column='BookingStatus', max_length=20)
    bookingchannel = models.CharField(db_column='BookingChannel', max_length=20)
    passengerid = models.ForeignKey(Passenger, on_delete=models.CASCADE, db_column='PassengerID')
    currencycode = models.ForeignKey(Currency, on_delete=models.CASCADE, db_column='CurrencyCode')
    
    class Meta:
        managed = False
        db_table = 'BOOKING'
    
    def __str__(self):
        return f"Booking {self.bookingid} - {self.bookingstatus}"

class Ticket(models.Model):
    ticketid = models.IntegerField(db_column='TicketID', primary_key=True)
    seatnumber = models.CharField(db_column='SeatNumber', max_length=10)
    ticketstatus = models.CharField(db_column='TicketStatus', max_length=20)
    checkedina = models.DateTimeField(db_column='CheckedInAt', null=True, blank=True)
    bookingid = models.ForeignKey(Booking, on_delete=models.CASCADE, db_column='BookingID')
    flightid = models.ForeignKey(Flight, on_delete=models.CASCADE, db_column='FlightID')
    seatclass = models.ForeignKey(SeatClass, on_delete=models.CASCADE, db_column='SeatClass')
    passengerid = models.ForeignKey(Passenger, on_delete=models.CASCADE, db_column='PassengerID')
    
    class Meta:
        managed = False
        db_table = 'TICKET'
    
    def __str__(self):
        return f"Ticket {self.ticketid} - Seat {self.seatnumber}"

class Route(models.Model):
    routeid = models.IntegerField(db_column='RouteID', primary_key=True)
    distancekm = models.IntegerField(db_column='DistanceKM')
    estimateddurationmins = models.IntegerField(db_column='EstimatedDurationMins')
    routetype = models.IntegerField(db_column='RouteType')
    originairportcode = models.ForeignKey(Airport, on_delete=models.CASCADE, db_column='OriginAirportCode', related_name='origin_routes')
    destinationairportcode = models.ForeignKey(Airport, on_delete=models.CASCADE, db_column='DestinationAirportCode', related_name='destination_routes')
    
    class Meta:
        managed = False
        db_table = 'ROUTE'
    
    def __str__(self):
        return f"Route {self.routeid}"

class CrewMember(models.Model):
    crewid = models.IntegerField(db_column='CrewID', primary_key=True)
    firstname = models.CharField(db_column='FirstName', max_length=50)
    lastname = models.CharField(db_column='LastName', max_length=50)
    dateofbirth = models.DateField(db_column='DateOfBirth')
    hiredate = models.DateField(db_column='HireDate')
    crewtype = models.IntegerField(db_column='CrewType')
    airlineid = models.ForeignKey(Airline, on_delete=models.CASCADE, db_column='AirlineID')
    airportcode = models.ForeignKey(Airport, on_delete=models.CASCADE, db_column='AirportCode')
    
    class Meta:
        managed = False
        db_table = 'CREW_MEMBER'
    
    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class MaintenanceType(models.Model):
    maintenancetypeid = models.IntegerField(db_column='MaintenanceTypeID', primary_key=True)
    maintenancetype = models.CharField(db_column='MaintenanceType', max_length=100)
    
    class Meta:
        managed = False
        db_table = 'MAINTENANCE_TYPE'
    
    def __str__(self):
        return self.maintenancetype

class Technician(models.Model):
    technicianid = models.IntegerField(db_column='TechnicianID', primary_key=True)
    licensenumber = models.CharField(db_column='LicenseNumber', max_length=50)
    licenseexpiry = models.DateField(db_column='LicenseExpiry')
    crewid = models.ForeignKey(CrewMember, on_delete=models.CASCADE, db_column='CrewID')
    
    class Meta:
        managed = False
        db_table = 'TECHNICIAN'
    
    def __str__(self):
        return f"Technician {self.technicianid}"

class MaintenanceRecord(models.Model):
    maintenanceid = models.IntegerField(db_column='MaintenanceID', primary_key=True)
    maintenancedate = models.DateField(db_column='MaintenanceDate')
    description = models.TextField(db_column='Description')
    cost = models.DecimalField(db_column='Cost', max_digits=10, decimal_places=2)
    nextduedate = models.DateField(db_column='NextDueDate')
    technicianid = models.ForeignKey(Technician, on_delete=models.CASCADE, db_column='TechnicianID')
    aircraftid = models.ForeignKey(Aircraft, on_delete=models.CASCADE, db_column='AircraftID')
    maintenancetypeid = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE, db_column='MaintenanceTypeID')
    
    class Meta:
        managed = False
        db_table = 'MAINTENANCE_RECORD'
    
    def __str__(self):
        return f"Maintenance {self.maintenanceid}"

