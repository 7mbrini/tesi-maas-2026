# (C) 2026 Francesco Settembrini

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db import transaction  # Per rendere atomica la creazione

import os
import decimal
import io
import base64
import uuid
import qrcode
import string

from django.http import HttpResponse
from django.utils import timezone

from xhtml2pdf import pisa
from django.core.mail import EmailMultiAlternatives

# IMPORTAZIONI CORRETTE DELLE DUE APP
from rentals.models import Rental
from payments.models import PaymentTransaction  # Il nostro nuovo modello finanziario
from cars.models import Car
from .forms import PaymentInitiateForm, PaymentPayForm

from utils.logs import log_print, log_clear


# =============================================================================
# Gestisce il pagamento del noleggio relativo al veicolo car_id
# =============================================================================
def payment_initiate(request, car_id):
    # Usiamo get_object_or_404 per evitare IndexError se l'id non esiste
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = PaymentInitiateForm(request.POST)

        if form.is_valid():
            # Converte in ore e calcola l'importo parziale e totale
            minutes = form.cleaned_data['rental_duration_minutes']
            total_hours = float(minutes) / 60.0

            # Scomposizione analitica dei costi per la trasparenza utente
            unlock_cost = float(car.unlock_cost)
            time_cost = float(car.hourly_rate) * total_hours
            total_amount = unlock_cost + time_cost

            # Memorizza l'importo e i dettagli del calcolo nella sessione (Formato stringa a 2 decimali)
            request.session['pending_amount'] = f"{total_amount:.2f}"
            request.session['unlock_cost_breakdown'] = f"{unlock_cost:.2f}"
            request.session['time_cost_breakdown'] = f"{time_cost:.2f}"

            # Informazioni di contesto del noleggio
            request.session['rental_duration_minutes'] = minutes
            request.session['license_plate'] = car.license_plate
            request.session['selected_car_id'] = car.id

            return redirect('payment_pay')
    else:
        form = PaymentInitiateForm()

        context = {
            'form': form,
            'car_plate': car.license_plate
        }

    return render(request, 'payments/payment_initiate.html', context)


# =============================================================================
# Sottopone la form di pagamento: numero di carta, data scadenza, importo, ecc...
# =============================================================================
@login_required
def payment_pay(request):
    # Recupera l'importo calcolato in base al tempo effettivo
    pending_amount = request.session.get('pending_amount', '0.00')

    if request.method == 'POST':
        form = PaymentPayForm(request.POST)
        if form.is_valid():
            #request.session['pending_amount'] = str(form.cleaned_data['amount'])
            #request.session['pending_amount'] = str(form.cleaned_data['pending_amount'])
            request.session['pending_amount'] = pending_amount
            return redirect('payment_process')
    else:
        initial_data = {
            'amount': request.session.get('pending_amount', '0.00'),
        }
        form = PaymentPayForm(initial=initial_data)

    # --- CORREZIONE: Estraiamo i dati dalla sessione e creiamo il contesto completo ---
    context = {
        'form': form,
        'unlock_cost': request.session.get('unlock_cost_breakdown', '0.00'),
        'time_cost': request.session.get('time_cost_breakdown', '0.00'),
        'duration_minutes': request.session.get('rental_duration_minutes', 0),
        'license_plate': request.session.get('license_plate', ''),
    }

    return render(request, 'payments/payment_pay.html', context)

# =============================================================================
# Memorizza la transazione di pagamento nel database e prepara i dati per il successo
# =============================================================================
@login_required
def payment_process(request):
    amount_str = request.session.get('pending_amount')
    duration_minutes = request.session.get('rental_duration_minutes', 60)
    car_id = request.session.get('selected_car_id')

    if not amount_str or not car_id:
        messages.error(request, "No pending transaction or vehicle found.")
        return redirect('payment_initiate', car_id=car_id if car_id else 1)

    try:
        amount_decimal = decimal.Decimal(amount_str)
        car = get_object_or_404(Car, id=car_id)

        # RIMOZIONE DEL VECCHIO ERRORE: Logica atomica disaccoppiata
        with transaction.atomic():
            # 1. Creiamo il Rental passandogli i suoi soli parametri validi
            new_rental = Rental.objects.create(
                user=request.user,
                car=car,
                status='reserved',
                duration_minutes=duration_minutes
            )

            # 2. Creiamo la PaymentTransaction agganciata al Rental
            new_transaction = PaymentTransaction.objects.create(
                rental=new_rental,
                user=request.user,
                amount=amount_decimal,
                status='completed',
                is_paid=True,
                gateway_transaction_id=str(uuid.uuid4())
            )

            # 3. Aggiorniamo la disponibilità dell'auto per bloccarla sul server
            car.is_available = False
            car.save()

        token = new_rental.check_code

        # Genera il QR Code in memoria (Formato PNG)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()

        # Inietta il QR Code convertito in Base64 nella sessione per la pagina di successo
        request.session['success_qr_base64'] = base64.b64encode(qr_bytes).decode('utf-8')

        license_plate = request.session.get('license_plate', car.license_plate)

        # Invia l'e-mail di conferma protetta da un try/except locale per isolare gli errori SMTP
        try:
            send_confirmation_email(request.user, new_rental, token, license_plate, qr_bytes)
        except Exception as mail_err:
            print(f"[WEB] Errore non bloccante nell'invio della mail: {str(mail_err)}")

        # Pulizia della sessione
        request.session.pop('pending_amount', None)
        request.session.pop('rental_duration_minutes', None)
        request.session.pop('selected_car_id', None)

        return redirect(reverse('payment_success', args=[token]))

    except decimal.InvalidOperation:
        messages.error(request, "Invalid amount format. Transaction failed.")
        return redirect('payment_failure')

    except Exception as e:
        messages.error(request, f"A database error occurred: {e}. Transaction failed.")
        return redirect('payment_failure')

# =============================================================================
# Gestisce il pagamento avvenuto con successo
# =============================================================================
@login_required
def payment_success(request, token):
    # .pop() estrae il valore e CANCELLA la chiave dalla sessione in un colpo solo, in modo atomico
    qr_base64 = request.session.pop('success_qr_base64', '')
    license_plate = request.session.pop('license_plate', '')

    context = {
        'token': token,
        'qr_base64': qr_base64,
        'license_plate': license_plate,
    }
    return render(request, 'payments/payment_success.html', context)


# =============================================================================
# Gestisce il pagamento avvenuto con insuccesso
# =============================================================================
@login_required
def payment_failure(request):
    return render(request, 'payments/payment_failure.html')


# =============================================================================
# Email di conferma col QR-Code di sblocco e codice per tastierino
# =============================================================================
def send_confirmation_email(user, rental, token, license_plate, qr_bytes):
    subject = "Payment Confirmation - Unlock Ticket"
    qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')

    # Recuperiamo la transazione finanziaria correlata per estrarre l'importo
    tx = rental.transactions.first()
    amount_val = tx.amount if tx else "0.00"

    context = {
        'user': user,
        'rental': rental,
        'token': token,
        'qr_base64': qr_base64
    }

    # Stringa HTML inline compattata in memoria
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .box {{ border: 2px dashed #007bff; padding: 20px; text-align: center; max-width: 400px; margin: 20px; }}
        </style>
    </head>
    <body>
        <h3> RentalCars s.r.l. - Bari Corso Cavour 123 <h3><br>
        <h2>Thank you for your purchase, {user.username}!</h2>
        <p>Your payment of <strong>€{amount_val}</strong> has been processed successfully.</p>

        <div class="box">
            <h4>You are allowed to use the vehicle</h4>
            </p><h2><strong>{license_plate}</strong></h2></p>
        </div>

        <div class="box">
            <h3>YOUR UNLOCK CODE</h3>
            <p><h2><strong>{token}</strong></h2></p>
        </div>

        <div class="box">
            <h3>YOUR QR CODE</h3>
            <img src="data:image/png;base64,{qr_base64}" width="200" height="200" alt="QR Code"><br>
        </div>

        <div>
            <h3>
            <p><br>Scan the QR CODE on the reader or enter the UNLOCK CODE on the vehicle keypad.</p>
            <p><br><br>Best regards, RentalCars Team.</p>
            </h3>
        </div>
    </body>
    </html>
    """
    html_content = html_template

    text_content = (
        f"Thanks to appreciate our services {user.username}.\n"
        f"Your unlock code is: {token}\n"
        f"You can scan the attached QR-Code or type this numeric code directly on the vehicle's keypad."
    )

    email = EmailMultiAlternatives(
        subject,
        text_content,
        'noreply@yourdomain.com',
        [user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.attach(f'ticket_{token}.png', qr_bytes, 'image/png')

    # Gestisce già nativamente i timeout se Mailpit dovesse essere spento
    email.send(fail_silently=True)


# =============================================================================
# Genera al volo e scarica il report PDF in memoria senza salvare file
# =============================================================================
@login_required
def download_ticket_pdf(request, token, license_plate):
    """Genera al volo e scarica il report PDF in memoria senza salvare file"""
    # Recupera la transazione dal database tramite il token
    rental = get_object_or_404(Rental, check_code=token, user=request.user)

    # Recupera la transazione finanziaria correlata dal nuovo modello payments
    tx = rental.transactions.first()
    amount_val = tx.amount if tx else "0.00"
    gateway_id = tx.gateway_transaction_id if tx else "N/A"

    # Rigenera il QR code specifico in memoria per il layout del PDF
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_buffer = io.BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

    current_timestamp = timezone.now().strftime("%d/%m/%Y %H:%M")

    # Stringa HTML del PDF (rigorosamente in inglese per l'utente)
    pdf_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: letter;
                margin: 15mm;
            }}
            body {{ 
                font-family: Helvetica, Arial, sans-serif; 
                color: #333; 
                font-size: 14px; 
                line-height: 1.2;
            }}
            .header {{ text-align: center; margin-bottom: 10px; }}
            .header h3 {{ margin: 2px 0; font-size: 16px; font-weight: normal; color: #555; }}

            .bg-black-header {{
                background-color: #000000;
                color: #ffffff;
                text-align: center;
                padding: 10px 0;
                margin-top: 5px;
                margin-bottom: 15px;
            }}
            .bg-black-header h1 {{ 
                margin: 0; 
                font-size: 22px; 
                font-weight: bold;
                letter-spacing: 0.5px;
            }}

            .info-table {{ width: 100%; margin-top: 15px; margin-bottom: 15px; border-collapse: collapse; }}
            .info-table td {{ padding: 6px 10px; font-size: 14px; border-bottom: 1px solid #ddd; }}

            .qr-container {{ text-align: center; margin-top: 20px; margin-bottom: 20px; }}
            .qr-container h2 {{ font-size: 16px; line-height: 1.2; margin-top: 0; margin-bottom: 10px; color: #111; }}
            .qr-code {{ width: 220px; height: 220px; }}

            .footer-signature {{ 
                text-align: left; 
                margin-top: 25px; 
                font-size: 16px; 
                color: #555; 
                font-weight: bold; 
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h3>RentalCars s.r.l. - Bari Corso Cavour 123</h3>
        </div>

        <div class="bg-black-header">
            <h1>RECEIPT &amp; UNLOCK TICKET</h1>
        </div>

        <table class="info-table">
            <tr>
                <td><strong>Date:</strong></td>
                <td>{current_timestamp}</td>
            </tr>
            <tr>
                <td><strong>User:</strong></td>
                <td>{request.user.username} ({request.user.email})</td>
            </tr>
            <tr>
                <td><strong>Total Amount:</strong></td>
                <td>&euro;{amount_val}</td>
            </tr>
            <tr>
                <td><strong>Transaction Status:</strong></td>
                <td>Completed</td>
            </tr>
            <tr>
                <td><strong>Unique Transaction ID:</strong></td>
                <td>{gateway_id}</td>
            </tr>
            <tr>
                <td><strong>Vehicle License Plate:</strong></td>
                <td>{license_plate}</td>
            </tr>
            <tr>
                <td><strong>Unlock Code:</strong></td>
                <td>{rental.check_code}</td>
            </tr>
        </table>

        <div class="qr-container">
            <h2>SCAN THIS QR CODE ON THE READER<br>OR ENTER THE UNLOCK CODE ON THE VEHICLE KEYPAD</h2>
            <img class="qr-code" src="data:image/png;base64,{qr_base64}" />
        </div>

        <div class="footer-signature">
            Best regards, RentalCars Team.
        </div>
    </body>
    </html>
    """

    # Prepara la risposta HTTP di tipo PDF forzando il download
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{token}.pdf"'

    # Renderizza il PDF in memoria usando xhtml2pdf (pisa)
    pisa_status = pisa.CreatePDF(pdf_template, dest=response)

    # Gestione dell'errore di rendering
    if pisa_status.err:
        return HttpResponse('An error occurred while generating your PDF ticket.', status=500)

    return response
