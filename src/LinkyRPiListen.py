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


print("=============================================================================")
print("Démarrage du process listenner : " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))

syllabus, dataFormat = linkyRPiTranslate.generateSyllabus()

# On ouvre le fichier de param et on recup les param
config = configparser.RawConfigParser()
config.read('/home/pi/LinkyRPi/LinkyRPi.conf')
ldebug = int(config.get('PARAM','debuglevel'))

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


#Ouverture de la pile FIFO pour communication avec la le dispatcher
queueName = config.get('POSIX','queueDispatch')
queueDepth = int(config.get('POSIX','depthDispatch'))
try:
    q1 = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREX, max_messages=queueDepth)
    if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Queue Dispatcher créée")
except :
    if ldebug>0 : print("[" + bcolors.WARNING + "WA" + bcolors.RESET + "] La queue Dispatcher existe deja")
    q1 = posix_ipc.MessageQueue(queueName)



#==============================================================================#
# Initialisation du process                                                    #
#==============================================================================#
def init():

    if ldebug>1 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] Détection du mode de fonctionnement de la TIC...")

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
            if ldebug>2 : print(line_str)
        else :
            modeTIC = "Standard"
            if ldebug>0 : print("[" + bcolors.OK + "OK" + bcolors.RESET + "] TIC en mode STANDARD")
            if ldebug>2 : print(line_str)
    else :
        if ldebug>0 : print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "] Unable to detect the baud rate")
        if ldebug>1 : print(line_str)
    ser.close()

    return modeTIC

#==============================================================================#
# Traitement de la mesure lue                                                  #
#==============================================================================#
def treatmesure(mesureCode,mesureValue,mesureValue2) :
    #Les codes ci-dessous contiennent 2 valeurs : un horodatage + la valeur en question.
    #Du coup on bypass l'horodatage pour ne garder que la valeur
    if mesureCode in ["SMAXSN","SMAXSN1","SMAXSN2","SMAXSN3","SMAXSN-1","SMAXSN1-1","SMAXSN2-1","SMAXSN3-1","SMAXIN","SMAXIN-1","CCASN","CCASN-1","CCAIN","CCAIN-1","UMOY1","UMOY2","UMOY3","DPM1","FPM1","DPM2","FPM2","DPM3","FPM3"] :
        mesure = (mesureCode, mesureValue2.strip("\n"))
        if ldebug>9 : print("[" + bcolors.OK + ">>" + bcolors.RESET + "]" , mesureCode + " : " + mesureValue2.strip("\n"))
    else :
        mesure = (mesureCode, mesureValue)
        if ldebug>9 : print("[" + bcolors.OK + ">>" + bcolors.RESET + "]" , mesureCode + " : " + mesureValue)

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
    if ldebug>1 : print("--------------------------------------------------------------------------------")

    #On traduit la trame reçue en un dictionnaire agnostique du type de fonctionnement de la TIC
    analysedDict = {}
    analysedDict = linkyRPiTranslate.analyseTrame(syllabus, dataFormat, dict(list_measures))

    #On envoie le dictionnaire traduit à la UI sous forme de Json
    trameJson = json.dumps(analysedDict, indent=4)
    q1.send(trameJson)


#==============================================================================#
# Traitement des exceptions                                                    #
#==============================================================================#
def treaterror(errEvent,errCode,errValue) :
    if ldebug>0 : print("[" + bcolors.FAIL + "KO" + bcolors.RESET + "]",errEvent,' : ' , errCode , ' = ' ,errValue)
    #Ici on va pousser l'ensemble des mesures de la trame dans le topic Kafka pour la Log



#==============================================================================#
# PRODEDURE PRINCIPALE                                                         #
#==============================================================================#
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
        if ldebug>1 : print("================================================================================")
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
        if ldebug>1 : print("================================================================================")
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
