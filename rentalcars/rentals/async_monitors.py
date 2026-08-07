# (C) 2026 Francesco Settembrini
# HUB CENTRALIZZATO DEI MONITOR ASINCRONI E PARALLELI (MaaS Enterprise Architecture)

import time
import threading
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.conf import settings  # Per verifivehiclee il flag settings.DEBUG
from django import db  # <--- IMPORTANTE: Necessario per governare i canali del Database


def send_timeout_email(user, rental):
    """Invia una mail su Mailpit avvisando l'utente del ritardo e della perdita del denaro."""
    subject = f"Reservation Expired - Rental ID {rental.id}"
    targa = rental.vehicle.license_plate if rental.vehicle else "N/A"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.4; }}
            .container {{ padding: 20px; border: 1px solid #e2e8f0; max-width: 500px; }}
            .danger-text {{ color: #dc2626; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h3>RentalCars s.r.l. - Bari</h3>
            <h2>Dear {user.username},</h2>
            <p>We are sorry to inform you that your reservation for the vehicle <strong>{targa}</strong> (Rental ID: {rental.id}) has been <span class="danger-text">automatically cancelled</span>.</p>
            <p>According to our corporate policy, users must unlock the vehicle within <strong>30 minutes</strong> from the payment transaction. Since this time limit has been exceeded, you have lost the rental rights and the amount already paid cannot be refunded.</p>
            <p>The vehicle has been successfully locked and re-introduced into our fleet for other customers.</p>
            <br>
            <p>Best regards,<br><strong>RentalCars Team</strong></p>
        </div>
    </body>
    </html>
    """
    text_content = f"Dear {user.username},\n\nYour reservation for vehicle {targa} has been cancelled for exceeding the 30-minute limit."

    email = EmailMultiAlternatives(subject, text_content, 'noreply@yourdomain.com', [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)
    print(f"   [EMAIL SENT] Notifica di annullamento recapitata a {user.email}")


def start_rentals_monitor():
    """MONITOR 1: Ciclo continuo del thread di controllo delle scadenze commerciali e hardware."""
    # Attesa iniziale per garantire che il database PostGIS sia pronto
    time.sleep(5)

    # Import locale interno per evitare l'errore AppRegistryNotReady all'avvio di Django
    from rentals.models import Rental

    while True:
        try:
            # --- PROTEZIONE THREAD STEP 1: Chiude i canali sporchi o obsoleti prima di interrogare PostGIS ---
            db.close_old_connections()

            now = timezone.now()

            # Stampa di presenza continua ad ogni ciclo di verifica
            print(f"[{now.strftime('%H:%M:%S')}] [M2M HUB THREAD] Analisi flotta in corso...")

            # =============================================================
            # POLICY 1: Timeout sblocco (Annullamento dopo 30 minuti dal pagamento)
            # =============================================================
            soglia_prenotazione = now - timedelta(minutes=30)
            expired_reservations = Rental.objects.filter(status='reserved', timestamp__lt=soglia_prenotazione)

            for rental in expired_reservations:
                print(f"[{now.strftime('%H:%M:%S')}] RITARDO PRENOTAZIONE: Annullamento Rental ID {rental.id}.")

                rental.status = 'cancelled'
                rental.save()

                if rental.vehicle:
                    rental.vehicle.is_available = True
                    rental.vehicle.is_locked = True
                    rental.vehicle.save()

                if rental.user:
                    send_timeout_email(rental.user, rental)

            # =============================================================
            # POLICY 2: Fine tempo di guida (start_time + duration_minutes)
            # =============================================================
            active_rentals = Rental.objects.filter(status='active')

            for rental in active_rentals:
                if rental.is_expired:
                    vehicle_plate = rental.vehicle.license_plate if rental.vehicle else "N/A"
                    print(
                        f"[{now.strftime('%H:%M:%S')}] FINE CORSA: Tempo esaurito per Rental ID {rental.id} - Vehicle: {vehicle_plate}")

                    rental.status = 'completed'
                    rental.actual_end_time = now
                    rental.save()

                    if rental.vehicle:
                        rental.vehicle.is_locked = True
                        rental.vehicle.is_available = True
                        rental.vehicle.save()

        except Exception as e:
            print(f"[ERRORE THREAD BACKGROUND]: {str(e)}")

        finally:
            # --- PROTEZIONE THREAD STEP 2: Rilascia la connessione prima di andare in sleep ---
            # Evita la saturazione del pool di connessioni di PostgreSQL sulla porta 5510
            db.close_old_connections()

        # Intervallo dinamico: 10 secondi in sviluppo (DEBUG), 60 secondi in produzione
        if settings.DEBUG:
            time.sleep(10)
        else:
            time.sleep(60)


# =============================================================================
# INIZIALIZZATORE DELL'HUB (Lancia tutti i monitor registrati)
# =============================================================================
def launch_all_monitors():
    """Inizializza e lancia in parallelo tutti i thread demoni registrati nell'Hub."""
    print("=== [M2M HUB] Inizializzazione di tutti i monitor asincroni da async_monitors.py... ===")

    # Lancio del Monitor 1 (Gestione scadenze flotta e noleggi)
    rentals_thread = threading.Thread(target=start_rentals_monitor, daemon=True)
    rentals_thread.start()
