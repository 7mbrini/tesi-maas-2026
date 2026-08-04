# (C) 2026 Francesco Settembrini

from django.db import models
from django.contrib.auth.models import User
from rentals.models import Rental  # Importa il noleggio correlato


class PaymentTransaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    # Il pagamento punta al noleggio di riferimento
    rental = models.ForeignKey(
        Rental,
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    # GUID simulato del gateway esterno (es. Stripe)
    gateway_transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Tx {self.id} | Rental: {self.rental.id} | Amount: €{self.amount} | Status: {self.status}"
