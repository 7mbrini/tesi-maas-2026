# (C) 2025 Francesco Settembrini

from django.urls import path
from . import views

urlpatterns = [
    path('initiate/<int:car_id>/', views.payment_initiate, name='payment_initiate'),
    path('pay/', views.payment_pay, name='payment_pay'),
    path('process/', views.payment_process, name='payment_process'),
    path('success/<str:token>/', views.payment_success, name='payment_success'),
    path('failure/', views.payment_failure, name='payment_failure'),
]
