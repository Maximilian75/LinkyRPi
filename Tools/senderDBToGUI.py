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
import time
from datetime import datetime

config = configparser.RawConfigParser()
config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
DBuser = config.get('POSTGRESQL','user')
DBpassword = config.get('POSTGRESQL','password')
DBhost = config.get('POSTGRESQL','host')
DBport = config.get('POSTGRESQL','port')
DBdbname = config.get('POSTGRESQL','dbname')

#Connexion à la DB Postgresql sur le DataServer
try:
    connection = psycopg2.connect(user=DBuser,
                                  password=DBpassword,
                                  host=DBhost,
                                  port=DBport,
                                  dbname=DBdbname)

    connectDB = True

    print("Connected to DB")
    print("     -- host = " + DBhost)
    print("     -- port = " + DBport)
    print("     -- DB   = " + DBdbname)
except (Exception, Error) as error:
    #Si pb de connexion DB, alors pas grave, on continue en stand alone
    print("No DB connexion")
    print(error)
    print("EXIT !")
    quit()

#Ouverture de la pile FIFO pour communication avec la UI
queueName = config.get('POSIX','queueGUI')
queueDepth = int(config.get('POSIX','depthGUI'))
try:
    q1 = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX, max_messages=queueDepth)
    print("Queue UI créée")
except :
    print("La queue UI existe deja")
    q1 = posix_ipc.MessageQueue(queueName)


cursor = connection.cursor()

query = "select compteur.adressecompteur," + \
        "compteur.versiontic," + \
	    "mesures.dateheurelinky," + \
	    "abonnement.tarifsouscrit," + \
	    "mesures.periodetarifaireencours," + \
	    "mesures.indextotal as index00," + \
	    "COALESCE(mesures.indexhc, 0)  + COALESCE(mesures.indexejpnormale, 0) + COALESCE(mesures.indexhcjb, 0) as index01," + \
	    "COALESCE(mesures.indexhp, 0)  + COALESCE(mesures.indexejppointe, 0) + COALESCE(mesures.indexhpjb, 0) as index02," + \
	    "COALESCE(mesures.indexwe, 0)  + COALESCE(mesures.indexhcjw, 0) as index03," + \
	    "COALESCE(mesures.indexhpjw, 0) as index04," + \
	    "COALESCE(mesures.indexhcjr, 0) as index05," + \
	    "COALESCE(mesures.indexhpjr, 0) as index06," + \
	    "mesures.index07," + \
	    "mesures.index08," + \
	    "mesures.index09," + \
	    "mesures.index10," + \
	    "mesures.energieactivesoutireedistributeurindex1," + \
	    "mesures.energieactivesoutireedistributeurindex2," + \
	    "mesures.energieactivesoutireedistributeurindex3," + \
	    "mesures.energieactivesoutireedistributeurindex4," + \
	    "mesures.intensiteinstantanee," + \
	    "mesures.tensionefficacephase1," + \
	    "abonnement.intensitesouscrite," + \
	    "abonnement.puissancecoupure," + \
	    "mesures.puissanceapparente," + \
	    "mesures.puissancemaxatteinte," + \
	    "mesures.puissanceapparentemaxn1," + \
	    "mesures.pointncourbechargeactivesoutiree," + \
	    "mesures.pointn1courbechargeactivesoutiree," + \
	    "mesures.tensionmoyennephase1," + \
	    "mesures.messagecourt," + \
	    "compteur.PRM," + \
	    "mesures.periodetarifaireencours," + \
	    "mesures.numerojourcalendrierfournisseur," + \
	    "mesures.numeroprochainjourcalendrierfournisseur," + \
	    "mesures.profilprochainjourcalendrierfournisseur," + \
	    "mesures.modetic," + \
	    "mesures.contactsec," + \
	    "mesures.organedecoupure," + \
	    "mesures.cachebornedistributeur," + \
	    "mesures.surtensionphase," + \
	    "mesures.depassementpuissanceref," + \
	    "mesures.fonctionnement," + \
	    "mesures.sensenergieactive," + \
	    "mesures.tarifencoursf," + \
	    "mesures.tarifencoursd," + \
	    "mesures.horlogedegradee," + \
	    "mesures.sortiecommeuridis," + \
	    "mesures.statutcpl," + \
	    "mesures.synchrocpl," + \
	    "mesures.couleurtempojour," + \
	    "mesures.couleurtempodemain," + \
	    "mesures.preavispointesmobiles," + \
	    "mesures.pointemobile," + \
	    "mesures.modetic as registremodetic," + \
	    "mesures.couleurtempodemain as couleurdemain," + \
	    "compteur.typecompteur," + \
	    "compteur.nomcompteur," + \
	    "mesures.indexhc," + \
	    "mesures.indexhp," + \
	    "mesures.indextotal," + \
	    "abonnement.horaireshc," + \
	    "mesures.relais1," + \
	    "mesures.relais2," + \
	    "mesures.relais3," + \
	    "mesures.relais4," + \
	    "mesures.relais5," + \
	    "mesures.relais6," + \
	    "mesures.relais7," + \
	    "mesures.relais8 " + \
        "from public.compteur right join public.abonnement on (abonnement.adressecompteur = compteur.adressecompteur)" + \
        "right join public.mesures    on (mesures.abonnementid = abonnement.abonnementid) order by mesures.DateHeureLinky " + \
        "limit 1000"

cursor.execute(query)
data = cursor.fetchone()

while data != "" :
    analysedDict = {}
    analysedDict.update({"AdresseCompteur":data[0]})
    analysedDict.update({"VersionTIC":data[1]})

    dateString = str(data[2])
    dateHeureLinky = "X - " + dateString[8:10] + "/" + dateString[5:7] + "/" + dateString[0:4] + " - " + dateString[11:]
    analysedDict.update({"DateHeureLinky":dateHeureLinky})

    print(dateHeureLinky)

    analysedDict.update({"TarifSouscrit":data[3]})
    analysedDict.update({"PeriodeTarifaireEnCours":data[4].strip()})
    analysedDict.update({"Index00":data[5]})
    analysedDict.update({"Index01":data[6]})
    analysedDict.update({"Index02":data[7]})
    analysedDict.update({"Index03":data[8]})
    analysedDict.update({"Index04":data[9]})
    analysedDict.update({"Index05":data[10]})
    analysedDict.update({"Index06":data[11]})
    analysedDict.update({"Index07":data[12]})
    analysedDict.update({"Index08":data[13]})
    analysedDict.update({"Index09":data[14]})
    analysedDict.update({"Index10":data[15]})
    analysedDict.update({"EnergieActiveSoutireeDistributeurIndex1":data[16]})
    analysedDict.update({"EnergieActiveSoutireeDistributeurIndex2":data[17]})
    analysedDict.update({"EnergieActiveSoutireeDistributeurIndex3":data[18]})
    analysedDict.update({"EnergieActiveSoutireeDistributeurIndex4":data[19]})
    analysedDict.update({"IntensiteInstantanee":data[20]})
    analysedDict.update({"IntensiteInstantaneePhase1":data[20]})
    analysedDict.update({"TensionEfficacePhase1":data[21]})
    analysedDict.update({"IntensiteSouscrite":data[22]})
    analysedDict.update({"PuissanceCoupure":data[23]})
    analysedDict.update({"PuissanceApparente":data[24]})
    analysedDict.update({"PuissanceMaxAtteinte":data[25]})
    analysedDict.update({"PuissanceApparenteMaxN-1":data[26]})
    analysedDict.update({"PointNCourbeChargeActiveSoutiree":data[27]})
    analysedDict.update({"PointN-1CourbeChargeActiveSoutiree":data[28]})
    analysedDict.update({"TensionMoyennePhase1":data[29]})
    analysedDict.update({"MessageCourt":data[30]})
    analysedDict.update({"PRM":data[31]})
    analysedDict.update({"CodeTarifEnCours":data[32]})
    analysedDict.update({"NumeroJourCalendrierFournisseur":data[33]})
    analysedDict.update({"NumeroProchainJourCalendrierFournisseur":data[34]})
    analysedDict.update({"ProfilProchainJourCalendrierFournisseur":data[35]})
    analysedDict.update({"ModeTIC":data[36]})
    analysedDict.update({"ContactSec":data[37]})
    analysedDict.update({"OrganeDeCoupure":data[38]})
    analysedDict.update({"CacheBorneDistributeur":data[39]})
    analysedDict.update({"SurtensionPhase":data[40]})
    analysedDict.update({"DepassementPuissanceRef":data[41]})
    analysedDict.update({"Fonctionnement":data[42]})
    analysedDict.update({"SensEnergieActive":data[43]})
    analysedDict.update({"TarifEnCoursF":data[44]})
    analysedDict.update({"TarifEnCoursD":data[45]})
    analysedDict.update({"HorlogeDegradee":data[46]})
    analysedDict.update({"SortieCommEuridis":data[47]})
    analysedDict.update({"StatutCPL":data[48]})
    analysedDict.update({"SynchroCPL":data[49]})
    analysedDict.update({"CouleurTempoJour":data[50]})
    analysedDict.update({"CouleurTempoDemain":data[51]})
    analysedDict.update({"PreavisPointesMobiles":data[52]})
    analysedDict.update({"PointeMobile":data[53]})
    analysedDict.update({"RegistreModeTIC":data[54]})
    analysedDict.update({"CouleurDemain":data[55]})
    analysedDict.update({"TypeCompteur":data[56].strip()})
    analysedDict.update({"NomCompteur":data[57].replace("   ", "\n")})
    analysedDict.update({"IndexHC":data[58]})
    analysedDict.update({"IndexHP":data[59]})
    analysedDict.update({"IndexTotal":data[60]})
    analysedDict.update({"HorairesHC":data[61]})

    if data[62] :
        relais0 = '1'
    else :
        relais0 = '0'

    if data[63] :
        relais1 = '1'
    else :
        relais1 = '0'

    if data[64] :
        relais2 = '1'
    else :
        relais2 = '0'

    if data[65] :
        relais3 = '1'
    else :
        relais3 = '0'

    if data[66] :
        relais4 = '1'
    else :
        relais4 = '0'

    if data[67] :
        relais5 = '1'
    else :
        relais5 = '0'

    if data[68] :
        relais6 = '1'
    else :
        relais6 = '0'

    if data[69] :
        relais7 = '1'
    else :
        relais7 = '0'

    analysedDict.update({"Relais":relais0+relais1+relais2+relais3+relais4+relais5+relais6+relais7})

    trameJson = json.dumps(analysedDict, indent=4)
#    print(trameJson)
    q1.send(trameJson)

    time.sleep(1)

    data = cursor.fetchone()
