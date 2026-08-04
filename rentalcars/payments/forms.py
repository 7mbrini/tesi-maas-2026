# (C) 2026 Francesco Settembrini

from django import forms
from django.core.validators import MinValueValidator

from django.conf import settings

# class PaymentInitiateForm(forms.Form):
#                         # Field per definire la durata minima del noleggi
#                         # default a 30 minuti
#     rental_duration_minutes = forms.IntegerField(
#         label='Rental Duration (minutes)',
#         initial=30,
#         validators=[MinValueValidator(30)],
#         widget=forms.NumberInput(attrs={'min': '30'})
#     )
#

# (C) 2026 Francesco Settembrini
# Commenti in italiano, naming in inglese, logiche in inglese per l'utente

from django import forms
from django.core.validators import MinValueValidator
from django.conf import settings  # Importiamo i settings per controllare il flag DEBUG


class PaymentInitiateForm(forms.Form):
    # Dichiariamo il campo base senza validatore fisso per renderlo dinamico
    rental_duration_minutes = forms.IntegerField(
        label='Rental Duration (minutes)',
        widget=forms.NumberInput()
    )

    def __init__(self, *args, **kwargs):
        super(PaymentInitiateForm, self).__init__(*args, **kwargs)

        # --- LOGICA RICHIESTA: SOGLIA DINAMICA BASATA SU DEBUG ---
        # Se siamo in sviluppo (DEBUG=True) la durata minima è 1 minuto, altrimenti 5 minuti
        if settings.DEBUG:
            min_duration = 1
        else:
            min_duration = 5

        # Applichiamo dinamicamente il valore iniziale, il minimo HTML e il validatore Django
        self.fields['rental_duration_minutes'].initial = min_duration
        self.fields['rental_duration_minutes'].validators = [MinValueValidator(min_duration)]
        self.fields['rental_duration_minutes'].widget.attrs.update({
            'class': 'form-control',
            'min': str(min_duration)
        })


class PaymentPayForm(forms.Form):
    card_number = forms.CharField(max_length=16, min_length=16, label="Card Number")
    expiry_date = forms.CharField(max_length=5, label="Expiry Date (MM/YY)")
    cvc = forms.CharField(max_length=3, min_length=3, label="CVC")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=10.00,
        disabled = True, label="Amount \u20AC")

