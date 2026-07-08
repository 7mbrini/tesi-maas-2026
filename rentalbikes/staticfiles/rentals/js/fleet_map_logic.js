// (C) 2025 Francesco Settembrini

// --- Variabili Globali ---
let map;
let userMarker, destMarker;
let allCarsData = [];
let currentCarMarkers = [];
let currentMode = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    getUserLocation();
    fetchCarData();

    document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
    document.getElementById('setDestBtn').addEventListener('click', () => setPointMode('destination'));
    map.on('click', onMapClick);
});

function initializeMap() {
    map = L.map('mapid').setView([41.1171, 16.8718], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="www.openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);
}

function getUserLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                document.getElementById('userLocationStatus').textContent = `Posizione utente: [${lat.toFixed(3)}, ${lng.toFixed(3)}]`;

                if (userMarker) map.removeLayer(userMarker);
                userMarker = L.marker([lat, lng], {icon: L.icon({
                    iconUrl: 'cdn.rawgit.com',
                    shadowUrl: 'cdnjs.cloudflare.com',
                    iconSize:, iconAnchor:, popupAnchor: [1, -34], shadowSize:
                })}).addTo(map).bindPopup("La tua posizione (A)").openPopup();

                map.setView([lat, lng], 13);
                applyFilters();
            },
            (error) => {
                console.error("Errore GeoLocation:", error);
                document.getElementById('userLocationStatus').textContent = "Posizione utente: Non disponibile.";
                applyFilters();
            }
        );
    } else {
        document.getElementById('userLocationStatus').textContent = "GeoLocation non supportato.";
        applyFilters();
    }
}

function fetchCarData() {
    fetch('/cars/api/details/')
        .then(response => response.json())
        .then(data => {
            allCarsData = data;
            applyFilters();
        })
        .catch(error => console.error('Errore nel recupero dati auto:', error));
}

function applyFilters() {
    let filteredCars = allCarsData.filter(car => {
        const selectedDoors = document.getElementById('doorsFilter').value;
        if (selectedDoors !== 'all' && car.doors !== parseInt(selectedDoors)) return false;
        const minSeats = parseInt(document.getElementById('seatsFilter').value);
        if (car.seats < minSeats) return false;
        const minRange = parseInt(document.getElementById('rangeFilter').value);
        if (car.range_km < minRange) return false;

        if (userMarker && destMarker) {
            const from = userMarker.getLatLng();
            const to = destMarker.getLatLng();
            const distanceKm = calculateDistanceHaversine(from.lat, from.lng, to.lat, to.lng);
            if (car.range_km < distanceKm * 1.1) return false;
        }
        return true;
    });
    renderCarMarkers(filteredCars);
}

function renderCarMarkers(carsToRender) {
    currentCarMarkers.forEach(marker => map.removeLayer(marker));
    currentCarMarkers = [];

    carsToRender.forEach(car => {
        const lon = car.location.coordinates;
        const lat = car.location.coordinates;
        const markerHtml = `<strong>${car.license_plate}</strong><br>Tariffa: €${car.hourly_rate}<br>Autonomia: ${car.range_km} km`;

        let markerColor = 'green';
        if (userMarker) {
            const userLatLon = userMarker.getLatLng();
            const carDistance = calculateDistanceHaversine(userLatLon.lat, userLatLon.lng, lat, lon);
            if (carDistance < 5) markerColor = 'gold';
        }

        const carIcon = L.icon({
            iconUrl: `cdn.rawgit.com{markerColor}.png`,
            shadowUrl: 'cdnjs.cloudflare.com',
            iconSize:, iconAnchor:, popupAnchor: [1, -34], shadowSize:
        });

        const marker = L.marker([lat, lon], {icon: carIcon}).bindPopup(markerHtml);
        marker.addTo(map);
        currentCarMarkers.push(marker);
    });
}

function setPointMode(mode) {
    currentMode = mode;
    alert(`Clicca sulla mappa per impostare il punto di arrivo (B).`);
}

function onMapClick(e) {
    if (currentMode === 'destination') {
        if (destMarker) map.removeLayer(destMarker);
        destMarker = L.marker(e.latlng, {icon: L.icon({
            iconUrl: 'cdn.rawgit.com',
            shadowUrl: 'cdnjs.cloudflare.com',
            iconSize:, iconAnchor:, popupAnchor: [1, -34], shadowSize:
        })}).addTo(map).bindPopup("Arrivo (B)").openPopup();
        currentMode = null;
        calculateAndDisplayDistance();
        applyFilters();
    }
}

function calculateDistanceHaversine(lat1, lon1, lat2, lon2) {
    function deg2rad(deg) { return deg * (Math.PI / 180); }
    var R = 6371;
    var dLat = deg2rad(lat2 - lat1);
    var dLon = deg2rad(lon2 - lon1);
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    var d = R * c;
    return d;
}

function calculateAndDisplayDistance() {
    if (userMarker && destMarker) {
        const from = userMarker.getLatLng();
        const to = destMarker.getLatLng();
        const distanceKm = calculateDistanceHaversine(from.lat, from.lng, to.lat, to.lng);
        document.getElementById('distanceOutput').textContent = `${distanceKm.toFixed(2)} km`;
    }
}

