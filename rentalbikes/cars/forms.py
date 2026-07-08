# (C) 2025 Francesco Settembrini

from django.contrib.gis import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['id', 'license_plate', 'seats', 'hourly_rate', 'doors', 'image', 'range_km']
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 6}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'doors': forms.Select(attrs={'class': 'form-select'}),
            'range_km': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

