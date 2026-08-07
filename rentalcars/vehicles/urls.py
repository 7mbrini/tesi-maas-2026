
from django.urls import path
from .views import edit_vehicle_admin_view, CarDetailAPIView, CarLocationAPIView

urlpatterns = [
    path('admin/vehicle/edit/<int:vehicle_id>/', edit_vehicle_admin_view, name='edit_vehicle_admin'),
    path('api/details/', CarDetailAPIView.as_view(), name='vehicle-details-api'),
    path('api/locations/', CarLocationAPIView.as_view(), name='vehicle-locations-api'),
]
