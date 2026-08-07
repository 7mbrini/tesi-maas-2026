# (C) 2026 Francesco Settembrini

from django.urls import path
from .views import tools_view, tools_create_vehicles_view

urlpatterns = [
    path('', tools_view, name='tools'),
    path('create_vehicles', tools_create_vehicles_view, name='create_vehicles'),
]

