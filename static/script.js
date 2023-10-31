// Initialize the map
var map = L.map('map').setView([51.505, -0.09], 13);

// Add OpenStreetMap tile layer
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Initialize an empty layer group for markers
var markersLayer = L.layerGroup().addTo(map);

// Function to add markers to the map
function addMarkers(data) {
    var circle = L.circle([51.508, -0.11], {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.5,
        radius: 500
    }).addTo(map);
    // Clear the markers on the map
    markersLayer.clearLayers();
    // Creates a popup for the circle
    circle.bindPopup("I am a circle.");
    // Ensure each marker is plotted on the map
    data.forEach(function(marker) {
        var newMarker = L.marker([marker.Latitude, marker.Longitude]);
        newMarker.bindPopup("<b>Hello world!</b><br>I am a popup.").openPopup();
        newMarker.addTo(markersLayer);
    });
}

// Initial markers on the map
// addMarkers(markersData);

// Filtering logic
document.getElementById('filterButton').addEventListener('click', function() {
    var category = document.getElementById('categoryFilter').value;
    var filteredMarkers = markersData.filter(function(marker) {
        // return marker.category === category;
        // Return mark if room_0_price is less than 1000
        return marker.room_0_price < 1000;
    });
    addMarkers(filteredMarkers);
});


// Fetch data from Flask backend
fetch('/get_markers')
    .then(response => response.json())
    .then(data => {
        // Add markers to the map based on data received from the server
        addMarkers(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });