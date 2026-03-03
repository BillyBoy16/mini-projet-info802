import requests
import os
from flask import Blueprint, jsonify

voiture_bp = Blueprint('voiture', __name__)

@voiture_bp.get("/voiture")
def get_voitures():
    graphql_url = os.getenv("GRAPHQL_SERVICE_URL", "http://127.0.0.1:8001/graphql")

    # 2. Définition de la requête GraphQL (La même que dans le Playground)
    query = """
    query {
        getCarsJson
    }
    """

    try:
        # 3. Appel HTTP POST
        response = requests.post(
            graphql_url, 
            json={'query': query},
            timeout=5
        )

        # 4. Vérification du statut
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({
                "error": "Erreur API GraphQL", 
                "status": response.status_code,
                "details": response.text
            }), 502

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion au GraphQL: {e}")
        return jsonify({"error": "Service GraphQL indisponible", "msg": str(e)}), 503