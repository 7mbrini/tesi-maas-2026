# from django.urls import path
# from .views import edit_car_admin_view
#
# urlpatterns = [
#     path('admin/car/edit/<int:car_id>/', edit_car_admin_view, name='edit_car_admin'),
# ]
#
# from django.urls import path
# from .views import edit_car_admin_view, CarDetailAPIView, CarLocationAPIView
#
# urlpatterns = [
#     path('admin/car/edit/<int:car_id>/', edit_car_admin_view, name='edit_car_admin'),
#     path('api/details/', CarDetailAPIView.as_view(), name='car-details-api'),
#     path('api/locations/', CarLocationAPIView.as_view(), name='car-locations-api'),
# ]
#
from django.urls import path
from .views import edit_car_admin_view, CarDetailAPIView, CarLocationAPIView

urlpatterns = [
    path('admin/car/edit/<int:car_id>/', edit_car_admin_view, name='edit_car_admin'),
    path('api/details/', CarDetailAPIView.as_view(), name='car-details-api'),
    path('api/locations/', CarLocationAPIView.as_view(), name='car-locations-api'),
]
