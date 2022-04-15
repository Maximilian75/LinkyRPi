#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This file is part of LinkyRPi.
#LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
#(c)Copyright Mikaël Masci 2022


import psycopg2
from psycopg2 import Error
import psycopg2.extras
import configparser
import posix_ipc
import json
from datetime import datetime
import uuid
import schedule
import time
import linkyRPiTranslate

compteurInit = False
abonnementInit = False
abonnementUUID = ""

syllabus, dataFormat = linkyRPiTranslate.generateSyllabus()

#Definition de la classe bcolors pour afficher des traces en couleur à l'écran
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR




#Procédure d'enregistrement de l'abonnement en cours
def initAbonnement(analysedDict) :

    global abonnementUUID

    # D'abord on vérifie si l'abonnement existe et on récupère éventuellement son ID
    cursor = connection.cursor()
    query = "".join(["select abonnementid from public.abonnement where " , "adressecompteur = '" , analysedDict['AdresseCompteur'] , "' AND " ,
                     "tarifsouscrit = '" , analysedDict['TarifSouscrit'] , "' AND " , "intensitesouscrite = " , str(analysedDict['IntensiteSouscrite'])])
    #print(query)

    cursor.execute(query)
    data = cursor.fetchall()

    # Si le compteur est inconnu alors on le crée dans la DB
    if data == [] :
        if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] Nouvel abonnement détecté")

        #On regarde si un abonnement est actif pour ce compteur.
        query = "".join(["select abonnementid from public.abonnement where " , "adressecompteur = '" , analysedDict['AdresseCompteur'] , "' AND " , "status = 'OPEN'"])
        #print(query)
        cursor.execute(query)
        data = cursor.fetchall()

        # Si oui, on le cloture
        if data != [] :
            abonnementUUID = data[0][0]
            query = "update public.abonnement set status = 'CLOS', dateclos = '" + str(datetime.now()) + "' where abonnementid = '" + abonnementUUID + "'"
            #print(query)
            cursor.execute(query)

        #Puis on crée le nouvel'abonnement
        abonnementUUID = str(uuid.uuid4())
        query = "".join(["insert into public.abonnement (abonnementid, adressecompteur, tarifsouscrit, horaireshc, intensitesouscrite, puissancecoupure, datecre, status) VALUES ('" ,
                         abonnementUUID , "', '" , analysedDict['AdresseCompteur'] , "', '" , analysedDict['TarifSouscrit'] , "', '"])
        if "HorairesHC" in analysedDict :
            query = query + analysedDict['HorairesHC'] + "', '"
        else :
            query = query + "', '"
        query = query + str(analysedDict['IntensiteSouscrite']) + "', "
        if "PuissanceCoupure" in analysedDict :
            query = query + str(analysedDict['PuissanceCoupure']) + ", '"
        else :
            query = query + ", '"
        query = query + str(datetime.now()) + "', 'OPEN')"
        #print(query)
        cursor.execute(query)

    else :
        if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] L'abonnement existe déjà")
        abonnementUUID = data[0][0]
    connection.commit()




# On ouvre le fichier de param et on recup les param
config = configparser.RawConfigParser()
config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
DBuser = config.get('POSTGRESQL','user')
DBpassword = config.get('POSTGRESQL','password')
DBhost = config.get('POSTGRESQL','host')
DBport = config.get('POSTGRESQL','port')
DBdbname = config.get('POSTGRESQL','dbname')
refreshDB = config.get('POSTGRESQL','refreshDB')


ldebug = int(config.get('PARAM','debugLevel'))

#Ouverture de la pile FIFO pour communication avec la DB
activeDBVal = config.get('POSTGRESQL','active')
if activeDBVal == "True" :
    activeDB = True
    queueName = config.get('POSIX','queueDB')
    queueDepth = int(config.get('POSIX','depthDB'))
    try:
        q2 = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREAT)
        if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue DB créée")
    except :
        if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue DB existe deja")
        q2 = posix_ipc.MessageQueue(queueName)
else :
    activeDB = False


#Connexion à la DB Postgresql sur le DataServer
try:
    connection = psycopg2.connect(user=DBuser,
                                  password=DBpassword,
                                  host=DBhost,
                                  port=DBport,
                                  dbname=DBdbname)

    connectDB = True

    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Connected to DB")
    if ldebug>0 : print("     -- host = " + DBhost)
    if ldebug>0 : print("     -- port = " + DBport)
    if ldebug>0 : print("     -- DB   = " + DBdbname)
except (Exception, Error) as error:
    #Si pb de connexion DB, alors pas grave, on continue en stand alone
    if ldebug>0 : print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "] No DB connexion")
    if ldebug>0 : print(error)
    if ldebug>0 : print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "] EXIT !")
    quit()


nextTrace = time.monotonic()

#On part en boucle infinie
while True:

    # On lit une trame dans la queue
    try :
        msg = q2.receive(timeout = 1)
        msgJson = json.loads(msg[0])
        analysedDict = dict(msgJson)
        trameReceived = True
    except Exception as e:
        #La queue est vide, on reboucle direct
        trameReceived = False

    if trameReceived :

        # A la première trame reçue on check si le compteur est déjà référencé dans la DB
        # S'il ne l'est pas, on le crée
        if not compteurInit and "AdresseCompteur" in analysedDict :
            cursor = connection.cursor()
            query = "".join(["SELECT adressecompteur FROM public.compteur as c WHERE c.adressecompteur = '" , analysedDict['AdresseCompteur'] , "'"])
            try:
                cursor.execute(query)
                data = cursor.fetchall()

                # Si le compteur est inconnu alors on le crée dans la DB
                if data == [] :
                    if ldebug>1 : print("[" + bcolors.WARNING + "i-" + bcolors.RESET + "]Compteur ", analysedDict['AdresseCompteur'], " inconnu...")
                    if "PRM" in analysedDict :
                        PRM = analysedDict['PRM']
                    else :
                        PRM = ""

                    if "VersionTIC" in analysedDict :
                        VersionTIC = analysedDict['VersionTIC']
                    else :
                        VersionTIC = ""

                    query = "".join(["INSERT INTO public.compteur(adressecompteur, prm, typecompteur, nomcompteur, versiontic) VALUES ('",
                                     analysedDict['AdresseCompteur'] , "','" , PRM , "','" , analysedDict['TypeCompteur'] , "','" , analysedDict['NomCompteur'].replace("\n", " ") , "','" , VersionTIC , "')"])
                    #print(query)
                    try:
                        cursor.execute(query)
                        connection.commit()
                    except (Exception, Error) as error:
                        if ldebug>0 : print(error)
                else :
                    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "]Compteur ", analysedDict['AdresseCompteur'], " deja connu...")
            except (Exception, Error) as error:
                if ldebug>0 : print(error)

            compteurInit = True

        # De même à la première trame on initialise la DB avec les données de l'abonnement en cours
        # Puis la proc s'exécutera touts les jours à minuit pour prendre en compte un éventuel changement d'abonnemen
        if not abonnementInit :
            initAbonnement(analysedDict)
            abonnementInit = True
            schedule.every().day.at("00:00").do(initAbonnement, analysedDict)

        # Ensuite on charge les données dans la table des mesures
        # La query est construite en fonction des mesures présentes dans le dictionnaire (et donc dans la trame)
        # Note : pour la construire on concatène avec .join() plutôt qu'avec des + car .join() est plus rapide ;)
        queryInsert = "insert into public.mesures (abonnementid, "
        queryValues = "".join([" VALUES ('" , abonnementUUID , "', "])

        #On boucle sur le dictionnaire pour constituer la query d'Insert
        for key in analysedDict :

            #On by-pass les données liées au compteur, à l'abonnement ou aux index, gérées par ailleurs
            if key not in (['AdresseCompteur', 'PRM', 'TypeCompteur', 'NomCompteur', 'CouleurDemain', 'VersionTIC', 'TarifSouscrit',
                            'HorairesHC', 'IntensiteSouscrite', 'PuissanceCoupure', 'Relais', 'Index00', 'Index01', 'Index02', 'Index03',
                            'Index04', 'Index05', 'Index06', 'CodeTarifEnCours', 'RegistreModeTIC']) :

                queryInsert = "".join([queryInsert , key.replace("-", ""), ", "])

                #Cas de l'horodatage Linky qu'il faut remettre en forme
                if key == "DateHeureLinky":
                    queryValues = "".join([queryValues, "'", analysedDict[key][4:14], " ", analysedDict[key][17:], "', "])
                    #print(analysedDict["DateHeureLinky"])

                #Si la donnée est de type string, il faut mettre des '' de part et d'autre dans la query
                elif dataFormat[key] == "char" :
                    queryValues = "".join([queryValues, "'", str(analysedDict[key]).replace("'", " ") , "', "])

                #Sinon, pour les mesures numériques, pas besoin des ''
                else :
                    queryValues = "".join([queryValues , str(analysedDict[key]).replace("'", " ") , ", "])



        if "EnergieActiveSoutireeDistributeurIndex1" in analysedDict :
            if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
                queryInsert = "".join([queryInsert , "indexhcsaisonbasse, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex1"]) , ", "])
            else :
                queryInsert = "".join([queryInsert , "energieactivesoutireedistributeurindex1, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex1"]) , ", "])

        if "EnergieActiveSoutireeDistributeurIndex2" in analysedDict :
            if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
                queryInsert = "".join([queryInsert , "indexhpsaisonbasse, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex2"]) , ", "])
            else :
                queryInsert = "".join([queryInsert , "energieactivesoutireedistributeurindex2, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex2"]) , ", "])

        if "EnergieActiveSoutireeDistributeurIndex3" in analysedDict :
            if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
                queryInsert = "".join([queryInsert , "indexhcsaisonhaute, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex3"]) , ", "])
            else :
                queryInsert = "".join([queryInsert , "energieactivesoutireedistributeurindex3, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex3"]) , ", "])

        if "EnergieActiveSoutireeDistributeurIndex4" in analysedDict :
            if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
                queryInsert = "".join([queryInsert , "indexhpsaisonhaute, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex4"]) , ", "])
            else :
                queryInsert = "".join([queryInsert , "energieactivesoutireedistributeurindex4, "])
                queryValues = "".join([queryValues , str(analysedDict["EnergieActiveSoutireeDistributeurIndex4"]) , ", "])

        if 'Relais' in analysedDict :
            queryInsert = "".join([queryInsert , "relais1, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][0]))) , ", "])
            queryInsert = "".join([queryInsert , "relais2, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][1]))) , ", "])
            queryInsert = "".join([queryInsert , "relais3, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][2]))) , ", "])
            queryInsert = "".join([queryInsert , "relais4, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][3]))) , ", "])
            queryInsert = "".join([queryInsert , "relais5, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][4]))) , ", "])
            queryInsert = "".join([queryInsert , "relais6, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][5]))) , ", "])
            queryInsert = "".join([queryInsert , "relais7, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][6]))) , ", "])
            queryInsert = "".join([queryInsert , "relais8, "])
            queryValues = "".join([queryValues , str(not(bool(analysedDict["Relais"][7]))) , ", "])

        query = "".join([queryInsert[:-2], ")" , queryValues[:-2], ")"])
        #print(query)

        if (time.monotonic() >= nextTrace) :
            cursor.execute(query)
            connection.commit()
            config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
            refreshDB = config.get('POSTGRESQL','refreshDB')
            nextTrace = time.monotonic() + int(refreshDB)
