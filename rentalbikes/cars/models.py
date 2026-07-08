# (C) 2025 Francesco Settembrini

from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import re
from django.core.exceptions import ValidationError


def validate_license_plate(value):
    if not re.fullmatch(r'[A-Za-z0-9]{6}', value):
        raise ValidationError('License plate must be exactly 6 alphanumeric characters.', code='invalid_license_plate')

class Car(models.Model):
    license_plate = models.CharField(max_length=6, unique=True, validators=[validate_license_plate])
    seats = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(6)])
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    DOOR_CHOICES = [(3, '3 Doors'), (5, '5 Doors')]
    doors = models.IntegerField(choices=DOOR_CHOICES)
    image = models.ImageField(upload_to='car_images/', null=True, blank=True)
    range_km = models.IntegerField(validators=[MinValueValidator(0)])
    available = models.BooleanField(default=True)
    location = models.PointField(srid=4326)

    def __str__(self):
        return self.license_plate
