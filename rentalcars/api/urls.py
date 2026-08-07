# (C) 2026 Francesco Settembrini

from django.urls import path
from django.urls import re_path

from . import views


urlpatterns = [
    path('vehicles_get_all/', views.api_vehicles_get_all, name='api_vehicles_get_all'),
    path('vehicles_get_by_license_plate/<str:license_plate>/', views.api_vehicles_get_by_license_plate,
        name='api_vehicles_get_by_license_plate'),
    path('vehicles_get_by_seats/<int:seats>/', views.api_vehicles_get_by_seats,
        name='api_vehicles_get_by_seats'),
    path('vehicles_get_by_doors/<int:doors>/', views.api_vehicles_get_by_doors,
        name='api_vehicles_get_by_doors'),
    path('vehicles_get_by_range_km/<int:range>/', views.api_vehicles_get_by_range_km,
        name='api_vehicles_get_by_range'),
    re_path(r'vehicles_get_by_nearest_pos/(?P<latitude>[0-9.]+)/(?P<longitude>[0-9.]+)/(?P<radius>[0-9.]+)/$',
        views.api_vehicles_get_by_nearest_pos, name = 'api_vehicles_get_by_nearest_pos'),

    path('api_vehicle_unlock/', views.api_vehicle_unlock, name = 'api_vehcle_unlock'),
    path('api_vehicle_rent/', views.api_vehicle_rent, name = 'api_vehicle_rent'),
]


