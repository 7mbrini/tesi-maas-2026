# (C) 2025 Francesco Settembrini

from django.urls import path
from .views import tools_view, tools_create_cars_view

urlpatterns = [
    path('', tools_view, name='tools'),
    path('create_cars', tools_create_cars_view, name='create_cars'),
]

