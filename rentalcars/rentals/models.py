# (C) 2026 Francesco Settembrini

from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import string

from vehicles.models import Vehicle


# =============================================================================
def generate_unique_code():
    allowed_chars = string.ascii_uppercase + string.digits
    code_length = 6

    from django.apps import apps
    RentalModel = apps.get_model('rentals', 'Rental')

    while True:
        code = get_random_string(length=code_length, allowed_chars=allowed_chars)
        if not RentalModel.objects.filter(check_code=code).exists():
            break
    return code


# =============================================================================
class Rental(models.Model):
    STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('active', 'Active / Unlocked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reserved')

    timestamp = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=timezone.now, null=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    actual_end_time = models.DateTimeField(null=True, blank=True)

    # Codice keypad per sblocco hardware
    check_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_unique_code,
        editable=False,
    )

    class Meta:
        ordering = ['-start_time']

    # --- PROPRIETÀ CALCOLATE A RUNTIME ---

    @property
    def end_time(self):
        # Scadenza teorica calcolata a runtime in RAM
        if self.start_time:
            return self.start_time + timedelta(minutes=self.duration_minutes)
        return None

    @property
    def is_expired(self):
        # Verifica scadenza a runtime
        if self.actual_end_time:
            return timezone.now() > self.actual_end_time
        if self.end_time:
            return timezone.now() > self.end_time
        return False

    def __str__(self):
        return f"Rental {self.id} | Vehicle: {self.vehicle.license_plate if self.vehicle else 'None'} | Status: {self.status}"
