# (C) 2026 Francesco Settembrini

from django.shortcuts import render
from vehicles.models import Vehicle

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

# # =============================================================================
# # Renders the main landing page, listing available vehicles from the 'vehicles' app.
# # =============================================================================
# def fleet_view(request):
#     vehicles_list = Vehicle.objects.all().order_by('hourly_rate')
#     context = {'vehicles_list': vehicles_list}
#     return render(request, 'main/fleet.html', context)

# =============================================================================
# Renders the main landing page, listing usable vehicles from the 'vehicles' app.
# =============================================================================
def fleet_view(request):
    # Il filtro legge dinamicamente la costante dal modello Vehicle!
    vehicles_list = Vehicle.objects.filter(
        battery_percentage__gt=Vehicle.MIN_BATTERY_LEVEL
    ).order_by('hourly_rate')

    context = {'vehicles_list': vehicles_list}
    return render(request, 'main/fleet.html', context)
