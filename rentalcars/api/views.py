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

from utils.logs import log_clear, log_print


def get_db_connection():
    db_config = settings.DATABASES['default']

    connection = psycopg2.connect(
        dbname=db_config['NAME'],
        user=db_config['USER'],
        password=db_config['PASSWORD'],
        host=db_config['HOST'],
        port=db_config['PORT'],
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
        log_print("errore in: api_cars_get_all")

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

        #log_clear()
        #log_print(sel_cars)

    except (Exception, psycopg2.Error) as error:
        log_print(f"Error while fetching spatial data: {error}")

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

    #log_print(seats)
    #log_print(type(seats))

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
        cursor.execute(str_query, [seats])

        sel_cars = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        log_print(f"Error while fetching spatial data: {error}")

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
        log_print(f"Error while fetching spatial data: {error}")

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

    #log_print(seats)
    #log_print(type(seats))

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
        log_print(f"Error while fetching spatial data: {error}")

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

    # log_clear()
    # log_print(latitude)
    # log_print(longitude)
    # log_print(radius)

    lat = Decimal(latitude)
    lon = Decimal(longitude)
    radius = Decimal(radius)

    log_clear()
    log_print(lat)
    log_print(lon)
    log_print(radius)

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
        log_print(f"Error while fetching spatial data: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    return HttpResponse(
        json.dumps(sel_cars, indent=4, cls=DjangoJSONEncoder),
        content_type='application/json'
    )


# (C) 2026 Francesco Settembrini

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from rentals.models import Rental


@csrf_exempt  # Rimuove l'obbligo del token CSRF per le richieste esterne (M2M / .NET MAUI)
def api_hardware_unlock(request):
    # Consente esclusivamente richieste in POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        # Estrae il payload JSON inviato dall'hardware o dallo smartphone
        data = json.loads(request.body)
        code = data.get('unlock_code', '').strip().upper()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    # Verifica la presenza del codice di sblocco
    if not code:
        return JsonResponse({'error': 'Missing unlock_code'}, status=400)

    try:
        # Tenta di recuperare il noleggio associato a quel PIN specifico
        rental = Rental.objects.get(check_code=code, status='reserved')

        # 1. Attiva ufficialmente il noleggio facendo partire il timer a runtime ora
        rental.status = 'active'
        rental.start_time = timezone.now()
        rental.save()

        # 2. Invia l'impulso hardware all'auto associata sbloccando la serratura
        if rental.car:
            rental.car.is_locked = False  # Le portiere fisiche si aprono!
            rental.car.save()

            # --- Debug: log per confermare l'evento M2M a terminale ---
            print(f"[{timezone.now().strftime('%H:%M:%S')}] M2M API - UNLOCK CAR {rental.car.license_plate} CODE {code}")

        # Restituisce la risposta di successo in inglese per il client
        return JsonResponse({
            'status': 'success',
            'message': f'Vehicle {rental.car.license_plate} successfully unlocked. Enjoy your ride!',
            'start_time': rental.start_time.isoformat(),
            'estimated_end_time': rental.end_time.isoformat()  # Calcolata in RAM dalla property!
        }, status=200)

    except Rental.DoesNotExist:
        # Codice errato, scaduto o già utilizzato
        return JsonResponse({'error': 'Invalid or expired unlock code'}, status=404)
