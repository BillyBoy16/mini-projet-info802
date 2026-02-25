import strawberry
import httpx
from typing import List, Optional
from strawberry.scalars import JSON
import os
from dotenv import load_dotenv

load_dotenv()


#Definition des types
@strawberry.type
class CarNaming:
    make: str
    model: str
    version: Optional[str]

@strawberry.type
class CarRange:
    best: float
    worst: float

@strawberry.type
class CarImage:
    url: Optional[str]
    thumbail_url: Optional[str]

@strawberry.type
class CarBattery:
    usable_kwh: float

@strawberry.type
class Car:
    id: str
    naming: CarNaming
    media: Optional[CarImage]
    range: Optional[CarRange]
    battery: Optional[CarBattery]

# Définition de la logique

@strawberry.type
class Query:
    @strawberry.field
    async def get_cars_json(self) -> List[JSON] :
        # URL et headers du Chargetrip
        url = "https://api.chargetrip.io/graphql"
        client_id = os.getenv("CHARGETRIP_CLIENT_ID")
        app_id = os.getenv("CHARGETRIP_APP_ID")
        # on vérifie que les clés sont là
        if not client_id or not app_id:
            print("ERREUR : Les clés API sont manquantes dans le fichier .env")
            return []

        headers = {
            "x-client-id": client_id,
            "x-app-id": app_id,
        }

        query = """
        query {
          vehicleList(size: 10, page: 0) {
            id
            naming {
              make
              model
              version
            }
            media {
              image {
                url
                thumbnail_url
              }
            }
            range {
              chargetrip_range {
                best
                worst
              }
            }
            battery {
              usable_kwh
            }
          }
        }
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json={"query": query}, headers=headers)
                if response.status_code != 200:
                    return []

                data = response.json()                
                if data.get("data") is None:
                    print("ERREUR GRAPHQL REÇUE :", data.get("errors"))
                    return []

                return data.get("data", {}).get("vehicleList", [])
            except Exception as e:
                print(f"Erreur API Chargetrip: {e}")
                return []
            
schema = strawberry.Schema(query=Query)

