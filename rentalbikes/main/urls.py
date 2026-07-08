# (C) 2025 Francesco Settembrini

from django.urls import path


from .views import (home_view, about_view,
    policies_view, contacts_view, fleet_view)

urlpatterns = [
    path('', home_view, name='home'),
    path('fleet/', fleet_view, name='fleet'),
    path('about/', about_view, name='about'),
    path('policies/', policies_view, name='policies'),
    path('contacts/', contacts_view, name='contacts'),
]

