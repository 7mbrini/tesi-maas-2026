# (C) 2025 Francesco Settembrini

from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import connection

import os
import random
from django.contrib.gis.geos import Point

from cars.models import Car


# =============================================================================
def tools_view(request):
    #return HttpResponse("tools")
    return render(request, "tools/tools.html")


# =============================================================================
#
# =============================================================================
def tools_create_cars_view(request):
    # ERRORE VOLUTO PER TESTARE IL DEBUG: Divisione per zero
    # crash_test = 1 / 0

    try:
                                                            # Bari bboxes
        #41.09093838558338, 16.814744635798853
        ##41.140596893679714, 16.934185230930062
        outer_bbox = [41.090, 16.814, 41.140, 16.934]       # hinterland barese

        #41.107395104646294, 16.848428179301322
        #41.1326196154576, 16.899028764043038
        mid_bbox = [41.107, 16.848, 41.132, 16.899]         # intera area urbana

        #41.1117066723118, 16.855652248180245
        #41.12597388861723, 16.871184489239266
        inner_bbox = [41.111, 16.855, 41.125, 16.871]       # zona "murattiana"


        Car.objects.all().delete()

        bSnap = True

        create_cars(nCars=5, bbox = outer_bbox, snap = bSnap)
        create_cars(nCars=25, bbox = mid_bbox, snap = bSnap)
        create_cars(nCars=30, bbox = inner_bbox, snap = bSnap)


    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

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
# Genera in maniera random un punto geografico in un rettangolo assegnato
# =============================================================================
#def generate_random_geopoint(min_lat, min_lon, max_lat, max_lon):
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

# # =============================================================================
# # Return (lat,lon) snapped to a valid position on a viable road
# # =============================================================================
# def snap_to_road(lat, lon, radius_meters = 100):
#     try:
#         query = """
#             SELECT
#                 osm_name,
#                 ST_Y(ST_ClosestPoint(geom_way, ST_SetSRID(ST_Point(%s, %s), 4326))) AS snap_lat,
#                 ST_X(ST_ClosestPoint(geom_way, ST_SetSRID(ST_Point(%s, %s), 4326))) AS snap_lon,
#                 tag_id
#             FROM ways
#             WHERE ST_DWithin(
#                 geom_way::geography,
#                 ST_SetSRID(ST_Point(%s, %s), 4326)::geography,
#                 %s
#             )
#             ORDER BY geom_way <-> ST_SetSRID(ST_Point(%s, %s), 4326)
#             LIMIT 1;
#         """
#
#         params = [
#             lon, lat,  # Per ST_Y (1, 2)
#             lon, lat,  # Per ST_X (3, 4)
#             lon, lat, radius_meters,  # Per ST_DWithin (5, 6, 7)
#             lon, lat  # Per ORDER BY (8, 9)
#         ]
#
#         with connection.cursor() as cursor:
#             cursor.execute(query, params)
#             row = cursor.fetchone()
#
#         if row:
#             #print( row )
#
#             rclass = row[3]    # road class
#
#             if (rclass > 11) and (rclass < 60) :
#                 return row[1], row[2]
#
#         return None
#
#     except Exception as e:
#         print(str(e))
#         return None
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
        print(str(e))
        return None


# =============================================================================
# Genera e restituisce una lista di autoveicoli con "snap" sulle strade carrabili
# =============================================================================
def create_cars(nCars, bbox, snap=True, snap_radius=200):

    carModels = [
        {'seats': 2, 'doors': 3, 'hourly_rate': 20.0, 'image': 'car_images/ecar_01.jpg', 'range_km': 100},
        {'seats': 2, 'doors': 3, 'hourly_rate': 25.0, 'image': 'car_images/ecar_02.jpg', 'range_km': 150},
        {'seats': 2, 'doors': 3, 'hourly_rate': 20.0, 'image': 'car_images/ecar_03.jpg', 'range_km': 150},
        {'seats': 2, 'doors': 3, 'hourly_rate': 25.0, 'image': 'car_images/ecar_04.jpg', 'range_km': 100},
        {'seats': 2, 'doors': 3, 'hourly_rate': 20.0, 'image': 'car_images/ecar_05.jpg', 'range_km': 150},
        {'seats': 4, 'doors': 5, 'hourly_rate': 30.0, 'image': 'car_images/ecar_11.jpg', 'range_km': 300},
        {'seats': 4, 'doors': 5, 'hourly_rate': 35.0, 'image': 'car_images/ecar_12.jpg', 'range_km': 350},
        {'seats': 6, 'doors': 5, 'hourly_rate': 50.0, 'image': 'car_images/ecar_13.jpg', 'range_km': 250},
        {'seats': 4, 'doors': 5, 'hourly_rate': 35.0, 'image': 'car_images/ecar_14.jpg', 'range_km': 300},
        {'seats': 6, 'doors': 5, 'hourly_rate': 50.0, 'image': 'car_images/ecar_15.jpg', 'range_km': 350},
    ]

    counter = 0
    plates = []

    while counter < nCars:
        randModel = carModels[random.randint(0, len(carModels)-1)]

        TheCar = Car()
        TheCar.license_plate = f'BA{generate_unique_four_digit_id(plates)}'
        TheCar.seats = randModel['seats']
        TheCar.hourly_rate = randModel['hourly_rate']
        TheCar.doors = randModel['doors']
        TheCar.image = randModel['image']
        TheCar.range_km = randModel['range_km']
        TheCar.available = random.choice([True, False])

        pos = generate_random_geopoint(bbox)

                                            # se attivo lo "snap" posizione le auto sulle vie carrabili
        if snap == True :
            snapped_pos = snap_to_road(pos.y, pos.x, snap_radius)

            if snapped_pos:
                pos = Point(snapped_pos[1], snapped_pos[0], srid=4326)
            else:
                continue

        TheCar.location = pos
        TheCar.save()
        counter += 1
