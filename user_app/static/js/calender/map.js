const map = L.map('map').setView([24.7136, 46.6753], 13);

// [Az]Add the tile layer (map background)
L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// [Az] Default location marker
const marker = L.marker([24.7136, 46.6753]).addTo(map);
marker.bindPopup("Default Location").openPopup();

// [Az] Store POI markers to remove them on map move
let poiMarkers = [];

// [Az] Emoji-based Leaflet icons
const icons = {
    cafe: L.divIcon({ className: 'emoji-icon', html: '☕', iconSize: [20, 20], iconAnchor: [10, 10] }),
    restaurant: L.divIcon({ className: 'emoji-icon', html: '🍽️', iconSize: [20, 20], iconAnchor: [10, 10] }),
    hotel: L.divIcon({ className: 'emoji-icon', html: '🏨', iconSize: [20, 20], iconAnchor: [10, 10] }),
    park: L.divIcon({ className: 'emoji-icon', html: '🌳', iconSize: [20, 20], iconAnchor: [10, 10] }),
    default: L.divIcon({ className: 'emoji-icon', html: '📍', iconSize: [20, 20], iconAnchor: [10, 10] }),
};

// [Az] Fetch POIs using Overpass API
function fetchPOIs() {
    // Clear old POIs
    poiMarkers.forEach(m => map.removeLayer(m));
    poiMarkers = [];

    const bounds = map.getBounds();
    const query = `
    [out:json][timeout:25];
    (
        node["amenity"~"cafe|restaurant|atm|fast_food|bar"]( ${bounds.getSouth()}, ${bounds.getWest()}, ${bounds.getNorth()}, ${bounds.getEast()} );
        node["tourism"="hotel"]( ${bounds.getSouth()}, ${bounds.getWest()}, ${bounds.getNorth()}, ${bounds.getEast()} );
        node["leisure"="park"]( ${bounds.getSouth()}, ${bounds.getWest()}, ${bounds.getNorth()}, ${bounds.getEast()} );
    );
    out body;
    `;

    const url = "https://overpass-api.de/api/interpreter?data=" + encodeURIComponent(query);

    fetch(url)
    .then(res => res.json())
    .then(data => {
        data.elements.forEach(element => {
        const lat = element.lat;
        const lon = element.lon;
        const tags = element.tags || {};
        const name = tags.name || 'Unnamed Place';

        // [Az] Pick an icon based on type
        let icon = icons.default;
        if (tags.amenity === 'cafe') icon = icons.cafe;
        else if (tags.amenity === 'restaurant') icon = icons.restaurant;
        else if (tags.tourism === 'hotel') icon = icons.hotel;
        else if (tags.leisure === 'park') icon = icons.park;

        // [Az] Add to map
        const marker = L.marker([lat, lon], { icon: icon }).addTo(map);
        marker.bindPopup(`<b>${name}</b>`);
        poiMarkers.push(marker);
        });
    })
    .catch(err => console.error("POI Fetch Error:", err));
}

// [Az] Load POIs on map movement
map.on('moveend', fetchPOIs);


fetchPOIs();