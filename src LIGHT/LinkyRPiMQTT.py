import configparser
from datetime import datetime
import posix_ipc
import subprocess
import json
import time
import linkyRPiTranslate
import paho.mqtt.client as mqtt
import sys
import os
import psutil


print("=============================================================================")
print("Démarrage du process MQTT : " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))

# On ouvre le fichier de param et on recup les param
config = configparser.RawConfigParser()
config.read('/home/linkyrpi/LinkyRPi/LinkyRPi.conf')
ldebug = int(config.get('PARAM','debuglevel'))

syllabus, dataFormat = linkyRPiTranslate.generateSyllabus()
MQTTTopic = linkyRPiTranslate.getMQTTTopic()

#Definition de la classe bcolors pour afficher des traces en couleur à l'écran
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR


#Ouverture de la pile FIFO pour envoi vers MQTT
if config.get('MQTT', 'MQTTActive') == "True" :
    activeMQTT = True
    queueName = config.get('POSIX','queueMQTT')
    queueDepth = int(config.get('POSIX','depthMQTT'))
    try:
        queueMQTT = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREAT)
        if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue MQTT créée")
    except :
        if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue MQTT existe deja")
        queueMQTT = posix_ipc.MessageQueue(queueName)
else :
    activeMQTT = False


def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to MQTT Broker at " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
    else:
        print("Failed to connect at " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + ", return code : " + str (rc))

def on_disconnect(client, userdata, flags, rc, properties):
   print("Disconected at " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + ", return code : " + str (rc))


#Connexion au broker MQTT
broker = config.get('MQTT', 'MQTTAddress')
port = int(config.get('MQTT', 'MQTTPort'))
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(config.get('MQTT', 'MQTTUser'), config.get('MQTT', 'MQTTPass'))
client.on_connect = on_connect
client.on_disconnect = on_disconnect

notConnected = True
while notConnected :
    try :
        client.connect(broker, port)
        notConnected = False
    except :
        time.sleep(1)

client.loop_start()
while True:

    # On lit une trame dans la queue de dispatching
    try :
        msg = queueMQTT.receive(timeout = 1)
        msgJson = json.loads(msg[0])
        trameReceived = True
    except Exception as e:
        #La queue est vide, on reboucle direct
        trameReceived = False

    if trameReceived :
        try :
            #On push les stats du Raspberry Pi
            client.publish("LinkyRPi/Status/Execution","ON")
            client.publish("LinkyRPi/Status/CpuPercent",psutil.cpu_percent())
            #client.publish("LinkyRPi/Status/CpuAverage",psutil.getloadavg())

            memory = psutil.virtual_memory()
            client.publish("LinkyRPi/Status/RamAvailable",round(memory.available/1024.0/1024.0,1))
            client.publish("LinkyRPi/Status/RamTotal",round(memory.total/1024.0/1024.0,1))
            client.publish("LinkyRPi/Status/RamPercent",memory.percent)

            disk = psutil.disk_usage('/')
            client.publish("LinkyRPi/Status/SDAvailable",round(disk.free/1024.0/1024.0/1024.0,1))
            client.publish("LinkyRPi/Status/SDTotal",round(disk.total/1024.0/1024.0/1024.0,1))
            client.publish("LinkyRPi/Status/SDPercent",disk.percent)

            #cmd = "ifconfig eth0|grep 'inet '|cut -d' ' -f 10"
            #result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
            #if (result != '') and (result != 'wlan0: error fetching interface information: Device not found') :
            #    client.publish("LinkyRPi/Network/Ethernet/AdresseIP",result.rstrip("\n"))

            #Etat de la connexion WiFi
            cmd = "ifconfig wlan0|grep 'inet '|cut -d' ' -f 10"
            result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
            if result != '' :
                client.publish("LinkyRPi/Network/WiFi/AdresseIP",result.rstrip("\n"))
                cmd2 = "iwconfig wlan0|grep Quality|cut -d '=' -f 2|cut -d ' ' -f 1"
                result2 = subprocess.run(cmd2,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
                client.publish("LinkyRPi/Network/WiFi/Force",int(result2.split("/")[0]) / int(result2.split("/")[1]) * 100)
                cmd2 = "iwconfig wlan0|grep ESSID|cut -d ':' -f 2"
                result2 = subprocess.run(cmd2,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
                client.publish("LinkyRPi/Network/WiFi/Name",result2.rstrip("\n"))

            analysedDict = dict(msgJson)
            for key in analysedDict :
                MFormat = dataFormat[key]
                MTopic = MQTTTopic[key][0] + key
                if MFormat == "char" :
                    analysedDict[key] = analysedDict[key].replace("\n", "")
                    analysedDict[key] = analysedDict[key].replace("\r", "")
                    MValue = '{"' + MQTTTopic[key][1] + '": "' + analysedDict[key] + '", "unit_of_measurement": "' + MQTTTopic[key][2] + '", "icon": "' + MQTTTopic[key][3] + '"}'
                else :
                    MValue = '{"' + MQTTTopic[key][1] + '": ' + str(analysedDict[key]) + ', "unit_of_measurement": "' + MQTTTopic[key][2] + '", "icon": "' + MQTTTopic[key][3] + '"}'

                client.publish(MTopic, MValue)
                trameReceived = False
        except Exception as e:
            print("Error while pushing at " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
            print(e)
            client.disconnect()
            notConnected = True
            time.sleep(10)
            print("Trying to reconnect...")

            while notConnected :
                try :
                    client.connect(broker, port)
                    notConnected = False
                    print("Reconnected at " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
                except :
                    time.sleep(1)

                client.loop_start()

    else :
        time.sleep(1)
