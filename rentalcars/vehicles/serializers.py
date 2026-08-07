# (C) 2026 Francesco Settembrini

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers

from .models import Vehicle


class CarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'license_plate', 'seats', 'hourly_rate', 'doors', 'range_km', 'location']

class CarLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Vehicle
        geo_field = 'location'
        fields = ['id']
