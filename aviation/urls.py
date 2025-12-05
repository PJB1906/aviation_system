from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Home
    path('', views.home, name='home'),
    
    # Flights
    path('flights/', views.flights_list, name='flights_list'),
    path('flights/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('flights/add/', views.add_flight, name='add_flight'),
    path('flights/<int:flight_id>/edit/', views.edit_flight, name='edit_flight'),
    path('flights/<int:flight_id>/delete/', views.delete_flight, name='delete_flight'),
    
    # Passengers
    path('passengers/', views.passengers_list, name='passengers_list'),
    path('passengers/<int:passenger_id>/', views.passenger_detail, name='passenger_detail'),
    path('passengers/add/', views.add_passenger, name='add_passenger'),
    path('passengers/<int:passenger_id>/edit/', views.edit_passenger, name='edit_passenger'),
    path('passengers/<int:passenger_id>/delete/', views.delete_passenger, name='delete_passenger'),
    
    # Bookings
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/add/', views.add_booking, name='add_booking'),
    path('bookings/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('bookings/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    
    # Airlines
    path('airlines/', views.airlines_list, name='airlines_list'),
    path('airlines/<int:airline_id>/', views.airline_detail, name='airline_detail'),
    path('airlines/add/', views.add_airline, name='add_airline'),
    path('airlines/<int:airline_id>/edit/', views.edit_airline, name='edit_airline'),
    path('airlines/<int:airline_id>/delete/', views.delete_airline, name='delete_airline'),
    
    # Airports
    path('airports/', views.airports_list, name='airports_list'),
    path('airports/<int:airport_code>/', views.airport_detail, name='airport_detail'),
    path('airports/add/', views.add_airport, name='add_airport'),
    path('airports/<int:airport_code>/edit/', views.edit_airport, name='edit_airport'),
    path('airports/<int:airport_code>/delete/', views.delete_airport, name='delete_airport'),
    
    # Aircraft
    path('aircraft/', views.aircraft_list, name='aircraft_list'),
    path('aircraft/add/', views.add_aircraft, name='add_aircraft'),
    path('aircraft/<int:aircraft_id>/edit/', views.edit_aircraft, name='edit_aircraft'),
    path('aircraft/<int:aircraft_id>/delete/', views.delete_aircraft, name='delete_aircraft'),
    
    # Routes
    path('routes/', views.routes_list, name='routes_list'),
    path('routes/add/', views.add_route, name='add_route'),
    path('routes/<int:route_id>/edit/', views.edit_route, name='edit_route'),
    path('routes/<int:route_id>/delete/', views.delete_route, name='delete_route'),
    
    # Crew
    path('crew/', views.crew_list, name='crew_list'),
    path('crew/add/', views.add_crew, name='add_crew'),
    path('crew/<int:crew_id>/edit/', views.edit_crew, name='edit_crew'),
    path('crew/<int:crew_id>/delete/', views.delete_crew, name='delete_crew'),
    
    # Maintenance
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/add/', views.add_maintenance, name='add_maintenance'),
    path('maintenance/<int:maintenance_id>/edit/', views.edit_maintenance, name='edit_maintenance'),
    path('maintenance/<int:maintenance_id>/delete/', views.delete_maintenance, name='delete_maintenance'),
    
    # Countries
    path('countries/', views.countries_list, name='countries_list'),
    path('countries/add/', views.add_country, name='add_country'),
    path('countries/<int:country_code>/edit/', views.edit_country, name='edit_country'),
    path('countries/<int:country_code>/delete/', views.delete_country, name='delete_country'),
    
    # Search
    path('search/', views.search_flights, name='search_flights'),
]