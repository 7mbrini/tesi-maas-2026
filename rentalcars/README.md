

RentalCars - (C) 2026 Francesco Settembrini

Progetto per la mia Tesi di Laurea (Project Work)
presso l'Universita' Telematica UniPegaso.


Istruzioni per il setup.

Il progetto fa uso dei container Docker.
Occorre avere installato ed avviato il servizio (daemon)
Docker sul proprio sistema.

Fare il download dell'intero progetto zip, scompattarlo
in una directory di preferenza, avviare una command line
o power-shell di Windows, posizionarsi nella directory
del progetto (dove c'e' il file docker-compose.yml) e, per
Windows, digitare il seguente comando :

docker-compose build up -d

Per Linux digitare il seguente comando:

docker compose build up -d

Verranno scaricate le immagini dal repository ufficiale,
creati i containers ed avviato il database PostGIS.

Al termine del setup aprire sul browser il seguente link:

http://localhost:8000


Dovra' apparire il sito web del progetto.

Il database inizialmente e' vuoto.
Per popolare il database con dati di prova
inserire la seguente url :

http://localhost:8000/tools

e creare il database premendo il pulsante 
"create cars table".

Quindi, per vedere sulla mappa la flotta dei
veicoli, aprire il seguente link:

http://localhost:8000/fleet/

Dovra' apparire la mappa dei veicoli con le
relative schede informative.

Per simulare il noleggio di un autoveicolo
aprire il link :

http://localhost:8000/rentals


Il marker blu rappresenta la posizione dell'utente.
Per posizionare il marker fare click sulla mappa
o trascinare il marker.

Selezionare le caratteristiche dell'autoveicolo
desiderato ed avviare la query.

Se ci saranno autoveicoli che soddisfano il
criterio di ricerca si potra' avviare la procedura
di noleggio cliccando sul pulsante "Rent Now".

La procedura di acquisto e' solo simulata per cui
le informazioni relative alla carta di credito
sono fittizie.

Per procedere all'acquisto occorre essersi registrati.

Per il login come amministratore (Django) usare :

username: admin

password: admin

Per entrare nella dashboard di amministratore
inserire la seguente url:

http://localhost:8000/admin


Si avra' accesso a database utenti, autoveicoli
e transazioni commerciali relative al noleggio.

Per accedere direttamente al database PostgreSQL
il container Docker e' settato sulla porta 5432
con le seguenti proprieta':

nome: rentalcars

user: posgtres

password: postgres

Per ulteriori dettagli relativi al setup consultare
i files Dockerfile, docker-compose.yml e settings.py










