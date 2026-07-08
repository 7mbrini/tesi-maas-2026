# (C) 2025 Francesco Settembrini

from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

import string

# =============================================================================
# Genera una stringa alfanumerica per simulare la "targa" del veicolo
# =============================================================================
def generate_unique_code():
                                            # Restringo ai soli caratteri maiuscoli
                                            # per evitare confusioni, e.g.  I, l, 1, 0, O
    allowed_chars = string.ascii_uppercase + string.digits
    code_length = 6
                                            # Genera il codice e si assicura che sia unico
    while True:
        code = get_random_string(length=code_length, allowed_chars=allowed_chars)
        if not Transaction.objects.filter(check_code=code).exists():
            break
    return code

# =============================================================================
# Memorizza i dati per la transazione per il noleggio dell'auto
# =============================================================================
class Transaction(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_status = models.CharField(max_length=20, default='pending')  # e.g., 'pending', 'completed', 'failed'
    timestamp = models.DateTimeField(auto_now_add=True)

                                            # Codice univoco che l'utente digitera'
                                            # sul keypad del veicolo per "sbloccarlo"
    check_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_unique_code, # Use the function as the default generator
        editable=False, # Prevents the code from being edited in the admin interface
    )
                                            # simula la ricezione di un GUID
                                            # da un reale gateway di pagamento
    gateway_transaction_id = models.CharField(max_length=100, unique=True, null=True)

    def __str__(self):
        return f"Transaction {self.id} | Status: {self.transaction_status} | Amount: ${self.amount}"

