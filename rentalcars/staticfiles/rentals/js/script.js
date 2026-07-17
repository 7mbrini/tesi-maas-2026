// (C) 2026 Francesco Settembrini

// ==========================================
// ESECUZIONE (Punto di Partenza Unico)
// ==========================================
document.addEventListener("DOMContentLoaded", function ()
{
    initializeMap();

    // Sincronizzazione  dei dati
    syncUserPositionWithServer();
    renderCarMarkersFromDatabase();
});


// ==========================================
// variabili globali
// ==========================================
let map;
let userMarker;
let carMarkerGroup;

// Connettore principale al Form HTML
const mainForm = document.getElementById('mainForm');

// ==========================================
// FUNZIONE DI INIZIALIZZAZIONE (Setup)
// ==========================================
function initializeMap()
{
    // Parametri di fallback predefiniti (Bari)
    let initialZoom = 15;
    let initialCoords = [41.12, 16.87];

    // Lettura sicura dello stato precedente dai campi nascosti Django
    const elZoom = document.getElementById('id_map_zoom');
    const elCenter = document.getElementById('id_map_center');
    const savedZoom = (elZoom && elZoom.value) ? elZoom.value : "15";
    const savedCenter = (elCenter && elCenter.value) ? elCenter.value : "41.12,16.87";

    if (savedZoom && savedZoom !== "") { initialZoom = parseInt(savedZoom); }
    if (savedCenter && savedCenter !== "") { initialCoords = savedCenter.split(',').map(Number); }

    // Creazione dell'istanza Leaflet
    map = L.map('RentalsMap', { center: initialCoords, zoom: initialZoom, minZoom: 10, maxZoom: 18 });

    // Configurazione e caricamento del Tile Layer (OpenStreetMap protetto)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        referrerPolicy: 'no-referrer-when-downgrade'
    }).addTo(map);

    // Setup del Marker Posizione Utente (Trascina e Clicca)
    userMarker = L.marker(initialCoords, { draggable: true }).addTo(map);
    userMarker.bindPopup("Your Position");

    // Inizializzazione del gruppo per le auto spaziali
    carMarkerGroup = L.layerGroup();
    map.addLayer(carMarkerGroup);

    // Registrazione degli eventi di interazione
    map.on('click', onMapClick);
}

// ==========================================
// GESTIONE EVENTI MAPPA (Interazioni)
// ==========================================
function onMapClick(e)
{
    userMarker.setLatLng(e.latlng);
}

// ==========================================
// ELABORAZIONE DATI GEOGRAFICI (MaaS Logica)
// ==========================================

// Forza il Pin dell'utente sulle coordinate reali inviate dal Backend
function syncUserPositionWithServer()
{
    const jsonElement = document.getElementById('json-userPos');

    if (jsonElement && jsonElement.textContent) {
        try {
            const markerPos = JSON.parse(jsonElement.textContent);
            const lat = parseFloat(markerPos.lat);
            const lon = parseFloat(markerPos.lon);

            userMarker.setLatLng([lat, lon]);
        } catch (e) {
            console.error("Error parsing user position JSON:", e);
        }
    }
}

// Disegna le icone SVG vettoriali delle auto estratte dalla Query Spaziale
function renderCarMarkersFromDatabase()
{
    const jsonElement = document.getElementById('json-selCars');

    if (jsonElement && jsonElement.textContent)
    {
        try {
            carMarkerGroup.clearLayers();
            const selectedCars = JSON.parse(jsonElement.textContent);

            // Configurazione dell'icona personalizzata per la flotta veicoli
            const carIcon = L.divIcon({
                html: `
                    <div style="background-color: #00aa00; width: 36px; height: 36px; border-radius: 8px;
                     border: 2px solid #ffffff; box-shadow: 0 3px 6px rgba(0,0,0,0.3); display: flex;
                     align-items: center; justify-content: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="24" height="24">
                            <path fill="#ffffff" d="M496 224h-18.3l-28.5-95.1c-8.9-29.6-36.3-50.1-67.2-50.1H129.9c-30.9
                            0-58.3 20.5-67.2 50.1L34.3 224H16c-8.8 0-16 7.2-16 16v88c0 13.3 10.7 24 24 24h16v56c0 13.3 10.7
                            24 24 24h40c13.3 0 24-10.7 24-24v-56h256v56c0 13.3 10.7 24 24 24h40c13.3 0 24-10.7 24-24v-56h16c13.3
                            0 24-10.7 24-24v-88c0-8.8-7.2-16-16-16zm-361.3-113c2.2-7.4 9.1-12.5 16.9-12.5h204.8c7.8 0 14.6 5.1
                            16.9 12.5L398.9 200H113.1l21.6-89zM88 288c-13.3 0-24-10.7-24-24s10.7-24 24-24 24 10.7 24 24-10.7
                            24-24 24zm336 0c-13.3 0-24-10.7-24-24s10.7-24 24-24 24 10.7 24 24-10.7 24-24 24zm44-48H44v-16h424v16z"/>
                        </svg>
                    </div>
                `,
                className: 'custom-car-marker',
                iconSize: [40, 40],
                iconAnchor: [20, 20],
                popupAnchor: [0, -20]
            });

            // Posizionamento puntuale dei marker sul Layer specifico
            selectedCars.forEach(car => {
                L.marker([car.lat, car.lon], { icon: carIcon })
                    .addTo(carMarkerGroup)
                    .bindPopup(`<b>License Plate:</b> ${car.license_plate}`);
            });

        } catch (e) {
            console.error("Error parsing cars JSON:", e);
        }
    } else {
        console.log("Nessun dato JSON 'json-selCars' trovato nel DOM o l'elemento è vuoto.");
    }
}

// ==========================================
// AGGIORNAMENTO AGGIUNTIVO: SUBMIT FORM
// ==========================================
if (mainForm)
{
    mainForm.addEventListener('submit', function ()
    {
        const coords = userMarker.getLatLng();

        // Sincronizza le coordinate reali per inviarle a PostGIS via Django Form
        document.getElementById('id_hidden_decimal_lat').value = coords.lat.toFixed(6);
        document.getElementById('id_hidden_decimal_lon').value = coords.lng.toFixed(6);

        // Preserva lo stato visivo di Zoom e Centro della mappa per il ricaricamento
        document.getElementById('id_map_zoom').value = map.getZoom();

        const currentCenter = map.getCenter();
        document.getElementById('id_map_center').value = currentCenter.lat.toFixed(6) + ',' + currentCenter.lng.toFixed(6);
    });
}

