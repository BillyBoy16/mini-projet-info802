from spyne.application import Application
from spyne.service import ServiceBase
from spyne import rpc, Unicode, Integer, Iterable, Float
from spyne.server.wsgi import WsgiApplication
from spyne.protocol.soap import Soap11

class DistanceService(ServiceBase):
    @rpc(Integer, Float, Integer, _returns=Unicode)
    def calcul_temps_trajet(ctx, distance, temps_chargement, nb_arrets):
        """
        Calcule le temps total du trajet.
        distance : distance totale du trajet en km
        temps_chargement : temps de chargement par arrêt en heures
        nb_arrets : nombre d'arrêts de recharge
        """
        
        if distance <= 0 or temps_chargement < 0:
            return "paramètres invalides"

        vitesse_moy = 83.0  # km/h

        temps_total_heures = (distance / vitesse_moy) + (nb_arrets * temps_chargement)

        heures = int(temps_total_heures)
        minutes = int(round((temps_total_heures - heures) * 60))

        if minutes == 60:
            heures += 1
            minutes = 0

        return f"{heures}h{minutes:02d}min"

    @rpc(Integer, _returns=Unicode)
    def calcul_prix_trajet(ctx,  nb_arrets):
        """
        Calcule le prix total du trajet.
        nb_arrets : nombre d'arrêts de recharge
        """

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