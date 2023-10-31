// Initialize the map
var map = L.map('map').setView([51.505, -0.09], 12);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Initialize an empty layer group for markers
var markersLayer = L.layerGroup().addTo(map);

// Function to add markers to the map
function addMarkers(data) {
markersLayer.clearLayers(); // Clear existing markers

data.forEach(function(marker) {
    var newMarker = L.marker([marker.lat, marker.lng]);
    newMarker.addTo(markersLayer);
});
}

  // Initial markers on the map
addMarkers(markersData);

// Filtering logic
document.getElementById('filterButton').addEventListener('click', function() {
var category = document.getElementById('categoryFilter').value;
var filteredMarkers = markersData.filter(function(marker) {
    return marker.category === category;
});
addMarkers(filteredMarkers);
});


  // Fetch data from Flask backend
fetch('/get_markers')
    .then(response => response.json())
    .then(data => {
    // Add markers to the map based on data received from the server
    })
    .catch(error => {
    console.error('Error:', error);
    });