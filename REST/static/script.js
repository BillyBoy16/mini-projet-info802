/* Fonctions Loader */
function showLoader(message = "Chargement...") {
    const msgEl = document.getElementById("loaderMessage");
    const loaderEl = document.getElementById("loader");
    if (msgEl) msgEl.innerText = message;
    if (loaderEl) loaderEl.style.display = "flex";
}

function hideLoader() {
    const loaderEl = document.getElementById("loader");
    if (loaderEl) loaderEl.style.display = "none";
}

/* Fonctions initialisation (carte + voiture) */
let loadedCars = [];

// Initialisation de la carte Leaflet
var map = L.map('map').setView([46.603354, 1.888334], 6); // Centré sur la France

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var routeLayer = null;
var startMarker = null;
var endMarker = null;
var stationMarkers = L.layerGroup().addTo(map);

// Style des points rouge (Départ/Arrivée)
const redPointStyle = { 
    color: 'red', 
    fillColor: '#f03', 
    fillOpacity: 0.8, 
    radius: 8, 
    weight: 1 
};

/* Chargement initial voiture */
document.addEventListener("DOMContentLoaded", async () => {
    await loadCarsFromGraphQL();
});

/* Fonctions GraphSQL */
async function loadCarsFromGraphQL() {
    const select = document.getElementById("carSelect");

    try {
        const response = await fetch('/api/voiture', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        const result = await response.json();
        
        if (result.data && result.data.getCarsJson) {
            loadedCars = result.data.getCarsJson;
            
            // Vide le select
            select.innerHTML = '<option value="">-- Sélectionnez une voiture --</option>';

            // Remplit le select
            loadedCars.forEach((car, index) => {
                const option = document.createElement("option");
                option.value = index; 
                option.text = `${car.naming.make} ${car.naming.model} ${car.naming.version || ''}`;
                select.appendChild(option);
            });
        } else {
            select.innerHTML = '<option>Erreur chargement API</option>';
        }

    } catch (error) {
        console.error("Erreur GraphQL:", error);
        select.innerHTML = '<option>Erreur de connexion (Port 8001 ?)</option>';
    }
}

function updateCarDetails() {
    const index = document.getElementById("carSelect").value;
    const previewDiv = document.getElementById("carPreview");
    const imgEl = document.getElementById("carImage");
    const textEl = document.getElementById("carData");
    const autonomieInput = document.getElementById("autonomie");

    if (index === "") {
        previewDiv.style.display = "none";
        return;
    }

    const car = loadedCars[index];
    
    previewDiv.style.display = "flex";

    // Gestion de l'image
    if (car.media && car.media.image && car.media.image.thumbnail_url) {
        imgEl.src = car.media.image.thumbnail_url;
    } else {
        imgEl.src = "https://via.placeholder.com/100x60?text=No+Img";
    }

    // Calcul autonomie moyenne
    let range = 300; 
    if (car.range && car.range.chargetrip_range) {
        range = (car.range.chargetrip_range.best + car.range.chargetrip_range.worst) / 2;
        range = Math.round(range);
    }
    autonomieInput.value = range;

    textEl.innerHTML = `
        <strong>${car.naming.make} ${car.naming.model}</strong><br>
        Batterie : ${car.battery ? car.battery.usable_kwh : '?'} kWh<br>
        Autonomie estimée : ${range} km
    `;
}

/* Fonctions REST */

async function getCoordsFromCity(city) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${city}`;
    const response = await fetch(url);
    const data = await response.json();
    
    if (data && data.length > 0) {
        return [parseFloat(data[0].lon), parseFloat(data[0].lat)];
    } else {
        throw new Error("Ville introuvable : " + city);
    }
}

async function lancerTraitement() {
    const btn = document.getElementById("btnCalculer");
    const divRes = document.getElementById("resultat");
    const villeDep = document.getElementById("depart").value;
    const villeArr = document.getElementById("arrivee").value;

    showLoader("Calcul de l'itinéraire et recherche des bornes...");

    btn.disabled = true;
    btn.innerText = "Chargement...";
    divRes.innerText = "";
    divRes.style.color = "#333";

    // Nettoyage de la carte
    if (routeLayer) map.removeLayer(routeLayer);
    if (startMarker) map.removeLayer(startMarker);
    if (endMarker) map.removeLayer(endMarker);
    stationMarkers.clearLayers();

    try {
        const startCoords = await getCoordsFromCity(villeDep);
        const endCoords = await getCoordsFromCity(villeArr);
        const autonomieVal = document.getElementById("autonomie").value;

        // Appel à l'API REST (Port 5000)
        const response = await fetch('/api/trajet-complet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_coords: startCoords,
                end_coords: endCoords,
                autonomie: parseInt(autonomieVal)
            })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.msg);

        // --- Affichage ---

        // 1. La ligne (Trajet)
        routeLayer = L.geoJSON(data.geometry, { style: { color: 'blue', weight: 5 } }).addTo(map);

        // 2. Les infos
        divRes.innerHTML = `
            <div style="background:#e8f4fd; padding:15px; border-radius:8px; margin-top:10px;">
                <h4 style="margin-top:0;">Résumé du trajet</h4>
                <strong>Distance :</strong> ${data.infos.distance} <br>
                <strong>Temps total :</strong> ${data.infos.duree_avec_charge} <br>
                <strong>Coût estimé :</strong> ${data.infos.cout_estime}
            </div>
        `;

        // 3. Les bornes
        data.bornes.forEach(borne => {
            L.marker(borne.coords).addTo(stationMarkers)
            .bindPopup(`<b>Recharge nécessaire</b><br>${borne.nom}<br>${borne.dist_trajet}`);
        });

        // 4. Points départ/arrivée
        startMarker = L.circleMarker([startCoords[1], startCoords[0]], redPointStyle).addTo(map);
        endMarker = L.circleMarker([endCoords[1], endCoords[0]], redPointStyle).addTo(map);

        // 5. Zoom automatique sur le tracé
        if (routeLayer) {
            map.fitBounds(routeLayer.getBounds(), { padding: [10, 10] });
        }

    } catch (err) {
        console.error(err);
        divRes.innerText = "Erreur : " + err.message;
        divRes.style.color = "#c0392b";
    } finally {
        btn.disabled = false;
        btn.innerText = "Calculer";
        hideLoader();
    }
}