from spyne.application import Application
from spyne.service import ServiceBase
from spyne import rpc, Unicode, Integer, Iterable
from spyne.server.wsgi import WsgiApplication
from spyne.protocol.soap import Soap11

class DistanceService(ServiceBase):
    @rpc(Integer, Integer, float, _returns=Unicode)
    def calcul_temps_trajet(ctx, distance, autonomie, temps_chargement):
        
        if distance <= 0 or autonomie <= 0 or temps_chargement < 0:
            return "paramètres invalides"

        vitesse_moy = 83.0  # km/h

        # Nombre d'arrêts de recharge (pas de recharge au départ ni à l'arrivée)
        nb_arrets = max(0, (distance - 1) // autonomie)

        temps_total_heures = (distance / vitesse_moy) + (nb_arrets * temps_chargement)

        heures = int(temps_total_heures)
        minutes = int(round((temps_total_heures - heures) * 60))

        # Gestion du cas 1h60min
        if minutes == 60:
            heures += 1
            minutes = 0

        return f"{heures}h{minutes:02d}min"

    @rpc(Integer, Integer, _returns=Unicode)
    def calcul_prix_trajet(ctx, distance, autonomie):
        """
        Calcule le prix total du trajet.

        distance : distance totale en km
        autonomie : autonomie du véhicule en km
        """
        if distance <= 0 or autonomie <= 0:
            return "paramètres invalides"


        # Nombre d'arrêts de recharge (pas de recharge au départ ni à l'arrivée)
        nb_arrets = max(0, (distance - 1) // autonomie)
        prix = 10  # euros par recharge


        return f"{nb_arrets * prix}€"
    

application = Application([DistanceService], 'spyne.examples.hello.soap', 
                          in_protocol=Soap11(validator='lxml'), 
                          out_protocol=Soap11()) 
wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()