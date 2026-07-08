
function initializeLeafletMap(latitude, longitude, licensePlate) {

    var map = L.map('map').setView([latitude, longitude], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        { attribution: '&copy; <a href="www.openstreetmap.org">OpenStreetMap</a> contributors'}
    ).addTo(map);

    //var car_marker = L.marker([latitude, longitude], {'draggable':true}).addTo(map).bindPopup(licensePlate).openPopup();
    var car_marker = L.marker([latitude, longitude], {'draggable':false}).addTo(map).bindPopup(licensePlate).openPopup();
}
