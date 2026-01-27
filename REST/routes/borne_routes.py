import requests
from flask import Blueprint, request, jsonify

borne_bp = Blueprint('bornes', __name__)

@borne_bp.post("/borne-proche")
def trouver_borne_proche():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    rayon = data.get("rayon", 5000)

    if not lat or not lon:
        return jsonify({"msg": "Coordonnées manquantes"}), 400

    # Interrogation de la base de données (OpenDataSoft)
    ods_url = "https://odre.opendatasoft.com/api/records/1.0/search/"
    params = {
        "dataset": "bornes-irve",
        "rows": 1,
        "geofilter.distance": f"{lat},{lon},{rayon}"
    }

    try:
        response = requests.get(ods_url, params=params, timeout=5)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("records"):
                rec = json_data["records"][0]
                fields = rec["fields"]
                
                # On formate une réponse propre standardisée
                return jsonify({
                    "found": True,
                    "nom": fields.get("n_station", "Borne inconnue"),
                    "adresse": fields.get("ad_station", "Adresse N/A"),
                    "puissance": f"{fields.get('puiss_max', '?')} kW",
                    # Format standard GeoJSON pour l'API : [Lon, Lat]
                    "coords": [rec["geometry"]["coordinates"][0], rec["geometry"]["coordinates"][1]]
                }), 200
            else:
                return jsonify({"found": False, "msg": "Aucune borne trouvée"}), 200
        else:
            return jsonify({"msg": "Erreur OpenDataSoft"}), 502
            
    except Exception as e:
        return jsonify({"msg": "Erreur interne", "error": str(e)}), 500