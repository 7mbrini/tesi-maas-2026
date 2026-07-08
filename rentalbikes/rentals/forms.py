# (C) 2025 Francesco Settembrini

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

    listbox_doors = forms.ChoiceField(
        choices=CHOICES_DOORS,
        label="doors ",
        #widget=forms.Select(attrs={'size': '2'}) # Displays 2 rows visible
        widget=forms.Select() # Displays 2 rows visible
    )

    listbox_seats = forms.ChoiceField(
        choices=CHOICES_SEATS,
        label="seats ",
        #widget=forms.Select(attrs={'size': '2'}) # Displays 2 rows visible
        widget=forms.Select() # Displays 2 rows visible,
    )

                                    # buffer atttorno alla posizione dell'utente
    buffer = forms.IntegerField(
        label='Search radius (m) ',
        initial=500,  # Default value is still 500 meters
        min_value=0,  # Optional: ensures the value is non-negative
        required=True,
        # help_text='<br>(enter a positive integer number)'
        widget=forms.NumberInput(attrs={
            'class': 'form-control-sm',  # Dimensione ridotta (Bootstrap)
            'style': 'width: 100px;',  # Larghezza fissa via CSS
        })
    )

