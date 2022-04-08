#!/usr/local/env python
# -*- coding: utf-8 -*-

import posix_ipc
import time
import sys
import ast
import json
from datetime import datetime


list_measures = []

q1 = posix_ipc.MessageQueue("/LinkyRPiQueueGUI", posix_ipc.O_CREAT)

fileName = "/home/pi/LinkyRPi/log/" + sys.argv[1] + ".log"

nbLoop = int(sys.argv[2])
x = 1
oldTime = datetime.now()

while x <= nbLoop :
    print("Boucle n. " + str(x) + "/" + str(nbLoop))
    try :
        file = open(fileName, "r")

    except :
        print("File does not exists : " + fileName)


    line = file.readline()
    i = 0
    while line :
        i = i + 1
        analysedDict = ast.literal_eval(line)

        newTime = datetime.now()
        newTimeStr = newTime.strftime("%H:%M:%S.%f")
        delta = newTime - oldTime
        deltaStr = str(delta)
        print("  Envoi trame " + str(i) + " à " + newTimeStr + " (" + deltaStr + ")")
        oldTime = newTime

        trameJson = json.dumps(analysedDict, indent=4)
        q1.send(trameJson)
        line = file.readline()
        time.sleep(0.1)

    x = x + 1
    file.close()
    print("  Fin du fichier...")
