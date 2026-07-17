# (C) 2026 Francesco Settembrini

from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone

import string

from cars.models import Car

# # =============================================================================
# # Genera una stringa alfanumerica per simulare la "targa" del veicolo
# # =============================================================================
# def generate_unique_code():
#                                             # Restringo ai soli caratteri maiuscoli
#                                             # per evitare confusioni, e.g.  I, l, 1, 0, O
#     allowed_chars = string.ascii_uppercase + string.digits
#     code_length = 6
#                                             # Genera il codice e si assicura che sia unico
#     while True:
#         code = get_random_string(length=code_length, allowed_chars=allowed_chars)
#         if not Rentals.objects.filter(check_code=code).exists():
#             break
#     return code
#

# =============================================================================
# Genera una stringa alfanumerica per simulare la "targa" del veicolo
# =============================================================================
def generate_unique_code():
    allowed_chars = string.ascii_uppercase + string.digits
    code_length = 6

    # Recuperiamo il modello dinamicamente per evitare il NameError
    from django.apps import apps
    RentalModel = apps.get_model('payments', 'Rental')

    while True:
        code = get_random_string(length=code_length, allowed_chars=allowed_chars)
        if not RentalModel.objects.filter(check_code=code).exists():
            break
    return code


# class Rental(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     vehicle = models.ForeignKey(ElectricVehicle, on_models=models.CASCADE)
#     booking_reference = models.CharField(max_length=12, unique=True)
#     is_paid = models.BooleanField(default=False)
#     start_time = models.DateTimeField(auto_now_add=True)


# =============================================================================
# Memorizza i dati per la transazione per il noleggio dell'auto
# =============================================================================
class Rental(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_status = models.CharField(max_length=20, default='pending')  # e.g., 'pending', 'completed', 'failed'
    timestamp = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    start_time = models.DateTimeField(default=timezone.now, null=True);

                                            # Codice che l'utente dovra' digitare
                                            # sul keypad del veicolo per "sbloccarlo"
    check_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_unique_code,
        editable=False, # Previene l'editing del codiice nell'interfaccia admin
    )
                                            # per simulare la ricezione di un GUID
                                            # da un reale gateway di pagamento
    gateway_transaction_id = models.CharField(max_length=100, unique=True, null=True)

    def __str__(self):
        return f"Rental {self.id} | Status: {self.transaction_status} | Amount: ${self.amount}"

