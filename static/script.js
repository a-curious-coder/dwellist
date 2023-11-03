// Initialize the map
var map = L.map('map').setView([51.505, -0.09], 13);

// Add OpenStreetMap tile layer
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Initialize an empty layer group for markers
var markersLayer = L.layerGroup().addTo(map);
var markersData = [];

function generatePopupContent(row) {
    var imageLink = row["image_0"] ? `<img src="${row["image_0"]}" alt="Property Image" style="max-width: 100%">` : '';
    var roomPrice = "£" + row["room_0_price"];

    var popupContent = `
        <div style="width: 200px;">
            <h3>${row["area"]}</h3>
            <a href="${row["url"]}" target="_blank">${imageLink}</a>
            <p><strong>Type:</strong> ${row["type"]}</p>
            <p><strong>Bills Included: </strong> ${row["bills_included"]}</p>
            <p><strong>Available:</strong> ${row["available"]}</p>
            <p><strong>Room Prices:</strong></p>
            <ul>
                <li>${roomPrice}</li>
            </ul>
            <a href="${row["url"]}" target="_blank">View Details</a>
        </div>
    `;
    return popupContent;
}

function updateMarkerDetailsCard(content) {
    document.getElementById('markerDetailsCard').innerHTML = content;
}

function generateCardContent(row) {
    var imageLink = row["image_0"] ? `<img src="${row["image_0"]}" alt="Property Image" style="max-width: 100%">` : '';
    var roomPrice = "£" + row["room_0_price"];

    var cardContent = `
        <h3>${row["area"]}</h3>
        ${imageLink}
        <p><strong>Type:</strong> ${row["type"]}</p>
        <p><strong>Bills Included: </strong> ${row["bills_included"]}</p>
        <p><strong>Available:</strong> ${row["available"]}</p>
        <p><strong>Room Prices:</strong></p>
        <ul>
            ${roomPrice}
        </ul>
        <a href="${row["url"]}" target="_blank">View Details</a>
    `;

    return cardContent;
}

var highlightedIcon = L.icon({
    iconUrl: 'static/icons/icon.png',
    iconSize: [32, 32], // Set the size of the icon
    iconAnchor: [16, 32], // Set the anchor point for the icon
    popupAnchor: [0, -32] // Set the popup anchor for the icon
});

var defaultMarkerIcon = L.icon({
    iconUrl: 'static/icons/default.png',
    iconSize: [32, 32], // Set the size of the icon
    iconAnchor: [16, 32], // Set the anchor point for the icon
    popupAnchor: [0, -32] // Set the popup anchor for the icon
});


// Function to add markers to the map
function addMarkers(data) {

    // Clear the markers on the map
    markersLayer.clearLayers();

    // Ensure each marker is plotted on the map
    data.forEach(
        function(markerData) {
            // Create a new marker
            var newMarker = L.marker([markerData.latitude, markerData.longitude], {icon: defaultMarkerIcon});

            // Generate card content for the marker
            var popupContent = generatePopupContent(markerData);

            // Create a popup with picture from image_0 (url) and price
            newMarker.bindPopup(popupContent).openPopup();
            // Move the map to the marker when the popup is opened
            newMarker.on('popupopen', function() {
                map.setView(newMarker.getLatLng());
            });
            // Reset marker icons when any marker is clicked
            newMarker.on('click', function() {
                markersLayer.eachLayer(
                    function(layer) {
                        layer.setIcon(defaultMarkerIcon);
                    }
                );
                // Set the highlighted marker icon for the clicked marker
                newMarker.setIcon(highlightedIcon);
            });

            // Add the marker to the layer group
            newMarker.addTo(markersLayer);
        }
    );
}

// Create a function that filters markers based on the price range
function filterMarkers(minPrice, maxPrice, billsIncluded) {
    // Filter the markers based on the price range
    var filteredMarkers = markersData.filter(
        function(marker) {
            // Create let variables for the price of the room cast to a integer
            let roomPrice = parseInt(marker.room_0_price);
            // Print a message to console stating whether the price is more than or less than the minimum price
            return roomPrice >= minPrice && roomPrice <= maxPrice && billsIncluded === marker.bills_included;
        }
    );

    return filteredMarkers;
}
// JavaScript to handle filter card toggle
var filterCollapsible = document.querySelector('.filter-collapsible');
var filterCard = document.querySelector('.filter-card');

filterCollapsible.addEventListener('click', function() {
    filterCard.style.right = (parseInt(filterCard.style.right) === 0) ? '-300px' : '0';
});

// Filtering logic
document.getElementById('filterButton').addEventListener('click', 
    function() {
        event.preventDefault();
        // Get the minimum and maximum prices from the text boxes
        var minPrice = document.getElementById('minPrice').value;
        var maxPrice = document.getElementById('maxPrice').value;
        var billsIncluded = document.getElementById('billsIncluded').value;
        console.log(minPrice);
        console.log(maxPrice);
        var filteredMarkers = filterMarkers(minPrice, maxPrice, billsIncluded);
        console.log(filteredMarkers.length);
        // Redraw the markers on the map
        addMarkers(filteredMarkers);
    }
);


// Fetch data from Flask backend
fetch('/get_markers')
    .then(response => response.json())
    .then(data => {
        markersData = data;
        // Add markers to the map based on data received from the server
        addMarkers(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });