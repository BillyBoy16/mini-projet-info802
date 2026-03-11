# Mini-Projet INFO802 - API de Gestion de Flotte (VE)

Bienvenue sur le dépôt du projet **INFO802**. Ce projet met en place une architecture orientée services pour la gestion de trajets de véhicules électriques. Il orchestre plusieurs technologies et protocoles (**REST, SOAP, GraphQL**) ainsi que des API externes pour fournir des itinéraires intelligents incluant les arrêts de recharge.

## Documentation Interactive

La documentation complète de l'API REST a été rédigée au standard OpenAPI :

[![Swagger](https://img.shields.io/badge/Swagger-Voir_la_doc-85EA2D?logo=swagger&logoColor=black)](https://editor.swagger.io/?url=https://raw.githubusercontent.com/BillyBoy16/mini-projet-info802/develop/openapi.yaml)

---

## Services Déployés (Azure)

L'ensemble des microservices est actuellement déployé et hébergé sur le cloud Azure. Voici les points d'entrée (endpoints) de chaque service :

| Service | Protocole | Description | Lien d'accès |
| :--- | :---: | :--- | :--- |
| **API Principale** | `REST` | Cœur du système (calcul d'itinéraires, recherche de bornes, orchestration). | [Accéder à l'API REST](https://info802-rest-lenny-hwcggwdrbshve5hc.francecentral-01.azurewebsites.net) |
| **Service Estimation** | `SOAP` | Calculateur du coût financier et du temps de trajet estimé. | [Consulter le WSDL](https://info802-soap-lenny-d9dfcuerh9ehdqgk.francecentral-01.azurewebsites.net/?wsdl) |
| **Service Véhicules** | `GraphQL` | Base de données des modèles de voitures et de leurs caractéristiques. | [Playground GraphQL](https://info802-graphql-lenny-etbwh5a0ejendsga.francecentral-01.azurewebsites.net/graphql) |

---

## Architecture & Intégrations

Pour fournir des données précises, ce projet s'appuie sur les API externes suivantes :
* **OpenRouteService** : Génération des tracés GPS et calcul des distances.
* **ChargeTrip** : Récupère les voitures électriques et leurs caractéristiques.
* **OpenDataSoft** : Recherche géolocalisée des bornes de recharge IRVE.
