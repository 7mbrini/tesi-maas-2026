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

from django.contrib.auth.models import User

from decimal import Decimal, InvalidOperation

from django.conf import settings
from cars.models import Car

from utils.logs import log_clear, log_print

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

#from cars.models import Car, Rental, PaymentTransaction
from rentals.models import Rental
from payments.models import PaymentTransaction

from decimal import Decimal
import json
import uuid
import io
import qrcode
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

# Importa i tuoi modelli reali (verifica i percorsi delle app se necessario)
#from payments.models import PaymentTransaction
#from rental.models import Rental
#from cars.models import Car
from payments.views import send_confirmation_email

import uuid
import io
import qrcode


from decimal import Decimal
import json
import uuid
import io
import qrcode
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

# Import dei modelli dalle app reali del tuo database
from rentals.models import Rental
from payments.models import PaymentTransaction
from cars.models import Car



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


@csrf_exempt  # Rimuove l'obbligo del token CSRF per le richieste esterne (M2M)
def api_vehicle_unlock(request):
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

        # Attiva ufficialmente il noleggio facendo partire il timer a runtime ora
        rental.status = 'active'
        rental.start_time = timezone.now()
        rental.save()

        # Invia l'impulso hardware all'auto associata sbloccando la serratura
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


# =============================================================================
# API: Gestisce la prenotazione e il pagamento atomico dall'orchestratore MaaS
# =============================================================================
# @csrf_exempt
# def api_vehicle_rent(request):
#     """Endpoint API per l'orchestratore MaaS per prenotare e pagare un veicolo."""
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)
#
#     try:
#         # 1. Parsing del JSON
#         data = json.loads(request.body)
#
#         username = data.get('username')
#         car_id = data.get('car_id')
#         duration_minutes = data.get('duration_minutes')
#
#         if not all([username, car_id, duration_minutes]):
#             return JsonResponse(
#                 {'status': 'error', 'message': 'Missing required fields: username, car_id, duration_minutes'},
#                 status=400)
#
#         # CORRETTO: Validazione preventiva del tipo di dato per la durata
#         try:
#             dec_minutes = Decimal(str(duration_minutes))
#             int_duration_minutes = int(duration_minutes)
#         except (ValueError, TypeError, KeyError):
#             return JsonResponse({'status': 'error', 'message': 'Invalid format for duration_minutes'}, status=400)
#
#         # CORRETTO: Sostituito get_object_or_404 con costrutti try/except per restituire JSON coerenti
#         try:
#             user = User.objects.get(username=username)
#             car = Car.objects.get(id=car_id)
#         except ObjectDoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'User or Car not found'}, status=404)
#
#         # Calcolo analitico dei costi
#         dec_hourly_rate = Decimal(str(car.hourly_rate))
#         dec_unlock_cost = Decimal(str(car.unlock_cost))
#         time_cost = (dec_hourly_rate * dec_minutes) / Decimal('60.0')
#         total_amount = (dec_unlock_cost + time_cost).quantize(Decimal('0.01'))
#
#         # Transazione ACID atomica sul Database
#         with transaction.atomic():
#             # CORRETTO: select_for_update() blocca la riga sul DB ed evita che altri thread leggano l'auto come disponibile
#             car_locked = Car.objects.select_for_update().get(id=car.id)
#
#             if not car_locked.is_available:
#                 return JsonResponse({'status': 'error', 'message': 'Vehicle is already booked'}, status=400)
#
#             new_rental = Rental.objects.create(
#                 user=user,
#                 car=car_locked,
#                 status='reserved',
#                 duration_minutes=int_duration_minutes
#             )
#
#             new_transaction = PaymentTransaction.objects.create(
#                 rental=new_rental,
#                 user=user,
#                 amount=total_amount,
#                 status='completed',
#                 is_paid=True,
#                 gateway_transaction_id=str(uuid.uuid4())
#             )
#
#             # Cambia lo stato dell'auto locked
#             car_locked.is_available = False
#             car_locked.save()
#
#             # Aggiorniamo il riferimento locale per il resto della funzione
#             car = car_locked
#
#         # Generazione del token e del QR Code in memoria
#         token = new_rental.check_code
#         qr = qrcode.QRCode(version=1, box_size=10, border=4)
#         qr.add_data(token)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")
#
#         buffer = io.BytesIO()
#         img.save(buffer, format="PNG")
#         qr_bytes = buffer.getvalue()
#
#         # Deviazione della mail al passeggero reale
#         passenger_email = data.get('user_email', user.email)
#         user.email = passenger_email
#
#         # CORRETTO: Isolato l'invio email. Se fallisce la mail, l'API restituisce comunque Success (201)
#         # perché il noleggio sul DB è andato a buon fine.
#         try:
#             send_confirmation_email(user, new_rental, token, car.license_plate, qr_bytes)
#         except Exception as mail_err:
#             log_print(f"Errore non bloccante nell'invio della mail: {str(mail_err)}")
#
#         # Payload JSON pulito di risposta
#         response_data = {
#             'status': 'success',
#             'booking_id': new_rental.id,
#             'unlock_code': token,
#             'license_plate': car.license_plate,
#             'amount_paid': float(total_amount),
#             'gateway_transaction_id': new_transaction.gateway_transaction_id,
#             'message': 'Rental successfully processed via MaaS Orchestrator'
#         }
#         return JsonResponse(response_data, status=201)
#
#     except json.JSONDecodeError:
#         log_print("Errore: payload JSON non valido inviato all'API")
#         return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
#     except Exception as e:
#         log_print(f"Errore interno in api_book_and_pay: {str(e)}")
#         return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

# @csrf_exempt
# def api_vehicle_rent(request):
#     """
#     Endpoint API per l'orchestratore MaaS.
#     Imita fedelmente la logica atomica e disaccoppiata del noleggio diretto (payment_process).
#     Il conteggio del tempo NON parte qui: lo stato iniziale è 'reserved'.
#     """
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)
#
#     try:
#         # 1. Parsing del JSON inviato dall'orchestratore MaaS
#         data = json.loads(request.body)
#
#         username = data.get('username')
#         car_id = data.get('car_id')
#         duration_minutes = data.get('duration_minutes')
#
#         # Controllo presenza dati obbligatori
#         if not all([username, car_id, duration_minutes]):
#             return JsonResponse(
#                 {'status': 'error', 'message': 'Missing required fields: username, car_id, duration_minutes'},
#                 status=400)
#
#         # Validazione preventiva del tipo di dato per la durata
#         try:
#             dec_minutes = Decimal(str(duration_minutes))
#             int_duration_minutes = int(duration_minutes)
#         except (ValueError, TypeError, KeyError):
#             return JsonResponse({'status': 'error', 'message': 'Invalid format for duration_minutes'}, status=400)
#
#         # Recupero dell'utente e dell'auto con gestione pulita ed esplicita degli errori
#         try:
#             user = User.objects.get(username=username)
#             car = Car.objects.get(id=car_id)
#         except ObjectDoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'User or Car not found'}, status=404)
#
#         # Calcolo analitico e blindato dei costi (coerente con le tariffe del mezzo)
#         dec_hourly_rate = Decimal(str(car.hourly_rate))
#         dec_unlock_cost = Decimal(str(car.unlock_cost))
#         time_cost = (dec_hourly_rate * dec_minutes) / Decimal('60.0')
#         total_amount = (dec_unlock_cost + time_cost).quantize(Decimal('0.01'))
#
#         # =====================================================================
#         # LOGICA ATOMICA DISACCOPPIATA (Identica a payment_process)
#         # =====================================================================
#         with transaction.atomic():
#             # Blocca la riga sul DB ed evita che altri thread leggano l'auto come disponibile
#             car_locked = Car.objects.select_for_update().get(id=car.id)
#
#             if not car_locked.is_available:
#                 return JsonResponse({'status': 'error', 'message': 'Vehicle is already booked'}, status=400)
#
#             # 1. Creiamo il Rental passandogli i suoi soli parametri validi in stato 'reserved'
#             # Nota: il campo 'timestamp' (data di creazione) si popola automaticamente grazie all'auto_now_add di Django
#             new_rental = Rental.objects.create(
#                 user=user,
#                 car=car_locked,
#                 status='reserved',
#                 duration_minutes=int_duration_minutes
#             )
#
#             # 2. Creiamo la PaymentTransaction agganciata al Rental appena nato
#             new_transaction = PaymentTransaction.objects.create(
#                 rental=new_rental,
#                 user=user,
#                 amount=total_amount,
#                 status='completed',
#                 is_paid=True,
#                 gateway_transaction_id=str(uuid.uuid4())
#             )
#
#             # 3. Aggiorniamo la disponibilità dell'auto per bloccarla sul server MaaS
#             car_locked.is_available = False
#             car_locked.save()
#
#             car = car_locked
#
#         # Recuperiamo il token generato automaticamente dal modello
#         token = new_rental.check_code
#
#         # --- FEEDBACK NEL LOGGER [API] ---
#         print(f"[API] M2M API - RESERVATION CREATED FOR CAR {car.license_plate} CODE {token} DURATION {int_duration_minutes} MIN. WAITING FOR UNLOCK.")
#
#         # Generazione del QR Code in memoria (Formato PNG)
#         qr = qrcode.QRCode(version=1, box_size=10, border=4)
#         qr.add_data(token)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")
#
#         buffer = io.BytesIO()
#         img.save(buffer, format="PNG")
#         qr_bytes = buffer.getvalue()
#
#         # Deviazione della mail al passeggero reale configurato nel payload
#         passenger_email = data.get('user_email', user.email)
#         user.email = passenger_email
#
#         # Invia l'e-mail di conferma (Isolato per non bloccare la risposta HTTP se l'SMTP rallenta)
#         try:
#             send_confirmation_email(user, new_rental, token, car.license_plate, qr_bytes)
#         except Exception as mail_err:
#             print(f"[API] Errore non bloccante nell'invio della mail di conferma: {str(mail_err)}")
#
#         # Payload JSON pulito di risposta per l'orchestratore MaaS
#         response_data = {
#             'status': 'success',
#             'booking_id': new_rental.id,
#             'unlock_code': token,
#             'license_plate': car.license_plate,
#             'amount_paid': float(total_amount),
#             'gateway_transaction_id': new_transaction.gateway_transaction_id,
#             'message': 'Rental successfully processed via MaaS Orchestrator'
#         }
#         return JsonResponse(response_data, status=201)
#
#     except json.JSONDecodeError:
#         print("[API] Errore: payload JSON non valido inviato all'API")
#         return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
#     except Exception as e:
#         print(f"[API] Errore interno in api_vehicle_rent: {str(e)}")
#         return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


@csrf_exempt
def api_vehicle_rent(request):
    """
    Endpoint API per l'orchestratore MaaS.
    Imita al 100% la stessa logica atomica e disaccoppiata del noleggio diretto da browser (payment_process).
    Il conteggio del tempo NON parte qui: lo stato iniziale è 'reserved'.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        # 1. Parsing dei dati in ingresso dal JSON
        data = json.loads(request.body)
        username = data.get('username')
        car_id = data.get('car_id')
        duration_minutes = data.get('duration_minutes')

        # Controllo presenza dati obbligatori
        if not all([username, car_id, duration_minutes]):
            return JsonResponse(
                {'status': 'error', 'message': 'Missing required fields: username, car_id, duration_minutes'},
                status=400)

        # Validazione preventiva del tipo di dato per la durata
        try:
            dec_minutes = Decimal(str(duration_minutes))
            int_duration_minutes = int(duration_minutes)
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid format for duration_minutes'}, status=400)

        # Recupero dell'utente e dell'auto con gestione pulita ed esplicita degli errori
        try:
            user = User.objects.get(username=username)
            car = Car.objects.get(id=car_id)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User or Car not found'}, status=404)

        # Calcolo economico analitico e blindato (coerente con le tariffe del mezzo)
        dec_hourly_rate = Decimal(str(car.hourly_rate))
        dec_unlock_cost = Decimal(str(car.unlock_cost))
        time_cost = (dec_hourly_rate * dec_minutes) / Decimal('60.0')
        total_amount = (dec_unlock_cost + time_cost).quantize(Decimal('0.01'))

        # =====================================================================
        # LA STESSISSIMA LOGICA ATOMICA DI "PAYMENT_PROCESS" (Browser)
        # =====================================================================
        with transaction.atomic():
            # Blocca la riga su PostgreSQL per evitare doppie prenotazioni concorrenti
            car_locked = Car.objects.select_for_update().get(id=car.id)

            if not car_locked.is_available:
                return JsonResponse({'status': 'error', 'message': 'Vehicle is already booked'}, status=400)

            # 1. Creazione Rental (Django gestisce in automatico la colonna 'timestamp' come sul browser)
            new_rental = Rental.objects.create(
                user=user,
                car=car_locked,
                status='reserved',
                duration_minutes=int_duration_minutes
            )

            # 2. Creazione PaymentTransaction agganciata al Rental appena nato
            new_transaction = PaymentTransaction.objects.create(
                rental=new_rental,
                user=user,
                amount=total_amount,
                status='completed',
                is_paid=True,
                gateway_transaction_id=str(uuid.uuid4())
            )

            # 3. Blocco dell'auto sulla mappa del MaaS
            car_locked.is_available = False
            car_locked.save()

            car = car_locked

        # Recuperiamo il codice di sblocco generato automaticamente dal modello
        token = new_rental.check_code

        # --- FEEDBACK NEL LOGGER [API] ---
        print(
            f"[API] M2M API - RESERVATION CREATED FOR CAR {car.license_plate} CODE {token} DURATION {int_duration_minutes} MIN. WAITING FOR UNLOCK.")

        # Generazione del QR Code in memoria (Formato PNG)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()

        # Configurazione email per la deviazione al passeggero reale a Bari
        passenger_email = data.get('user_email', user.email)
        user.email = passenger_email

        # Spedizione email protetta da un try/except locale per isolare gli errori SMTP
        try:
            send_confirmation_email(user, new_rental, token, car.license_plate, qr_bytes)
        except Exception as mail_err:
            print(f"[API] Errore non bloccante nell'invio della mail: {str(mail_err)}")

        # Payload JSON pulito di risposta per l'orchestratore MaaS
        return JsonResponse({
            'status': 'success',
            'booking_id': new_rental.id,
            'unlock_code': token,
            'license_plate': car.license_plate,
            'amount_paid': float(total_amount),
            'gateway_transaction_id': new_transaction.gateway_transaction_id,
            'message': 'Rental successfully processed via MaaS Orchestrator'
        }, status=201)

    except json.JSONDecodeError:
        print("[API] Errore: payload JSON non valido inviato all'API")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        print(f"[API] Errore interno nell'API api_vehicle_rent: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


