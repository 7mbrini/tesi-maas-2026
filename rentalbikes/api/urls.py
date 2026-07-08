# (C) 2025 Francesco Settembrini

from django.urls import path
from django.urls import re_path

from . import views

urlpatterns = [
    path('cars_get_all/', views.api_cars_get_all, name='api_cars_get_all'),
    path('cars_get_by_license_plate/<str:license_plate>/', views.api_cars_get_by_license_plate,
        name='api_cars_get_by_license_plate'),
    path('cars_get_by_seats/<int:seats>/', views.api_cars_get_by_seats,
        name='api_cars_get_by_seats'),
    path('cars_get_by_doors/<int:doors>/', views.api_cars_get_by_doors,
        name='api_cars_get_by_doors'),
    path('cars_get_by_range_km/<int:range>/', views.api_cars_get_by_range_km,
        name='api_cars_get_by_range'),
    re_path(r'cars_get_by_nearest_pos/(?P<latitude>[0-9.]+)/(?P<longitude>[0-9.]+)/(?P<radius>[0-9.]+)/$',
        views.api_cars_get_by_nearest_pos, name = 'api_cars_get_by_nearest_pos'),
]


