# (C) 2026 Francesco Settembrini

from django.shortcuts import render, redirect
from decimal import Decimal, InvalidOperation
from .forms import RentalsForm

import os
import psycopg2
from psycopg2.extras import RealDictCursor

from django.conf import settings

from cars.models import Car


# =============================================================================
# Restituisca la connessione al database PosgreSQL (PostGIS)
# =============================================================================
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
# # =============================================================================
# # Restituisca la connessione al database PosgreSQL (PostGIS)
# # =============================================================================
def get_db_connection():
    # Preleviamo la configurazione reale del database calcolata da Django
    db_config = settings.DATABASES['default']

    # Apriamo una connessione psycopg2 cruda usando ESATTAMENTE i valori calcolati
    connection = psycopg2.connect(
        dbname=db_config['NAME'],  # Sarà 'rentalbikes' grazie al fallback!
        user=db_config['USER'],  # 'postgres'
        password=db_config['PASSWORD'],  # 'postgres'
        host=db_config['HOST'],  # 'db'
        port=db_config['PORT'],  # '5432'
    )
    return connection


# =============================================================================
# Gestisce la richiesta di noleggio
# =============================================================================
def rentals_view(request):
                                        # richiesta POST
    if request.method == 'POST':
        form = RentalsForm(request.POST)
                                        # lat e lon sono campi aggiuntivi
                                        # non fanno parte della form ma sono
                                        # stati creati come "campi nascosti"
        raw_decimal_lat = request.POST.get('hidden_decimal_lat', '')
        raw_decimal_lon = request.POST.get('hidden_decimal_lon', '')

        decimal_lat_value = None
        decimal_lon_value = None
        backend_error = None

        try:
            user_lat = Decimal(raw_decimal_lat)
            user_lon = Decimal(raw_decimal_lon)
        except InvalidOperation:
            backend_error = "One of the hidden decimal values was invalid."

                                        # Verifica la validita' degli input
        if form.is_valid() and backend_error is None:

            choice_seats = form.cleaned_data['listbox_seats']
            choice_doors = form.cleaned_data['listbox_doors']
            buffer_radius = form.cleaned_data['buffer']

            connection = None
            try:
                connection = get_db_connection()

                                            # Usa RealDictCursor per ottenere
                                            # il risultato come dizionario
                cursor = connection.cursor(cursor_factory=RealDictCursor)

                                            # esegue la "spatial query" (buffer)
                spatial_query = """
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
                    AND doors >= %s
                    AND seats >= %s
                    AND available = TRUE
                    ORDER BY distance_meters ASC;
                """
                                        # esegue la query
                cursor.execute(spatial_query,
                    (user_lon, user_lat, user_lon, user_lat,
                    buffer_radius, choice_doors, choice_seats, ))

                selCars = cursor.fetchall()
                #os.system('cls')
                #print(selCars)

            except (Exception, psycopg2.Error) as error:
                print(f"Error while fetching spatial data: {error}")
                return render(request, 'rentals/rentals.html', {'form':form})

            finally:
                if connection:
                    cursor.close()
                    connection.close()

            userPos = { 'lat': user_lat, 'lon': user_lon }
            context = { 'form':form, 'selCars':selCars, 'userPos': userPos }

            return render(request, 'rentals/rentals.html', context)

                                            # restituisce la form aggiornata
        context = {'form': form, 'error': backend_error}

        return render(request, 'rentals/rentals.html', context)

                                            # richiesta GET (primo caricamento della pagina)
    else:
        form = RentalsForm()

    return render(request, 'rentals/rentals.html', {'form': form})



