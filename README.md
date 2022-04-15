LinkyRPi – documentation


# Objet du projet
L’objet de ce projet est d’exploiter les données émises par les compteurs communicants Enedis via la Télé-Information Client (TIC).

Différents usages sont possibles :

- Analyser en direct les données de consommation et/ou de production d’électricité. Ceci afin de connaitre celles-ci en temps réel et en déduire les postes de consommation du foyer. Dans le cas d’une installation électrique triphasée, cela permet aussi de s’assurer du bon équilibrage des phases et, éventuellement, de l’optimiser.
- Analyser à posteriori des données de consommation afin de calculer divers types d’indicateurs de consommation dans le but d’optimiser celles-ci et de réduire sa facture d’électricité et, par conséquent, son empreinte carbone.
- Exploiter les basculements de plages tarifaires (Heures pleines/creuses, Heures normales/de pointe EJP, Couleurs du jour/lendemain Tempo) ainsi que les différents relais virtuels du compteur afin de piloter automatiquement des délestages de consommation, et ainsi limiter l’utilisation des postes de forte consommation (chauffage d’eau sanitaire, chauffage électrique, lave-linge, sèche-linge, four électrique, etc…) aux plages de moindre coût de l’électricité.

# Considérations
Ce projet est pensé pour être compatible avec tous les compteurs communiquant Enedis, à savoir :

- Les compteurs communiquant antérieurs à Linky disposant d’une sortie TIC.
- Les compteurs Linky monophasés et triphasés.
- Les compteurs Linky dont la TIC est programmée en mode « Historique » ou « Standard ».
- Il prend aussi en charge les installations de production électriques (foyers équipés de panneaux photovoltaïques) et permet d’analyser les données de production.

Il est prévu pour fonctionner en « stand alone », à savoir sans avoir recours à aucun ordinateur ou serveur annexe. Il est totalement autonome et peut donc être branché à tout compteur communiquant Enedis, quelle que soit la situation. Il nécessite seulement une alimentation externe, qui peut être fournie soit par un transformateur permettant de raccorder son port micro-USB à une prise secteur, soit par une batterie externe.

Il peut aussi fonctionner avec une base de données externe Postgresql, installée sur un serveur distant. Dans ce cas il doit en plus être raccordé au réseau sur lequel se trouve le serveur de base de données, soit au travers d’un câble Ethernet, soit via une connexion WiFi.

# Références / sources

|**Document**|**Objet du document**|
| :-: | :-: |
|[Enedis-NOI-CPT_54E](https://www.enedis.fr/media/2035/download)|Documentation technique de la TIC|
|[Page Wikipedia du compteur Linky](https://fr.wikipedia.org/wiki/Linky#T%C3%A9l%C3%A9-information_client)|Informations générales sur le compteur Linky et la TIC|
|[Magdiblog](https://www.magdiblog.fr/gpio/teleinfo-edf-suivi-conso-de-votre-compteur-electrique/)|Inspiration de base pour la conception de cette application|


# Architecture matérielle
Le matériel se compose de :

- Un Raspberry Pi (modèle 1b ou supérieur) avec sa carte SD et son alimentation.
- Une carte d’interface permettant le raccordement du Raspberry-Pi au compteur électrique.
- [Un écran LDC tactile](https://www.amazon.fr/gp/product/B085NH94KV/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1). 
- Des câbles de connexion :
  - [Un câble HDMI plat](o%09https:/www.amazon.fr/gp/product/B07R6CWPH1/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1).
  - [Un câble USB pour alimenter l’écran LCD et transmettre les informations tactiles](o%09https:/www.amazon.fr/gp/product/B01N7ZE55F/ref=ppx_yo_dt_b_asin_title_o03_s01?ie=UTF8&psc=1).
- [Un boitier](https://www.amazon.fr/gp/product/B07GPY8TPD/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1).

## La carte d’interface
La carte d’interface se compose :

- [D’une carte de prototypage](https://www.amazon.fr/gp/product/B073W78G8J/ref=ppx_yo_dt_b_asin_title_o04_s01?ie=UTF8&psc=1).
- D’un optocoupleur [SFH620A-3X](https://www.amazon.fr/gp/product/B015H608BM/ref=ppx_yo_dt_b_asin_title_o09_s00?ie=UTF8&psc=1) à doubles diodes têtes-bêches.
- D’une résistance de 1.2kOhm et une résistance de 3.3kOhm.
- [D’un bornier de connexion pour raccorder la carte d’interface au compteur Linky](https://www.amazon.fr/gp/product/B018OTAKJO/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1).
- [D’un bornier de connexion au GPIO du Raspberry Pi](https://www.amazon.fr/gp/product/B0786WVNR8/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1).
- D’un câble de type « paire torsadée » pour la connexion au compteur Linky (bornes I1 et I2 de ce dernier).

Le rôle de la carte d’interface est d’assurer la transmission des données de la TIC au port série du Raspberry-Pi tout en assurant l’isolation galvanique entre ces deux éléments (grâce à l’optocoupleur).

De plus, le signal émis par le compteur étant de type « modulation d’amplitude » sur une porteuse alternative sinusoïdale à 50Hz, l’optocoupleur assure en plus le redressement du signal (d’où la nécessité d’un optocoupleur à double diode tête-bêches).

La résistance de pull-up (R2 dans le schéma ci-dessous) étant raccordée au +3.3V du GPIO du Raspberry-Pi, cela assure la compatibilité du signal avec les caractéristiques du port série de ce dernier. La résistance R1 assure quant à elle la protection des diodes de l’optocoupleur.
##
## Schéma de la carte d’interface

![alt text](https://github.com/Maximilian75/LinkyRPi/blob/main/Picture1.jpg)


## Connecteur GPIO du Raspberry-Pi

|**Raspberry-Pi modèle 1**|<p>**Raspberry-Pi modèles 2+**</p><p></p>|
| :-: | :-: |
|![alt text](https://github.com/Maximilian75/LinkyRPi/blob/main/Picture2.png)|![alt text](https://github.com/Maximilian75/LinkyRPi/blob/main/Picture3.png)|



# Architecture logicielle
![alt text](https://github.com/Maximilian75/LinkyRPi/blob/main/Picture4.jpg)
## Framework technique
Le système d’exploitation installé sur le Raspberry Pi est une distribution Linux « Raspbian Lite ».

Les différents modules sont écrits en Python 3.

L’interface graphique est développée sous tkinter.

## Le listener
Le module « LinkyRPiListen.py » est chargé de lire les trames d’information émises par le compteur Linky, de les décoder et de les transmettre aux deux autres modules au travers de « message queues POSIX ».
### Première étape : détection du mode de fonctionnement de la TIC
La première étape consiste en la détection du type de trames émises par le compteur Linky. En effet, celui-ci propose deux modes de fonctionnement de la TIC : « Historique » et « Standard ».

En mode « Historique » le compteur envoie des trames à 1200 Bauds tandis qu’en mode « Standard » les trames sont émises à 9600 Bauds.

***Note :** Il est possible de demander à son fournisseur d’énergie (EDF, Total énergie, …) de modifier le mode de fonctionnement de la TIC sur le compteur Linky. L’opération est gratuite et est en général traitée dans les 24 heures. Elle est faite à distance et ne demande donc aucune intervention sur place.*

Le principe de fonctionnement de cette détection est simple : le module va d’abord tenter de décoder une trame à 1200 Bauds. S’il y parvient, alors c’est que la TIC est en mode « Historique ». Sinon il va tenter de décoder une trame à 9600 Bauds. Dans ce cas, cela voudra dire que la TIC est en mode « Standard ».

Une fois le mode de fonctionnement de la TIC connu, le module se met en écoute permanente du port série afin de décoder les trames reçues.
### Deuxième étape : décoder les trames de la TIC
Comme expliqué ci-dessus, le compteur Linky peut émettre des trames en mode « Historique » ou « Standard ».

La constitution des trames étant différente d’un mode à l’autres (mots-codes différents, listes d’informations transmises différentes), le module Listener va décoder les trames afin des les charger dans un dictionnaire agnostique du mode de fonctionnement de la TIC. Cela simplifiera le travail en aval. Ceci est fait au travers des différentes fonctions contenues dans le module « linky.py ».

De plus, cela permet une compatibilité totale avec les deux modes de fonctionnement.
### Troisième étape : émission des trames décodées vers les modules GUI et DB
L’étape suivante est d’envoyer la trame traduite vers les deux autres modules.

Tout d’abord le dictionnaire contenant la trame traduite est sérialisé sous forme de Json, puis ce Json est envoyé dans deux « message queues POSIX », l’une à destination du module d’affichage des données à l’écran (LinkyRPiGUI.py), l’autre à destination du module d’enregistrement des données dans la base de données Postgresql (LinkyRPiDB.py).

## Le module d’enregistrement en base de données
Le module « LinkyRPiDB » est chargé d’enregistrer les trames dans la base de données Postgresql.

Dans un premier temps le module tente de se connecter à la base de données.

S’il y parvient, il se met en écoute permanente des messages émis par le listener. Sinon il s’arrête définitivement.

A chaque message reçu, il va enregistrer les informations contenues dans le message dans la base de données Postgresql.

***Note :** il est possible de se passer de ce module. Dans ce cas il faudra adapter la configuration de l’application dans le fichier « linkyRPi.conf » afin de signaler au Listener de ne pas envoyer de messages à l’attention du module d’enregistrement en base de données.*
## Le module d’affichage des données à l’écran
### Première étape : initialisation de l’interface graphique
Dans un premier temps, le module se met en attente d’un message sur sa queue dédiée. A réception de la première trame, le module va exploiter celle-ci afin d’initialiser la GUI.

En effet, comme expliqué plus haut, les informations véhiculées par la TIC sont différentes selon si celle-ci est paramétrée en mode « Historique » ou « Standard ». L’interface graphique doit donc être adaptée au mode de fonctionnement de la TIC.

Lors de cette étape, le module va donc analyser la première trame reçue et créer les différents onglets et différents champs de l’interface graphique.
### Deuxième étape : scheduling des procédures de rafraichissement
La plupart des données n’ont pas besoin d’un taux de rafraichissement très élevé. En dehors des données « instantanées » qui seront traitées en temps réel, le reste sera rafraichi à intervalles plus ou moins grands.

Le module va donc mettre en place des procédures qui seront exécutées à intervalles réguliers, quel que soit le rythme de réception des trames. Ces procédures utiliseront les données de la trame courante au moment de leur exécution afin d’en afficher les données à l’écran.

- Les données signalétiques ne sont affichées que lors de la réception de la première trame et ne seront jamais mises à jour. C’est le cas des identifiants du compteur et des informations relatives au type d’abonnement. En effet, ces informations ne changent en principe jamais. Dans le cas d’un changement d’abonnement, il suffirait de redémarrer le process pour voir apparaitre les nouvelles informations.
- Les données liées aux plages tarifaires en cours (Heures pleines / creuses, heures de pointe EJP ou couleurs du jour / lendemain Tempo) sont rafraichies toutes les 15 minutes (ce temps est paramétrable dans le fichier de configuration « linkyRPi.conf ».
- Les données liées aux index de consommation, aux messages d’information ou d’avertissement (tels que les alertes de dépassement), ainsi que les données statistiques (intensités, tensions et puissances moyennes / maximales atteintes) sont rafraichies toutes les minutes. Là aussi ce temps est configurable.
### Troisième étape : réception des données et rafraichissement des écrans
Une fois l’interface graphique initialisée et les procédures schedulées démarrées, le process se met en écoute constante de la message queue afin de collecter les trames envoyées par le listener.

Les données instantanées (tensions, intensités et puissances) sont rafraichies à chaque réception de trames, soit en quasi-temps-réel.
## Le fichier de configuration « linkyRPi.conf »
Ce fichier contient toute la configuration de l’application. Il est divisé en différentes sections :
### Paramètres généraux de l'application
```
[PARAM]
debugLevel: 0  --> Permet d'activer des traces pour debugger le code
refreshPlage: 2000  --> Temps en mili-secondes entre deux refresh de la frame "Info"
refreshStats: 2000  --> Temps en mili-secondes entre deux refresh des frames "Status" et "Registre"
refreshIndex: 2000  --> Temps en mili-secondes entre deux refresh de la frame "Courbe"
traceFile: True  --> 'True' pour activer l'enregistrement de trames dans un fichier text. Pratique pour ensuite tester la GUI sans être raccordé au compteur
traceFreq: 300  --> Durée en secondes entre deux enregistrements dans le fichier texte
version: 2.10  --> Version de LinkyRPi
```
### Paramètres liés à la communication IPC
```
[POSIX]
queueGUI: /LinkyRPiQueueGUI  --> Nom de la message queue pour communication Listener --> GUI
depthGUI: 8  --> Nombre de messages max dans la queue de communication de la GUI
queueDB: /LinkyRPiQueueDB  --> Nom de la message queue pour communication Listener --> DB
depthDB: 200  --> Nombre de messages max dans la queue de communication de la DB

[PATH]  --> Ce groupe indique les path vers les différents sous-composants de l'appli (logs, icones,...)
```
### Paramètres liés au style de la GUI
```
[GUICSS]  --> Ce groupe définit les couleurs, polices d'écriture, etc... de la GUI
```
### Paramètres liés à la base de données Postgresql
```
[POSTGRESQL]
active: True  --> 'True' pour activer le process d'écriture en DB, 'False' sinon
user: xxxxx  --> Le user d'accès à la DB Postgresql
password: xxxxxxx  --> Le mot de passe d'accès à la DB
host: xxx.xxx.xxx.xxx  --> L'adresse IP du serveur où se trouve physiquement la DB Postgresql
port: 5432  --> Le port d'écoute de la DB
dbname: linkydb  --> Le nom de la DB
refreshDB: 60  --> Durée en seconde entre deux enregistrements en DB
```


# Procédure d’installation de l’application « stand alone »
La procédure suivante indique comment installer l’application en mode « stand alone », c’est-à-dire sans la base de données permettant de stocker les données issues du compteur de façon permanente.

Dans ce mode, les données sont « consommées » par l’application et affichées sur l’écran. Rien n’est conservé.

Pour bénéficier du stockage à long terme des données issues du compteur (afin de les exploiter à posteriori), il suffit de suivre l’installation « stand alone » puis de suivre les instructions du chapitre suivant : [Fonctionnement avec base de données](#_Fonctionnement_avec_base).

## Outils à télécharger
Logiciels à installer (sous Windows) pour l’installation de l’application sur le Raspberry-Pi :

- Putty : <https://www.putty.org/>
- FileZilla : <https://filezilla-project.org/>
- SD Card Formatter : <https://sd-card-formatter.en.uptodown.com/windows>
- Win32 Disk Imager : <https://sourceforge.net/projects/win32diskimager/>

Image de l’OS à installer sur le Raspberry-Pi :

- Raspbian **Lite** : <https://www.raspberrypi.com/software/operating-systems/>

## Initialisation de la carte SD et installation du système d’exploitation
### Formatage de la carte SD

### Installation de l’OS (Raspbian Lite) sur la carte SD

### Connexion SSH via Putty
La suite de l’installation se fera directement sur le Raspberry-Pi. Il est donc nécessaire de se connecter dessus en SSH grâce à Putty.

Par défaut les informations de connexion sont les suivantes :

- User : pi
- Password : raspberry

## Configuration du Raspberry Pi
La première étape consiste à configurer le Raspberry-Pi :
```shell
sudo raspi-config
```
--> Autoriser le serveur SSH
--> Interdire le SSH Serial
--> Display --> VNC resolution --> mettre en 1024*600

## Installation des paquets nécessaires à l’application
Avant tout, il faut ajouter un nouveau dépot :
```
sudo nano /etc/apt/sources.list
```
A la fin du fichier, ajouter le dépot suivant :
```
deb http://mirror.ox.ac.uk/sites/archive.raspbian.org/archive/raspbian stretch main contrib non-free rpi
```
Puis faite un update d'apt-get
```
sudo apt-get update
```
Enfin, on installe tous les paquets nécessaire à LinkyRPi, à savoir
- Python3 et pip :
```
sudo apt install python3
sudo apt install python3-pip
```
- Les paquest permettant de gérer le port série :
```
sudo apt install python3-serial
pip3 install RPi.GPIO
pip3 install pyserial
```
- Les paquets permettant de comuniquer avec la DB Postgresql
```
sudo apt-get install libpq-dev
pip3 install psycopg2
pip3 install psycopg2-binary
sudo apt-get install python3-psycopg2
```
- Les paquest liés à l'interface graphique
```
sudo apt-get install python3-tk
sudo apt-get install xterm
sudo apt-get install libopenjp2-7
```
- Le paquet permettant l'utilisation des message-queues POSIX pour la communication IPC
```
pip3 install posix_ipc
```

## Gestion de la mise à l'heure du Raspberry-Pi
```
sudo timedatectl set-timezone Europe/Paris
sudo timedatectl set-ntp true
```
Vérification :
```
timedatectl status
```

## Gestion du WiFi
Création/modification du fichier wpa_supplicant.conf
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
Celui-ci doit contenir les lignes suivantes. Les ajouter si ce n'est pas le cas :
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR
```
Ainsi que la liste des WiFi disponibles sous la forme
```
network={
        ssid="Mon wifi 1"
        psk="mot de pass de mon wifi 1"
}
network={
        ssid="Mon wifi 2"
        psk="mot de pass de mon wifi 2"
}
```
## Configuration de l'écran tactile et installation des paques nécessaires à son utilisation
```
sudo nano /boot/config.txt
```
Ajouter les lignes suivantes :
```
max_usb_current=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt 1024 600 60 6 0 0 0
hdmi_drive=1
```
Puis installer les paquets suivants :
```
sudo apt-get -y install nodm matchbox-window-manager
sudo apt-get install x11-xserver-utils
sudo apt-get install xinit
```
Enfin il faut paramétrer le démarrage automatique du serveur X
```
sudo nano /lib/systemd/system/nodm.service
```
Modifier la ligne "After" ainsi :
```
After=plymouth-quit.service systemd-user-sessions.service runlevel2.target, runlevel4.target, multi-user.target
```

## Déploiement de l’application sur le Raspberry Pi
Les différents scripts et objets graphiques doivent ensuite être transférés sur la carte SD du Raspberry-Pi. Pour cela il faut se connecter au Raspberry-Pi avec FileZilla. Les user/password à utiliser sont les mêmes que dans Putty.

### Arborescence des répertoires du Raspberry Pi

|/usr/pi|Répertoire racine du user par défaut du Raspberry Pi (pi)|
| :- | :- |
|/usr/pi/LinkyRPi|Répertoire racine de l’application|
||- LinkyRPiListen.py|Script du listener|
||- LinkyRPiGUI.py|Script de l’interface graphique|
||- LinkyRPiDB.py|Script d’écriture dans la base de données|
||- linky.py|Script de décodage des trames|
||- linky.conf|Fichier de configuration de l’application|
|/usr/pi/LinkyRPi/icons|Ce répertoire contient les objets graphiques de l’interface (boutons, voyants, etc…)|
|/usr/pi/LinkyRPi/logs|Ce répertoire contient les logs d’exécution des différents process|


## Création des services pour démarrage automatique de l’application
L’objectif ici étant de démarrer automatiquement tous les modules de l’application afin qu’aucune manipulation (saisie de ligne de commande) ne soit nécessaire. C’est le principe d’une application embarquée. Tout fonctionne sans avoir besoin d’un clavier connecté à l’appareil. C’est aussi là tout l’intérêt d’avoir un écran tactile.

### Démarrage automatique du listener :
```
sudo nano /lib/systemd/system/LinkyRPiListen.service
```
Copier les lignes suivantes dans le fichier :
```
[Unit]
Description=LinkyRPi Listen
After=multi-user.target LinkyRPiGUI.service
[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/pi/LinkyRPi/LinkyRPiListen.py > /home/pi/LinkyRPi/LinkyRPiListen.log 2>&1
WorkingDirectory=/home/pi/LinkyRPi
User=pi
[Install]
WantedBy=multi-user.target
```
Puis modifier les droits d'accès au fichier et recharger le deamon systemctl :
```
sudo chmod 644 /lib/systemd/system/LinkyRPiListen.service
sudo systemctl daemon-reload
sudo systemctl enable LinkyRPiListen.service
```

### Démarrage automatique de la GUI :
```
sudo nano /lib/systemd/system/LinkyRPiGUI.service
```
Copier les lignes suivantes dans le fichier :
```
[Unit]
Description=LinkyRPi GUI
After=syslog.target network.target multi-user.target nodm.service systemd-user-sessions.service runlevel5.target graphical.target
[Service]
Type=idle
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /home/pi/LinkyRPi/LinkyRPiGUI.py > /home/pi/LinkyRPi/LinkyRPiGUI.log 2>&1
WorkingDirectory=/home/pi/LinkyRPi
User=pi
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target default.target
```
Puis modifier les droits d'accès au fichier et recharger le deamon systemctl :
```
sudo chmod 644 /lib/systemd/system/LinkyRPiGUI.service
sudo systemctl daemon-reload
sudo systemctl enable LinkyRPiGUI.service
```


# Fonctionnement avec base de données
Ce chapitre détaille comment bénéficier d’une sauvegarde à long terme des données lues sur la TIC du compteur.
## Installation de Postgresql
Ce projet se base sur une base de données Postgresql. Il est possible d’adapter le fonctionnement de l’application à d’autres gestionnaires de bases de données tels que PHP, SQLite ou Oracle mais Postgresql a l’avantage d’être à la fois gratuit et très robuste. Il offre de plus, et de manière native, beaucoup de fonctions d’agrégation et d’analyse. C’est pourquoi il a été préféré aux autres.

Pour installer Postgresql, il suffit de suivre les tutoriels suivants (suivant le système sur lequel Postgresql sera installé) :

- Pour Windows : <https://www.postgresqltutorial.com/install-postgresql/>
- Pour MacOS : <https://www.postgresqltutorial.com/install-postgresql-macos/>
- Pour Linux : <https://www.postgresqltutorial.com/install-postgresql-linux/>

## Installation de PgAdmin
Afin de gérer facilement la base de données Postgresql, il est possible d’installer, sur la machine accueillant Postgresql, PgAdmin. Il s’agit d’un outil d’administration et de consultation accessible via un client web tel que Firefox ou Chrome :

<https://www.pgadmin.org/download/>

## Création de la DB (user, tables, etc...)
Tous les scripts permettant de créer la DB sont disponibles dans le fichier /sql/CreateDB.sql

## Création du service pour démarrage automatique du process de stockage
Une fois la base de données installée et le fichier de configuration mis à jour, il suffit de transférer le script de stockage « LinkyRPiDB.py » sur le Raspberry-Pi dans le répertoire « /usr/pi/Linky » et de paramétrer son démarrage automatique de la manière suivante :

```
sudo nano /lib/systemd/system/LinkyRPiDB.service
```
Copier les lignes suivantes dans le fichier :
```
[Unit]
Description=LinkyRPi DB
After=syslog.target network.target multi-user.target nodm.service systemd-user-sessions.service runlevel5.target graphical.target
[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/pi/LinkyRPi/LinkyRPiDB.py > /home/pi/LinkyRPi/LinkyRPiDB.log 2>&1
WorkingDirectory=/home/pi/LinkyRPi
User=pi
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target default.target
```
Puis modifier les droits d'accès au fichier et recharger le deamon systemctl :
```
sudo chmod 644 /lib/systemd/system/LinkyRPiDB.service
sudo systemctl daemon-reload
sudo systemctl enable LinkyRPiDB.service
```

Il faudra ensuite redémarrer le Raspberry-Pi afin de s’assurer que tout fonctionne bien et que le listener envoie bien les trames vers le module de stockage.
```
sudo reboot
```

## Exploitation des données sauvegardées dans la base de données
Une fois l’application démarrée avec le process de stockage, la base de données va commencer à se remplir au fur et à mesure des trames transmises par la TIC.

Il est donc désormais possible d’y accéder :

- Soit par SQL dans un terminal Postgres
- Soit par SQL via PgAdmin
- Soit par un outil de BI tel que [Tableau](https://www.tableau.com/fr-fr) ou [Qlik](https://www.qlik.com/fr-fr/) par exemple.
