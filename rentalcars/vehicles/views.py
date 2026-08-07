# (C) 2026 Francesco Settembrini

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import generics
from .models import Vehicle
from .forms import CarForm
from .serializers import CarDetailSerializer, CarLocationSerializer

# FBV for custom admin editing page
@staff_member_required
def edit_vehicle_admin_view(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            #return redirect('admin:index')
    else:
        form = CarForm(instance=vehicle)

    context = {'form': form, 'vehicle': vehicle}
    return render(request, 'vehicles/edit_vehicle_admin.html', context)

# API View 1: Complete details (standard DRF ListAPIView)
class CarDetailAPIView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = CarDetailSerializer

# API View 2: Geo locations (standard DRF ListAPIView, serializer handles GeoJSON)
class CarLocationAPIView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = CarLocationSerializer
