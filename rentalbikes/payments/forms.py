# (C) 2025 Francesco Settembrini

from django import forms
from django.core.validators import MinValueValidator

class PaymentInitiateForm(forms.Form):
                        # Field per definire la durata minima del noleggi
                        # default a 30 minuti
    rental_duration_minutes = forms.IntegerField(
        label='Rental Duration (minutes)',
        initial=30,
        validators=[MinValueValidator(30)],
        widget=forms.NumberInput(attrs={'min': '30'})
    )

class PaymentPayForm(forms.Form):
    card_number = forms.CharField(max_length=16, min_length=16, label="Card Number")
    expiry_date = forms.CharField(max_length=5, label="Expiry Date (MM/YY)")
    cvc = forms.CharField(max_length=3, min_length=3, label="CVC")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=10.00,
        disabled = True, label="Amount \u20AC")

