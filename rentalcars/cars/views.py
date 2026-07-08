
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import generics
from .models import Car
from .forms import CarForm
from .serializers import CarDetailSerializer, CarLocationSerializer

# FBV for custom admin editing page
@staff_member_required
def edit_car_admin_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            #return redirect('admin:index')
    else:
        form = CarForm(instance=car)

    context = {'form': form, 'car': car}
    return render(request, 'cars/edit_car_admin.html', context)

# API View 1: Complete details (standard DRF ListAPIView)
class CarDetailAPIView(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarDetailSerializer

# API View 2: Geo locations (standard DRF ListAPIView, serializer handles GeoJSON)
class CarLocationAPIView(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarLocationSerializer
