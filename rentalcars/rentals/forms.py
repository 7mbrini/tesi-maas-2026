
# (C) 2026 Francesco Settembrini

from django import forms


class RentalsForm(forms.Form):
    # scelta per il numero di porte
    CHOICES_DOORS = (
        ('0', 'any'),
        ('3', '3'),
        ('5', '5'),
    )
    # scelta per il numero di posti
    CHOICES_SEATS = (
        ('0', 'any'),
        ('2', '2'),
        ('4', '4'),
        ('6', '6'),
    )

    # scelta predefinita per il raggio di ricerca
    CHOICES_BUFFER = (
        (100, '100 m'),
        (200, '200 m'),
        (300, '300 m'),
        (400, '400 m'),
        (500, '500 m'),  # Valore iniziale
        (600, '600 m'),
        (700, '700 m'),
        (800, '800 m'),
        (900, '900 m'),
        (1000, '1000 m'),
        (1500, '1500 m'),
        (2000, '2000 m'),
    )

    listbox_doors = forms.ChoiceField(
        choices=CHOICES_DOORS,
        label="doors ",
        widget=forms.Select()
    )

    listbox_seats = forms.ChoiceField(
        choices=CHOICES_SEATS,
        label="seats ",
        widget=forms.Select()
    )
    # buffer attorno alla posizione dell'utente (TRASFORMATO IN SELECT)
    buffer = forms.TypedChoiceField(
        choices=CHOICES_BUFFER,
        coerce=int,  # Converte automaticamente la stringa selezionata in un intero Python
        label='Search radius ',
        initial=500,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control-sm',  # Mantiene la dimensione ridotta di Bootstrap
            'style': 'width: 110px;',  # Larghezza fissa adatta al testo "500 m"
        })
    )
