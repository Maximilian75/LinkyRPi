#!/usr/bin/env python
# -*- coding: utf-8 -*-


#This file is part of LinkyRPi.
#LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
#(c)Copyright Mikaël Masci 2022


import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
import tkinter.font as font
from time import sleep
from threading import Thread
import sys
import os
import errno
import subprocess
import configparser
import posix_ipc
import datetime
import json
from datetime import datetime

#=======================================================================================#
#=== Initialisation                                                                  ===#
#=======================================================================================#

# Pour commenser on va lire le fichier de config
config = configparser.RawConfigParser()
config.read('/home/pi/LinkyRPi/LinkyRPi.conf')

ldebug = int(config.get('PARAM','debugLevel'))

if ldebug>0 : print("=============================================================================")
if ldebug>0 : print("Démarrage du process GUI : " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))

# On se connecte à la queue POSIX via laquelle le backend envoie les trames décodées
queueName = config.get('POSIX','queueGUI')
queueDepth = int(config.get('POSIX','depthGUI'))
mq = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREAT, max_messages=queueDepth)

# Dans le cas où la variable d'environnement DISPLAY ne serait pas définie, on la définie
# Ceci afin d'indiquer sur quel écran on veut afficher la UI (0.0 étant l'écran connecté au port HDMI du Raspberry)
if os.environ.get('DISPLAY','') == '':
    if ldebug>1 : print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

# On desactive le screen saver parce que ça fait chier et que le réveil via l'écran tactile ne fonctionne pas des masses
cmd = "xset -dpms"
result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
if ldebug>1 : print(result)
cmd = "xset s off"
result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
if ldebug>1 : print(result)
