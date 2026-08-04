# (C) 2026 Francesco Settembrini

# import os
# import time
# import threading
# from django.apps import AppConfig
# from django.utils import timezone
# from datetime import timedelta
# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings  # Importiamo i settings di Django per verificare il flag DEBUG
#
#
# class RentalsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'rentals'
#
#     # Flag di controllo per impedire l'avvio di thread duplicati all'inizializzazione
#     _thread_started = False
#
#     def ready(self):
#         # Avvio universale sicuro: se il thread non è ancora partito, lo lancia ora
#         if not RentalsConfig._thread_started:
#             RentalsConfig._thread_started = True
#             print("=== [M2M THREAD] Avvio universale del monitoraggio asincrono flotta... ===")
#             monitor_thread = threading.Thread(target=self.start_rentals_monitor, daemon=True)
#             monitor_thread.start()
#
#     def start_rentals_monitor(self):
#         # Attesa iniziale di sicurezza per dare tempo a PostGIS di essere pronto
#         time.sleep(5)
#
#         # Import locale interno per evitare l'errore AppRegistryNotReady di Django
#         from rentals.models import Rental
#
#         while True:
#             try:
#                 now = timezone.now()
#
#                 # Questa stampa comparirà a terminale ad ogni singolo ciclo di controllo
#                 print(f"[{now.strftime('%H:%M:%S')}] [M2M THREAD] Analisi flotta in corso...")
#
#                 # =============================================================
#                 # POLICY 1: Timeout sblocco (Annullamento dopo 30 minuti dal pagamento)
#                 # =============================================================
#                 soglia_prenotazione = now - timedelta(minutes=30)
#                 expired_reservations = Rental.objects.filter(status='reserved', timestamp__lt=soglia_prenotazione)
#
#                 for rental in expired_reservations:
#                     print(f"[{now.strftime('%H:%M:%S')}] RITARDO PRENOTAZIONE: Annullamento Rental ID {rental.id}.")
#
#                     # Il noleggio hardware passa a cancelled, ma il pagamento resta incassato
#                     rental.status = 'cancelled'
#                     rental.save()
#
#                     # Il veicolo torna utilizzabile e disponibile per Bari, ma chiuso a chiave
#                     if rental.car:
#                         rental.car.is_available = True
#                         rental.car.is_locked = True
#                         rental.car.save()
#
#                     # Invio notifica e-mail transazionale in inglese per superamento tempo limite
#                     if rental.user:
#                         self.send_timeout_email(rental.user, rental)
#
#                 # =============================================================
#                 # POLICY 2: Fine tempo di guida (start_time + duration_minutes)
#                 # =============================================================
#                 active_rentals = Rental.objects.filter(status='active')
#
#                 for rental in active_rentals:
#                     # Verifica la scadenza a runtime calcolata in RAM dalla property
#                     if rental.is_expired:
#                         #print(f"[{now.strftime('%H:%M:%S')}] FINE CORSA: Tempo esaurito per Rental ID {rental.id}.")
#                         # Recuperiamo la targa in modo sicuro con un fallback se il mezzo fosse assente
#                         car_plate = rental.car.license_plate if rental.car else "N/A"
#
#                         # --- MODIFICA APPLICATA: Inserita la targa nel log di fine corsa ---
#                         print(
#                             f"[{now.strftime('%H:%M:%S')}] FINE CORSA: Tempo esaurito per Rental ID {rental.id} - Vehicle: {car_plate}")
#
#
#                         rental.status = 'completed'
#                         rental.actual_end_time = now
#                         rental.save()
#
#                         # Comando hardware M2M: blocco immediato portiere e reinserimento in flotta
#                         if rental.car:
#                             rental.car.is_locked = True
#                             rental.car.is_available = True
#                             rental.car.save()
#
#             except Exception as e:
#                 print(f"[ERRORE THREAD BACKGROUND]: {str(e)}")
#
#             # --- MODIFICA RICHIESTA: CONTROLLO INTERVALLO DINAMICO ---
#             # Se siamo in DEBUG (sviluppo locale) controlla ogni 10 secondi, altrimenti ogni 60 secondi
#             if settings.DEBUG:
#                 time.sleep(10)
#             else:
#                 time.sleep(60)
#
#     # =============================================================================
#     # Invia una mail su Mailpit avvisando l'utente del ritardo e della perdita dei soldi
#     # =============================================================================
#     def send_timeout_email(self, user, rental):
#         subject = f"Reservation Expired - Rental ID {rental.id}"
#         targa = rental.car.license_plate if rental.car else "N/A"
#
#         # Layout HTML per l'utente in casella di posta (rigorosamente in inglese)
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.4; }}
#                 .container {{ padding: 20px; border: 1px solid #e2e8f0; max-width: 500px; }}
#                 .danger-text {{ color: #dc2626; font-weight: bold; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h3>RentalCars s.r.l. - Bari</h3>
#                 <h2>Dear {user.username},</h2>
#                 <p>We are sorry to inform you that your reservation for the vehicle <strong>{targa}</strong> (Rental ID: {rental.id}) has been <span class="danger-text">automatically cancelled</span>.</p>
#                 <p>According to our corporate policy, users must unlock the vehicle within <strong>30 minutes</strong> from the payment transaction. Since this time limit has been exceeded, you have lost the rental rights and the amount already paid cannot be refunded.</p>
#                 <p>The vehicle has been successfully locked and re-introduced into our fleet for other customers.</p>
#                 <br>
#                 <p>Best regards,<br><strong>RentalCars Team</strong></p>
#             </div>
#         </body>
#         </html>
#         """
#         text_content = f"Dear {user.username},\n\nYour reservation for vehicle {targa} has been cancelled for exceeding the 30-minute limit."
#
#         # Prepara e spara l'email transazionale intercettata da Mailpit
#         email = EmailMultiAlternatives(subject, text_content, 'noreply@yourdomain.com', [user.email])
#         email.attach_alternative(html_content, "text/html")
#         email.send(fail_silently=True)
#         print(f"   [EMAIL SENT] Notifica di annullamento recapitata a {user.email}")


# (C) 2026 Francesco Settembrini

import os
from django.apps import AppConfig


class RentalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentals'

    # Flag di controllo per impedire l'avvio di thread duplicati all'inizializzazione
    _thread_started = False

    def ready(self):
        # Se l'Hub non è ancora partito, ordina il boot di tutti i demoni registrati
        if not RentalsConfig._thread_started:
            RentalsConfig._thread_started = True

            # Importazione e attivazione centralizzata dell'Hub dei monitor
            from rentals.async_monitors import launch_all_monitors
            launch_all_monitors()
