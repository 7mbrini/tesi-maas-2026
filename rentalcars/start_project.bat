@echo off
echo Inizializzazione dell'ambiente locale in corso...
:: Esegue il build e avvia i container leggendo solo il file di sviluppo
docker compose -f docker-compose-dev.yml up -d --build
echo.
echo ===================================================
echo  Applicazione avviata correttamente.
echo  Pannello di controllo: http://localhost:8510/admin
echo ===================================================
pause
