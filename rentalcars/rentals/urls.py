# (C) 2026 Francesco Settembrini

from django.urls import path
from .views import rentals_view

urlpatterns = [
    path('', rentals_view, name='rentals'),
]

