#!/usr/local/env python
# -*- coding: utf-8 -*-

#This file is part of LinkyRPi.
#LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
#(c)Copyright Mikaël Masci 2022


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
