# (C) 2026 Francesco Settembrini

from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import re
from django.core.exceptions import ValidationError


def validate_license_plate(value):
    if not re.fullmatch(r'[A-Za-z0-9]{6}', value):
        raise ValidationError('License plate must be exactly 6 alphanumeric characters.', code='invalid_license_plate')

class Car(models.Model):
    # La soglia minima di batteria tollerata è definita SOLO QUI
    MIN_BATTERY_LEVEL = 10

    license_plate = models.CharField(max_length=8, unique=True, validators=[validate_license_plate])
    seats = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(6)])
    unlock_cost = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, validators=[MinValueValidator(0)])
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    DOOR_CHOICES = [(3, '3 Doors'), (5, '5 Doors')]
    doors = models.IntegerField(choices=DOOR_CHOICES)
    image = models.ImageField(upload_to='car_images/', null=True, blank=True)
    range_km = models.IntegerField(validators=[MinValueValidator(0)])
    battery_percentage = models.PositiveIntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_available = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=True)
    location = models.PointField(srid=4326)

    # @property
    # def available_range_km(self):
    #     # Calcola l'autonomia chilometrica rimasta moltiplicando range_km per la percentuale
    #     return (self.range_km * self.battery_percentage) / 100.0

    @property
    def available_range_km(self):
        # Controllo di sicurezza: se i campi sono assenti, restituisce 0
        if self.range_km is None or self.battery_percentage is None:
            return 0

        # Calcolo con cast esplicito a intero (arrotonda per difetto)
        return int((self.range_km * self.battery_percentage) / 100)


    @property
    def is_usable(self):
        # L'auto è usabile SOLO SE ha batteria > 10%
        return self.battery_percentage > MIN_BATTERY_LEVEL

    def __str__(self):
        return self.license_plate
