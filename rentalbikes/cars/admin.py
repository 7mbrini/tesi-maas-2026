# (C) 2025 Francesco Settembrini

from django.contrib.gis import admin
from .models import Car

@admin.register(Car)
class CarAdmin(admin.GISModelAdmin):
    list_display = ('license_plate', 'seats', 'doors', 'hourly_rate', 'range_km', 'location')
    list_filter = ('doors', 'seats')
    search_fields = ('license_plate',)
