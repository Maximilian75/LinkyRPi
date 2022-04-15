#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This file is part of LinkyRPi.
#LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
#(c)Copyright Mikaël Masci 2022

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
import linkyRPiTranslate

global connection
global connectDB
global firstTrame


syllabus, dataFormat = linkyRPiTranslate.generateSyllabus()

# On ouvre le fichier de param et on recup les param
config = configparser.RawConfigParser()
config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
ldebug = int(config.get('PARAM','debugLevel'))

traceFile = config.get('PARAM','traceFile')
traceFreq = int(config.get('PARAM','traceFreq'))

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




if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Démarrage du process listenner")

#Ouverture de la pile FIFO pour communication avec la UI
queueName = config.get('POSIX','queueGUI')
queueDepth = int(config.get('POSIX','depthGUI'))
try:
    q1 = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX, max_messages=queueDepth)
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue UI créée")
except :
    if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue UI existe deja")
    q1 = posix_ipc.MessageQueue(queueName)



#Ouverture de la pile FIFO pour communication avec la DB
activeDBVal = config.get('POSTGRESQL','active')
if activeDBVal == "True" :
    activeDB = True
    queueName = config.get('POSIX','queueDB')
    queueDepth = int(config.get('POSIX','depthDB'))
    try:
        q2 = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX)
        if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue DB créée")
    except :
        if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue DB existe deja")
        q2 = posix_ipc.MessageQueue(queueName)
else :
    activeDB = False

#==============================================================================#
# Initialisation du process                                                    #
#==============================================================================#
def init():


    #Détection du mode TIC en fonction du BAUDRATE détecté
    baud_dict = [1200, 9600]
    rateValue = 0
    modeTIC = ""

    for baud_rate in baud_dict:

        with serial.Serial(port='/dev/ttyAMA0', baudrate=baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.SEVENBITS, timeout=0) as ser:

            line = ser.readline()
            while b'\x02' not in line:  # recherche du caractère de début de trame
                line = ser.readline()

            # lecture de la première ligne de la première trame
            line = ser.readline()
            while True :
                line_str = line.decode("utf-8")

                rateFound = False
                if baud_rate == 1200 and "ADCO" in line_str :
                    #print("Trouvé 1200")
                    ar = line_str.split(" ")
                    rateFound = True
                    rateValue = 1200
                    break
                elif baud_rate == 9600 and "ADSC" in line_str :
                    #print("Trouvé 9600")
                    ar = line_str.split('\t')
                    rateFound = True
                    rateValue = 9600
                    break
                else :
                    rateFound = False
                    break

    if rateFound :
        if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Baud rate détecté : " + str(rateValue))
        if rateValue == 1200 :
            modeTIC = "Historique"
            if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] TIC en mode HISTORIQUE")
        else :
            modeTIC = "Standard"
            if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] TIC en mode STANDARD")

    else :
        if ldebug>0 : print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "] Unable to detect the baud rate")
    ser.close()

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

    list_measures.append(mesure)
    return list_measures


#==============================================================================#
# Traitement de la fin de trame                                                #
#==============================================================================#
def treattrame(list_measures):
    global connectDB ,nbTrame, oldTime, activeDB, syllabus, dataFormat

    #On ajoute les données techniques en fin de trame
    mesure = ("TICMODE", modeTIC)
    list_measures.append(mesure)
    if ldebug>2 : print("[" + bcolors.OK + ">>" + bcolors.RESET + "] TICMODE : " + modeTIC)
    if ldebug>1 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Fin de trame détectée")

    #On traduit la trame reçue en un dictionnaire agnostique du type de fonctionnement de la TIC
    analysedDict = {}
    analysedDict = linkyRPiTranslate.analyseTrame(syllabus, dataFormat, dict(list_measures))

    #On envoie le dictionnaire traduit à la UI sous forme de Json
    trameJson = json.dumps(analysedDict, indent=4)
    q1.send(trameJson)

    #On trace le dictionnaire dans un fichier texte (si actif)
    writeToFile(analysedDict)

    #Si la DB est en ligne on sauvegarde les données
    if activeDB :
        q2.send(trameJson)

    #On vide le tampon de trame pour traiter la suivante
    del list_measures[:]





#==============================================================================#
# Traitement des exceptions                                                    #
#==============================================================================#
def treaterror(errEvent,errCode,errValue) :
    if ldebug>0 : print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "]",errEvent,' : ' , errCode , ' = ' ,errValue)
    #Ici on va pousser l'ensemble des mesures de la trame dans le topic Kafka pour la Log



#==============================================================================#
# Trace de la trame dans un fichier texte (pratique pour faire du debug)       #
#==============================================================================#
def writeToFile(analysedDict) :

    global nextTrace

    config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
    traceFile = config.get('PARAM','traceFile')
    traceFreq = config.get('PARAM','traceFreq')

    if traceFile and (time.monotonic() >= nextTrace) :
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

        #Calcul de l'heure de la prochaine trace
        nextTrace = time.monotonic() + int(traceFreq)

#==============================================================================#
# PRODEDURE PRINCIPALE                                                         #
#==============================================================================#
traceFreq = config.get('PARAM','traceFreq')
nextTrace = time.monotonic() + int(traceFreq)

modeTIC = ""
while modeTIC == "" :
    modeTIC = init()
    if modeTIC == "" :
        time.sleep(1)



#Lecture des trames pour TIC en mode historique
if modeTIC == "Historique" :
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Mise en écoute en mode HISTORIQUE")
    with serial.Serial(port='/dev/ttyAMA0', baudrate=1200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.SEVENBITS, timeout=1) as ser:

        if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Lecture trames")

        # boucle d'attente du début de trame
        line = ser.readline()
        while b'\x02' not in line:  # recherche du caractère de début de trame
            line = ser.readline()

        # lecture de la première ligne de la première trame
        line = ser.readline()
        if ldebug>0 : print("[" + bcolors.OK + ">>" + bcolors.RESET + "] Debut de trame détecté à " + datetime.now().strftime("%H:%M:%S.%f"))
        while True:
            line_str = line.decode("utf-8")
            ar = line_str.split(" ")

            try :
                list_measures = treatmesure(ar[0],ar[1],ar[2])
            except :
                print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "] Probleme de decodage ligne : " + line_str)

            #On détecte le caractère de fin de ligne
            if b'\x03' in line:
                treattrame(list_measures)
                ser.reset_input_buffer()    # On vide le buffer du port série pour éviter le stacking
                line = ser.readline()
                while b'\x02' not in line:  # recherche du caractère de début de la prochaine trame
                    line = ser.readline()

            line = ser.readline()

#Lecture des trames pour TIC en mode standars
elif modeTIC == "Standard" :
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Mise en écoute en mode STANDARD")
    with serial.Serial(port='/dev/ttyAMA0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.SEVENBITS, timeout=5) as ser:

        if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Lecture trames")

        # boucle d'attente du début de trame
        line = ser.readline()
        while b'\x02' not in line:  # recherche du caractère de début de trame
            line = ser.readline()

        # lecture de la première ligne de la première trame
        line = ser.readline()
        if ldebug>0 : print("[" + bcolors.OK + ">>" + bcolors.RESET + "] Debut de trame détecté à " + datetime.now().strftime("%H:%M:%S.%f"))
        while True:
            line_str = line.decode("utf-8")
            ar = line_str.split("\t")

            try :
                list_measures = treatmesure(ar[0],ar[1],ar[2])
            except :
                print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "] Probleme de decodage ligne : " + line_str)

            #On détecte le caractère de fin de ligne
            if b'\x03' in line:
                treattrame(list_measures)
                ser.reset_input_buffer()    # On vide le buffer du port série pour éviter le stacking
                line = ser.readline()
                while b'\x02' not in line:  # recherche du caractère de début de la prochaine trame
                    line = ser.readline()
            line = ser.readline()

#Cas où le fichier de config serait corrompu
else :
    if ldebug>0 : print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "] Mise en écoute impossible. Mode TIC inconnu : " + modeTIC)
