@echo off
echo ==========================================
echo      LANCEMENT DES SERVEURS DU PROJET
echo ==========================================

:: 1. Lancer le serveur GraphQL (Port 8001)
:: "cd GraphSQL" entre dans le dossier
:: "&&" permet d'enchainer la commande suivante
:: "cmd /k" garde la fenetre ouverte en cas d'erreur
echo Lancement du serveur GraphQL...
start "Serveur GraphQL (Port 8001)" cmd /k "cd GraphSQL && python main.py"

:: 2. Lancer le serveur REST (Port 5000)
echo Lancement du serveur REST...
start "Serveur REST (Port 5000)" cmd /k "cd REST && python app.py"

:: 3. Lancer le serveur SOAP
echo Lancement du serveur SOAP...
start "Serveur SOAP (Port 8000)" cmd /k "cd soap && python soap.py"

echo.
echo Tous les serveurs sont en cours de demarrage dans des fenetres separees.
echo Vous pouvez reduire cette fenetre.
pause