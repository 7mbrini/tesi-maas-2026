#!/bin/bash
echo "Inizializzazione dell'ambiente locale in corso..."
# Avvia i container e gestisce i comandi sh -c interni in totale autonomia
docker compose -f docker-compose-dev.yml up -d --build
echo ""
echo "==================================================="
echo " Applicazione avviata correttamente."
echo " Pannello di controllo: http://localhost:8520/admin"
echo "==================================================="
