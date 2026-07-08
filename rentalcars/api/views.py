# (C) 2026 Francesco Settembrini

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize

from rest_framework.response import Response
from django.core.serializers.json import DjangoJSONEncoder

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

from decimal import Decimal, InvalidOperation

from django.conf import settings
from cars.models import Car

# =============================================================================
def clear_logs():
    # Stampa 3 stringhe vuote e una linea tratteggiata
    print("\n" * 3 + "="*50)
    print(" NUOVA ESECUZIONE ".center(50, "="))
    print("="*50 + "\n")

# # =============================================================================
# def get_db_connection():
#     connection = psycopg2.connect(
#         dbname="rentalcars",
#         user="postgres",
#         password="postgres",
#         host="db",
#         port="5432",
#     )
#
#     return connection

def get_db_connection():
    # Estraiamo il dizionario 'default' configurato in settings.py
    db_config = settings.DATABASES['default']

    connection = psycopg2.connect(
        dbname=db_config['NAME'],
        user=db_config['USER'],
        password=db_config['PASSWORD'],
        host=db_config['HOST'],
        port=db_config['PORT'],
        #port='9999',
    )
    return connection


# =============================================================================
# API: Restituisce tutte le auto presenti nel database
# =============================================================================
def api_cars_get_all(request):

    geojson_data = {}

    try:
        cars = Car.objects.all()

        geojson_data = serialize('geojson', cars,
            geometry_field = 'location',
            fields = ('license_plate', 'seats', 'hourly_rate',
                'doors', 'range_km', 'available', 'location' )
        )

    except Exception:
        print("errore in: api_cars_get_all")

    return HttpResponse(geojson_data, content_type='application/json')


# =============================================================================
# API: Restituisce l'auto con la targa richiesta
# =============================================================================
def api_cars_get_by_license_plate(request, license_plate):

    sel_cars = []
    connection = None

    try:
        connection = get_db_connection()

                                            # Usa RealDictCursor per ottenere
                                            # il risultato come dizionario
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        str_query = """
              SELECT 
                  id, 
                  license_plate,
                  doors,
                  seats,
                  hourly_rate,
                  range_km,
                  ST_X(location) AS lon,
                  ST_Y(location) AS lat 
              FROM cars_car
              WHERE license_plate = %s
          """
                                            # esegue la query
        cursor.execute(str_query, (str(license_plate), ))

        sel_cars = cursor.fetchone()

        #os.system('cls')
        #clear_logs()
        #print(sel_cars)

    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching spatial data: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    return HttpResponse(
        json.dumps(sel_cars, indent=4, cls=DjangoJSONEncoder),
        content_type='application/json'
    )


# =============================================================================
# API: Restituisce tutte le auto che hanno numero di posti a sedere
# maggiore o uguale al valore richiesto
# =============================================================================
def api_cars_get_by_seats(request, seats):

    sel_cars = []
    connection = None

    #print(seats)
    #print(type(seats))

    try:
        connection = get_db_connection()

                                            # Usa RealDictCursor per ottenere
                                            # il risultato come dizionario
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        str_query = """
              SELECT 
                  id, 
                  license_plate,
                  doors,
                  seats,
                  hourly_rate,
                  range_km,
                  ST_X(location) AS lon,
                  ST_Y(location) AS lat 
              FROM cars_car
              WHERE seats >= %s
          """
                                            # esegue la query
        #cursor.execute(str_query, (seats,))
        cursor.execute(str_query, [seats])

        sel_cars = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching spatial data: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    return HttpResponse(
        json.dumps(sel_cars, indent=4, cls=DjangoJSONEncoder),
        content_type='application/json'
    )

# =============================================================================
# API: Restituisce tutte le auto che hanno numero di porte maggiore o uguale
#      al valore richiesto
# =============================================================================
def api_cars_get_by_doors(request, doors):

    sel_cars = []
    connection = None

    try:
        connection = get_db_connection()

                                            # Usa RealDictCursor per ottenere
                                            # il risultato come dizionario
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        str_query = """
              SELECT 
                  id, 
                  license_plate,
                  doors,
                  seats,
                  hourly_rate,
                  range_km,
                  ST_X(location) AS lon,
                  ST_Y(location) AS lat 
              FROM cars_car
              WHERE doors >= %s
          """
                                            # esegue la query
        cursor.execute(str_query, (doors,))

        sel_cars = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching spatial data: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    return HttpResponse(
        json.dumps(sel_cars, indent=4, cls=DjangoJSONEncoder),
        content_type='application/json'
    )

# =============================================================================
# API: Restituisce tutte le auto che hanno una autonomia chilommetria
#      maggiore o uguale al valore richiesto
# =============================================================================
def api_cars_get_by_range_km(request, range):

    sel_cars = []
    connection = None

    #print(seats)
    #print(type(seats))

    try:
        connection = get_db_connection()

                                            # Usa RealDictCursor per ottenere
                                            # il risultato come dizionario
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        str_query = """
              SELECT 
                  id, 
                  license_plate,
                  doors,
                  seats,
                  hourly_rate,
                  range_km,
                  ST_X(location) AS lon,
                  ST_Y(location) AS lat 
              FROM cars_car
              WHERE range_km >= %s
          """
                                            # esegue la query
        cursor.execute(str_query, (range,))

        sel_cars = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching spatial data: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    return HttpResponse(
        json.dumps(sel_cars, indent=4, cls=DjangoJSONEncoder),
        content_type='application/json'
    )

# =============================================================================
# API: Restituisce tutte le auto piu' vicine alla posizione richiesta,
#      con le distanze in ordine crescente
# =============================================================================
def api_cars_get_by_nearest_pos(request, latitude, longitude, radius):
    connection = None
    sel_cars = []

    # clear_logs()
    # print(latitude)
    # print(longitude)
    # print(radius)

    lat = Decimal(latitude)
    lon = Decimal(longitude)
    radius = Decimal(radius)

    clear_logs()
    print(lat)
    print(lon)
    print(radius)

    try:
        connection = get_db_connection()
                                            # Usa RealDictCursor per ottenere
                                            # il risultato come dizionario
        cursor = connection.cursor(cursor_factory=RealDictCursor)

                                            # esegue la "spatial query" (buffer)
        str_spatial_query = """
            SELECT 
                id, 
                license_plate,
                doors,
                seats,
                hourly_rate,
                range_km,
                ST_X(location) AS lon,
                ST_Y(location) AS lat, 
                ST_Distance(
                    location::geography, 
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) AS distance_meters
            FROM cars_car
            WHERE ST_DWithin(
                location::geography, 
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 
                %s
            )
            ORDER BY distance_meters ASC;
        """
                                    # esegue la 'spatial query'
        cursor.execute(str_spatial_query, [longitude, latitude, longitude, latitude, radius])

        sel_cars = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching spatial data: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    return HttpResponse(
        json.dumps(sel_cars, indent=4, cls=DjangoJSONEncoder),
        content_type='application/json'
    )

