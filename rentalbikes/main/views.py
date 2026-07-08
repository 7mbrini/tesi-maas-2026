# (C) 2025 Francesco Settembrini

from django.shortcuts import render
from cars.models import Car

# =============================================================================
# Renders the main landing page
# =============================================================================
def home_view(request):
    return render(request, 'main/home.html')

# =============================================================================
# Renders a simple about page. (Template needs to be created in main/templates/main/about.html)
# =============================================================================
def about_view(request):
    return render(request, 'main/about.html')

# =============================================================================
# Policies View
# =============================================================================
def policies_view(request):
    return render(request,'main/policies.html')

# =============================================================================
# Renders a simple about page. (Template needs to be created in main/templates/main/about.html)
# =============================================================================
def contacts_view(request):
    return render(request, 'main/contacts.html')

# =============================================================================
# Renders the main landing page, listing available cars from the 'cars' app.
# =============================================================================
def fleet_view(request):
    cars_list = Car.objects.all().order_by('hourly_rate')
    context = {'cars_list': cars_list}
    return render(request, 'main/fleet.html', context)


