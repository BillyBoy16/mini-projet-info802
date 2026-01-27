from flask import Blueprint, request, jsonify, current_app
import openrouteservice
from zeep import Client
import requests
from math import radians, cos, sin, asin, sqrt

trajet_bp = Blueprint('trajet', __name__)

# Fonction utilitaire pour calculer la distance entre 2 points GPS
def haversine(lon1, lat1, lon2, lat2):
    # Conversion degrés -> radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Formule de Haversine
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r

@trajet_bp.post("/trajet-complet")
def calculer_trajet_complet():
    # Récupération des données
    data = request.json
    start_coords = data.get("start_coords")
    end_coords = data.get("end_coords")
    autonomie = data.get("autonomie", 300)
    
    #on s'assure que l'autonomie est un entier
    if isinstance(autonomie, str):
        autonomie = int(autonomie)

    # Clé API
    key = current_app.config['OPENROUTESERVICE_KEY']
    ors_client = openrouteservice.Client(key=key)

    try:
        # Calcul du tracé OpenRouteService
        routes = ors_client.directions(
            coordinates=[start_coords, end_coords],
            profile='driving-car',
            format='geojson'
        )
        
        feature = routes['features'][0]
        geometry = feature['geometry']
        summary = feature['properties']['summary']
        distance_totale_km = int(summary['distance'] / 1000)

        # 3. Appel SOAP (Calcul Prix/Temps)
        try:
            soap_client = Client('http://127.0.0.1:8000/?wsdl')
            temps_estime = soap_client.service.calcul_temps_trajet(
                distance=distance_totale_km, 
                autonomie=autonomie, 
                temps_chargement=0.5
            )
            prix_estime = soap_client.service.calcul_prix_trajet(
                distance=distance_totale_km, 
                autonomie=autonomie
            )
        except Exception as e:
            temps_estime = "Erreur SOAP"
            prix_estime = "N/A"
            print(f"Erreur SOAP: {e}")

        # Recherche des bornes
        bornes_trouvees = []
        path_coords = geometry['coordinates'] #liste de coordonnées
        
        dist_cumulee = 0
        dist_depuis_derniere_recharge = 0
        
        # On définit une marge de sécurité (on cherche une borne à 90% de la batterie)
        seuil_recharge = autonomie * 0.9 

        # URL de VOTRE propre service REST de bornes

        api_bornes_url = "http://127.0.0.1:5000/api/borne-proche"

        # On parcourt point par point
        for i in range(1, len(path_coords)):
            prev = path_coords[i-1]
            curr = path_coords[i]
            
            # Distance entre le point précédent et l'actuel
            segment_dist = haversine(prev[0], prev[1], curr[0], curr[1])
            
            dist_cumulee += segment_dist
            dist_depuis_derniere_recharge += segment_dist

            # Si on dépasse le seuil, il faut recharger ICI
            if dist_depuis_derniere_recharge >= seuil_recharge:
                
                payload = {
                    "lat": curr[1],
                    "lon": curr[0],
                    "rayon": 20000
                }
                
                try:
                    # Appel HTTP POST vers votre autre route
                    resp_service = requests.post(api_bornes_url, json=payload, timeout=2)
                    
                    if resp_service.status_code == 200:
                        data_borne = resp_service.json()
                        
                        if data_borne.get("found") is True:
                            # Le service a répondu qu'il a trouvé une borne
                            bornes_trouvees.append({
                                "nom": data_borne["nom"],
                                "coords": [data_borne["coords"][1], data_borne["coords"][0]],
                                
                                "dist_trajet": f"Arrêt à {int(dist_cumulee)} km",
                                "adresse": data_borne["adresse"],
                                "puissance": data_borne["puissance"]
                            })
                            
                            # On a rechargé, on reset le compteur
                            dist_depuis_derniere_recharge = 0
                            print(f"   [REST] Borne trouvée : {data_borne['nom']}")
                        else:
                            print("   [REST] Pas de borne dans la zone")
                    else:
                        print(f"   [REST] Erreur service : {resp_service.status_code}")

                except Exception as e:
                    print(f"   [REST] Exception connexion service : {e}")

        # Retour au front
        return jsonify({
            "geometry": geometry,
            "bbox": routes['bbox'],
            "infos": {
                "distance": f"{distance_totale_km} km",
                "duree_avec_charge": temps_estime,
                "cout_estime": prix_estime
            },
            "bornes": bornes_trouvees
        })

    except Exception as e:
        return jsonify({"msg": "Erreur interne", "error": str(e)}), 500