import configparser
import posix_ipc
import subprocess
import json
import time
import linkyRPiTranslate
import time
from datetime import datetime


print("=============================================================================")
print("Démarrage du process dispatcher : " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))

# On ouvre le fichier de param et on recup les param
config = configparser.RawConfigParser()
config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
ldebug = int(config.get('PARAM','debuglevel'))

#Definition de la classe bcolors pour afficher des traces en couleur à l'écran
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR


#Ouverture de la pile FIFO pour écoute du le listener
queueName = config.get('POSIX','queueDispatch')
queueDepth = int(config.get('POSIX','depthDispatch'))
try:
    queueDispatch = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX, max_messages=queueDepth)
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue " + queueName + " créée")
except :
    if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue " + queueName + " existe deja")
    queueDispatch = posix_ipc.MessageQueue(queueName)

#Ouverture de la pile FIFO pour communication avec la UI
queueName = config.get('POSIX','queueGUI')
queueDepth = int(config.get('POSIX','depthGUI'))
try:
    queueGUI = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX, max_messages=queueDepth)
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue " + queueName + " créée")
except :
    if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue " + queueName + " existe deja")
    try :
        queueGUI = posix_ipc.MessageQueue(queueName)
    except :
        print("pas glop")

#Ouverture de la pile FIFO pour envoi vers la DB
queueName = config.get('POSIX','queueDB')
queueDepth = int(config.get('POSIX','depthDB'))
try:
    queueDB = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX)
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue DB créée")
except :
    if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue DB existe deja")
    queueDB = posix_ipc.MessageQueue(queueName)

#Ouverture de la pile FIFO pour envoi vers MQTT
queueName = config.get('POSIX','queueMQTT')
queueDepth = int(config.get('POSIX','depthMQTT'))
try:
    queueMQTT = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX)
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue MQTT créée")
except :
    if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue MQTT existe deja")
    queueMQTT = posix_ipc.MessageQueue(queueName)







#==============================================================================#
# Trace de la trame dans un fichier texte (pratique pour faire du debug)       #
#==============================================================================#
def writeToFile(analysedDict) :

    global nextTrace

    tracePath = config.get('PATH','tracePath')

    #On trace les trames dans un fichier en cas de besoin, c'est pratique pour debugger la GUI sans faire tourner le listener !
    if "AdresseCompteur" in analysedDict :
        filename = config.get('PATH','tracePath') + "/" + analysedDict["AdresseCompteur"] + ".log"
    else :
        filename = config.get('PATH','tracePath') + "/000000000000.log"

    #Ouverture du fichier de log des trame
    f = open(filename,'a')
    f.write(str(analysedDict) + "\n")
    f.close()
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Enregistrement de la trame courante dans le fichier " + filename)




#==============================================================================#
# PRODEDURE PRINCIPALE                                                         #
#==============================================================================#
nextTraceDB = time.monotonic()
nextTraceMQTT = time.monotonic()
nexttraceActive = time.monotonic()

while True:


    traceActive = config.get('PARAM','traceActive')
    MQTTActive = config.get('MQTT','MQTTActive')
    DBActive = config.get('POSTGRESQL','active')

    # On lit une trame dans la queue de dispatching
    try :
        msg = queueDispatch.receive(timeout = 1)
        trameReceived = True
    except Exception as e:
        #La queue est vide, on reboucle direct
        trameReceived = False


    if trameReceived :
        msgJson = json.loads(msg[0])
        analysedDict = dict(msgJson)
        trameJson = json.dumps(analysedDict, indent=4)

        # Forward direct vers la GUI
        #print("Envoi vers la GUI")
        try:
            queueGUI.send(trameJson, timeout = 0)
        except:
            pass

        # Si envoi vers la DB activé
        if (DBActive == "True") and (time.monotonic() >= nextTraceDB) :
            #print("Envoi vers la DB")
            try:
                queueDB.send(trameJson, timeout = 0)
            except:
                pass

            DBFreq = config.get('POSTGRESQL','refreshDB')
            nextTraceDB = time.monotonic() + int(DBFreq)


        # Si envoi vers MQTT activé
        if (MQTTActive == "True") and (time.monotonic() >= nextTraceMQTT) :
            #print("Envoi MQTT")
            try:
                queueMQTT.send(trameJson, timeout = 0)
            except:
                pass

            MQTTFreq = config.get('MQTT','refreshMQTT')
            nextTraceMQTT = time.monotonic() + int(MQTTFreq)


        # Si enregistrement trame dans un fichier activé
        if (traceActive == "True") and (time.monotonic() >= nexttraceActive) :
            #print("Trace dans fichier")
            try:
                writeToFile(analysedDict)
            except:
                pass
                
            traceFreq = int(config.get('PARAM','traceFreq'))
            nexttraceActive = time.monotonic() + int(TraceFreq)
