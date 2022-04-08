#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Mickael Masci"

import serial
import time
from datetime import datetime
import csv
import os
import errno
import RPi.GPIO as GPIO
import sys
import configparser
import posix_ipc
import subprocess
import json
import linky


global connection
global connectDB
global firstTrame


oldTime = datetime.now()
newTime = datetime.now()
action = ""

def traceTime(action) :
    global newTime, oldTime
    newTime = datetime.now()
    delta = newTime - oldTime
    print(action + " à " + newTime.strftime("%H:%M:%S.%f") + " (" + str(delta) + ")")
    oldTime = newTime


traceTime("Démarrage")

# On ouvre le fichier de param et on recup les param
config = configparser.RawConfigParser()
config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
ldebug = int(config.get('PARAM','debugLevel'))

#Liste de toutes les mesures d'une trame Linky
list_measures = []

#Le tuple mesure contient une mesure Linky sous la forme (<code-mesure><valeur-mesure>)
mesure = ()


firstTrame = True
modeTIC = ""

#Definition de la classe bcolors pour afficher des traces en couleur à l'écran
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR

#Ouverture de la pile FIFO pour communication avec la UI
queueName = config.get('POSIX','queueName')
queueDepth = int(config.get('POSIX','queueDepth'))

try:
    q1 = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX, max_messages=queueDepth)
except :
    q1 = posix_ipc.MessageQueue(queueName)
    q1.close()
    q1.unlink()
    q1 = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX, max_messages=queueDepth)

traceTime("Queue créée")

#==============================================================================#
# Initialisation du process                                                    #
#==============================================================================#
def init():

    traceTime("Début INIT")

    #Détection du mode TIC en fonction du BAUDRATE détecté
    baud_dict = [1200, 9600]
    rateValue = 0
    modeTIC = ""

    for baud_rate in baud_dict:

        with serial.Serial(port='/dev/ttyAMA0', baudrate=baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.SEVENBITS, timeout=1) as ser:

            line = ser.readline()
            while b'\x02' not in line:  # recherche du caractère de début de trame
                line = ser.readline()

            # lecture de la première ligne de la première trame
            line = ser.readline()
            while True :
                line_str = line.decode("utf-8")

                rateFound = False
                if baud_rate == 1200 and "ADCO" in line_str :
                    print("Trouvé 1200")
                    ar = line_str.split(" ")
                    rateFound = True
                    rateValue = 1200
                    break
                elif baud_rate == 9600 and "ADSC" in line_str :
                    print("Trouvé 9600")
                    ar = line_str.split('\t')
                    rateFound = True
                    rateValue = 9600
                    break
                else :
                    rateFound = False
                    break

    if rateFound :
        if rateValue == 1200 :
            modeTIC = "HISTO"
        else :
            modeTIC = "STD"

    ser.close()

    traceTime("Mode TIC = " + modeTIC)
    return modeTIC

#==============================================================================#
# Traitement de la mesure lue                                                  #
#==============================================================================#
def treatmesure(mesureCode,mesureValue,mesureValue2) :
    #Les codes ci-dessous contiennent 2 valeurs : un horodatage + la valeur en question.
    #Du coup on bypass l'horodatage pour ne garder que la valeur
    if mesureCode in ["SMAXSN","SMAXSN1","SMAXSN2","SMAXSN3","SMAXSN-1","SMAXSN1-1","SMAXSN3-1","SMAXIN","SMAXIN-1","CCASN","CCASN-1","CCAIN","CCAIN-1","UMOY1","UMOY2","UMOY3","DPM1","FPM1","DPM2","FPM2","DPM3","FPM3"] :
        mesure = (mesureCode, mesureValue2.strip("\n"))
        if ldebug>2 : print("[" + bcolors.OK + ">>" + bcolors.RESET + "]" , mesureCode + " : " + mesureValue2.strip("\n"))
    else :
        mesure = (mesureCode, mesureValue)
        if ldebug>2 : print("[" + bcolors.OK + ">>" + bcolors.RESET + "]" , mesureCode + " : " + mesureValue)

    #traceTime("treatmesure avant append")
    list_measures.append(mesure)
    #traceTime("treatmesure après append")
    return list_measures



#==============================================================================#
# Traitement de la fin de trame                                                #
#==============================================================================#
def treattrame(list_measures):
    global connectDB
    global nbTrame

    #On ajoute les données techniques en fin de trame
    mesure = ("TICMODE", modeTIC)
    traceTime("treattrame avant append")
    list_measures.append(mesure)
    #traceTime("treattrame après append")

    #On traduit la trame reçue en un dictionnaire agnostique du type de fonctionnement de la TIC
    #traceTime("treattrame avant traduction")
    analysedDict = {}
    trameDict = dict(list_measures)
    analysedDict = linky.analyseTrame(dict(list_measures))
    #traceTime("treattrame après traduction")

    #On envoie le dictionnaire traduit à la UI sous forme de Json
    #trameJson = json.dumps(analysedDict, indent=4)
    trameJson = json.dumps(trameDict, indent=4)
    traceTime("treattrame après converions JSON")

    del list_measures[:]




#==============================================================================#
# Traitement des exceptions                                                    #
#==============================================================================#
def treaterror(errEvent,errCode,errValue) :
    traceTime("treaterror")






#==============================================================================#
# PRODEDURE PRINCIPALE                                                         #
#==============================================================================#
traceTime("Avant INIT")
modeTIC = ""
while modeTIC == "" :
    modeTIC = init()
    if modeTIC == "" :
        sleep(1)

#Lecture des trames pour TIC en mode historique
traceTime("Mise en écoute")
with serial.Serial(port='/dev/ttyAMA0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                   bytesize=serial.SEVENBITS, timeout=1) as ser:

    traceTime("Lecture des trames")

    # boucle d'attente du début de trame
    line = ser.readline()
    while b'\x02' not in line:  # recherche du caractère de début de trame
        line = ser.readline()

    # lecture de la première ligne de la première trame
    line = ser.readline()
    traceTime("Début de trame détecté")
    while True:
        line_str = line.decode("utf-8")
        ar = line_str.split(" ")
        traceTime("Trame splitée")
        try :
            list_measures = treatmesure(ar[0],ar[1],ar[2])
        except :
            #traceTime("Erreur décodage trame")
            pass

        #On détecte le caractère de fin de ligne
        if b'\x03' in line:
            traceTime("Fin de trame détecté")
            treattrame(list_measures)

        line = ser.readline()
