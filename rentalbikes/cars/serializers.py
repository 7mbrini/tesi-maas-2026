# (C) 2025 Francesco Settembrini

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers

from .models import Car


class CarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'license_plate', 'seats', 'hourly_rate', 'doors', 'range_km', 'location']

class CarLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Car
        geo_field = 'location'
        fields = ['id']
