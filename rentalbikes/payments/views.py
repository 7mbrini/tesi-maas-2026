# (C) 2025 Francesco Settembrini

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import uuid  # Helper per la generazione di un GUID

import os
import decimal
from django.http import HttpResponse

from .models import Transaction
from cars.models import Car
from .forms import PaymentInitiateForm, PaymentPayForm

# =============================================================================
# Gestisce il pagamento del noleggio relativo al veicolo car_id
# =============================================================================
def payment_initiate(request, car_id):

    car = Car.objects.all().filter(id = car_id)[0]

    if request.method == 'POST':
        form = PaymentInitiateForm(request.POST)

        if form.is_valid():
                                            # converte in ore e calcola l'importo
            str_minutes =  str(form.cleaned_data['rental_duration_minutes'])
            total_hours = float(str_minutes) / 60.0
            amount = float(car.hourly_rate) * total_hours
                                            # memorizza l'importo nella sessione
            request.session['pending_amount'] = amount

            return redirect('payment_pay')
    else:
        form = PaymentInitiateForm()

        context = {
            'form': form,
            'car_plate': car.license_plate  # The plate of the car being rented
        }

    return render(request, 'payments/payment_initiate.html', context)


# =============================================================================
# Sottopone la form di pagamento: numero di carta, data scadenza, importo, ecc...
# =============================================================================
@login_required     # richiede che l'utente sia loggato
def payment_pay(request):

    if request.method == 'POST':
        form = PaymentPayForm(request.POST)
        if form.is_valid():

            request.session['pending_amount'] = str(form.cleaned_data['amount'])

            return redirect('payment_process')
    else:
        initial_data = {
            'amount' : request.session['pending_amount'],
        }

        form = PaymentPayForm(initial=initial_data)

    return render(request, 'payments/payment_pay.html', {'form': form})


# =============================================================================
# Memorizza la transazione di pagamento nel database
# =============================================================================
@login_required
def payment_process(request):

    amount_str = request.session.get('pending_amount')

    if not amount_str:
        messages.error(request, "No pending transaction found.")
        return redirect('payment_initiate')

    try:
        amount_decimal = decimal.Decimal(amount_str)

                                            # memorizza la transazione nel database
        new_transaction = Transaction.objects.create(
            user = request.user,
            amount = amount_decimal,
            transaction_status = 'completed', # simula che la transazione sia avvenuta con successo
            gateway_transaction_id = str(uuid.uuid4()) # Example unique ID
        )
                                            # cancella i valori memorizzati
                                            # temporaneamente nella sessione
        del request.session['pending_amount']
                                            # eventuale feedback per l'utente
        #messages.success(request, "Transaction successfully recorded in the database.")

        token = new_transaction.check_code
                                            # eventuale feedback per l'utente
        #messages.success(request, f"Transaction recorded. Your code is: {token}")

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
    return render(request, 'payments/payment_success.html', {'token': token} )

# =============================================================================
# Gestisce il pagamento avvenuto con insuccesso
# =============================================================================
@login_required
def payment_failure(request):
    return render(request, 'payments/payment_failure.html')

