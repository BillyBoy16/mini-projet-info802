import zeep

wsdl = 'http://127.0.0.1:8000/?wsdl'
client = zeep.Client(wsdl=wsdl)
print(client.service.calcul_temps_trajet(436, 100, 0.5))
print(client.service.calcul_prix_trajet(436, 100))