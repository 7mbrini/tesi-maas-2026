# (C) 2026 Francesco Settembrini

from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import connection

import os
import random
from django.contrib.gis.geos import Point

from utils.logs import log_print

from vehicles.models import Vehicle


# =============================================================================
def tools_view(request):
    #return HttpResponse("tools")
    return render(request, "tools/tools.html")


# =============================================================================
#
# =============================================================================
def tools_create_vehicles_view(request):

    try:
                                                            # Bari bboxes
        outer_bbox = [41.090, 16.814, 41.140, 16.934]       # hinterland barese
        mid_bbox = [41.107, 16.848, 41.132, 16.899]         # intera area urbana
        inner_bbox = [41.111, 16.855, 41.125, 16.871]       # zona "murattiana"

        Vehicle.objects.all().delete()

        bSnap = True

        create_vehicles(nCars=5, bbox = outer_bbox, snap = bSnap)
        create_vehicles(nCars=15, bbox = mid_bbox, snap = bSnap)
        create_vehicles(nCars=30, bbox = inner_bbox, snap = bSnap)

    except Exception as e:
        log_print(f"An unexpected error occurred: {str(e)}")

    return HttpResponseRedirect(reverse('tools'))


# =============================================================================
# Genera intego random a 4 cifre e lo aggiunge ad una lista predefinita
# =============================================================================
def generate_unique_four_digit_id(target_list):
    while True:
                                # genera un integer random tra 1000 and 9999 (incluso)
        new_id = random.randint(1000, 9999)

                                # verifica per l'uncita' nella lista
        if new_id not in target_list:
            target_list.append(new_id)
            return new_id

# =============================================================================
# Genera intego random a 5 cifre e lo aggiunge ad una lista predefinita
# =============================================================================
def generate_unique_five_digit_id(target_list):
    while True:
                                # genera un integer random tra 1000 and 9999 (incluso)
        new_id = random.randint(10000, 99999)

                                # verifica per l'uncita' nella lista
        if new_id not in target_list:
            target_list.append(new_id)
            return new_id

# =============================================================================
# Genera in maniera random un punto geografico in un rettangolo assegnato
# =============================================================================
def generate_random_geopoint(bbox):

    min_lat = bbox[0]
    min_lon = bbox[1]
    max_lat = bbox[2]
    max_lon = bbox[3]

    random_latitude = random.uniform(min_lat, max_lat)
    random_longitude = random.uniform(min_lon, max_lon)

    # Crea un Point usando l'ordine (Lon, Lat)
    # Imposta il riferimento a srid=4326 WGS84 (GPS standard)
    random_point = Point(random_longitude, random_latitude, srid=4326)

    return random_point


# =============================================================================
# Riposiziona il punto (lat,lon) sul grafo stradale
# =============================================================================
def snap_to_road(lat, lon, radius_meters = 100):
    try:
        # Convertiamo i 100 metri in gradi per adattarci all'indice spaziale esistente
        # 111000 metri = 1 grado nel nostro sistema. 100m = ~0.0009 gradi
        radius_degrees = radius_meters / 111000.0

        query = """
            SELECT 
                osm_name,
                ST_Y(ST_ClosestPoint(geom_way, ST_SetSRID(ST_Point(%s, %s), 4326))) AS snap_lat,
                ST_X(ST_ClosestPoint(geom_way, ST_SetSRID(ST_Point(%s, %s), 4326))) AS snap_lon,
                tag_id
            FROM ways
            WHERE ST_DWithin(
                geom_way, -- Rimosso il cast ::geography per ATTIVARE l'indice esistente!
                ST_SetSRID(ST_Point(%s, %s), 4326), 
                %s        -- Passiamo il raggio in gradi (radius_degrees)
            )
            ORDER BY geom_way <-> ST_SetSRID(ST_Point(%s, %s), 4326)
            LIMIT 1;
        """

        params = [
            lon, lat,  # Per ST_Y
            lon, lat,  # Per ST_X
            lon, lat, radius_degrees,  # Per ST_DWithin (Usa i gradi!)
            lon, lat  # Per ORDER BY (Operatore KNN <-> velocissimo con l'indice)
        ]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()

        if row:
            rclass = row[3]    # tag_id

            if (rclass > 11) and (rclass < 120) :
                return row[1], row[2]

        return None

    except Exception as e:
        log_print(str(e))
        return None


# =============================================================================
# Genera e restituisce una lista di autoveicoli con "snap" sulle strade vehiclerabili
# =============================================================================
def create_vehicles(nCars, bbox, snap=True, snap_radius=200):

    vehicleModels = [
        {'seats': 2, 'doors': 3, 'hourly_rate': 15.0, 'image': 'vehicle_images/evehicle_01.jpg', 'range_km': 100},
#        {'seats': 2, 'doors': 3, 'hourly_rate': 15.0, 'image': 'vehicle_images/evehicle_02.jpg', 'range_km': 100},
        {'seats': 2, 'doors': 3, 'hourly_rate': 15.0, 'image': 'vehicle_images/evehicle_03.jpg', 'range_km': 100},
#        {'seats': 2, 'doors': 3, 'hourly_rate': 15.0, 'image': 'vehicle_images/evehicle_04.jpg', 'range_km': 100},
        {'seats': 2, 'doors': 3, 'hourly_rate': 15.0, 'image': 'vehicle_images/evehicle_05.jpg', 'range_km': 100},
        {'seats': 4, 'doors': 5, 'hourly_rate': 20.0, 'image': 'vehicle_images/evehicle_11.jpg', 'range_km': 150},
#        {'seats': 4, 'doors': 5, 'hourly_rate': 20.0, 'image': 'vehicle_images/evehicle_12.jpg', 'range_km': 150},
        {'seats': 6, 'doors': 5, 'hourly_rate': 20.0, 'image': 'vehicle_images/evehicle_13.jpg', 'range_km': 150},
#        {'seats': 4, 'doors': 5, 'hourly_rate': 20.0, 'image': 'vehicle_images/evehicle_14.jpg', 'range_km': 150},
#        {'seats': 6, 'doors': 5, 'hourly_rate': 20.0, 'image': 'vehicle_images/evehicle_15.jpg', 'range_km': 150},
    ]

    counter = 0
    plates = []

    while counter < nCars:
        randModel = vehicleModels[random.randint(0, len(vehicleModels)-1)]

        TheCar = Vehicle()
        #TheCar.license_plate = f'BA{generate_unique_four_digit_id(plates)}'
        TheCar.license_plate = f'BAC{generate_unique_five_digit_id(plates)}'
        TheCar.seats = randModel['seats']
        TheCar.unlock_cost = 1.5
        TheCar.hourly_rate = randModel['hourly_rate']
        TheCar.doors = randModel['doors']
        TheCar.image = randModel['image']
        TheCar.range_km = randModel['range_km']
        TheCar.is_available = random.choice([True, False])
        TheCar.battery_percentage = random.randint(0, 100)

        pos = generate_random_geopoint(bbox)

                                            # se attivo lo "snap" posizione le auto sulle vie vehiclerabili
        if snap == True :
            snapped_pos = snap_to_road(pos.y, pos.x, snap_radius)

            if snapped_pos:
                pos = Point(snapped_pos[1], snapped_pos[0], srid=4326)
            else:
                continue

        TheCar.location = pos
        TheCar.save()
        counter += 1
