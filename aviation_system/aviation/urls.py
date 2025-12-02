from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Flights
    path('flights/', views.flights_list, name='flights_list'),
    path('flights/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('flights/add/', views.add_flight, name='add_flight'),
    
    # Passengers
    path('passengers/', views.passengers_list, name='passengers_list'),
    path('passengers/<int:passenger_id>/', views.passenger_detail, name='passenger_detail'),
    path('passengers/add/', views.add_passenger, name='add_passenger'),
    
    # Bookings
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/add/', views.add_booking, name='add_booking'),
    
    # Airlines
    path('airlines/', views.airlines_list, name='airlines_list'),
    path('airlines/<int:airline_id>/', views.airline_detail, name='airline_detail'),
    
    # Airports
    path('airports/', views.airports_list, name='airports_list'),
    path('airports/<str:airport_code>/', views.airport_detail, name='airport_detail'),
    
    # Search
    path('search/', views.search_flights, name='search_flights'),
]