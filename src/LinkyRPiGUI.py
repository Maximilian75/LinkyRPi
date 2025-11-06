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

notebookBgColor    = config.get('GUICSS','notebookBgColor')
notebookBgLight    = config.get('GUICSS','notebookBgLight')
notebookBgMedium   = config.get('GUICSS','notebookBgMedium')
notebookSelColor   = config.get('GUICSS','notebookSelColor')
notebookUnselColor = config.get('GUICSS','notebookUnselColor')
notebookFont       = config.get('GUICSS','notebookFont')
graphBg            = config.get('GUICSS','graphBg')
textFont           = config.get('GUICSS','textFont')
textSizeBig        = config.get('GUICSS','textSizeBig')
textSizeMedium     = config.get('GUICSS','textSizeMedium')
textSizeSmall      = config.get('GUICSS','textSizeSmall')
labelBg            = config.get('GUICSS','labelBg')
labelColor         = config.get('GUICSS','labelColor')
colorPhase1        = config.get('GUICSS','phase1')
colorPhase2        = config.get('GUICSS','phase2')
colorPhase3        = config.get('GUICSS','phase3')
valueColorWar      = config.get('GUICSS','valueColorWar')
titleColor         = config.get('GUICSS','titleColor')



master = tk.Tk()
master.attributes('-alpha', 0.0)
master.iconify()
master.geometry("1024x600")
master.attributes("-fullscreen", True)
master.minsize(1024,600)
master.maxsize(1024,600)
master.configure(bg=notebookBgColor)
master.config(cursor="none")    # On désactive le curseur parcequ'on a un écran tactile :)
master.overrideredirect(1)      # On supprime le bord

#On commence par créer le style de notre UI
s = ttk.Style()
scaleDBVal = tk.DoubleVar()
scaleFileVal = tk.DoubleVar()

s.theme_create( "MyStyle", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [0, 0, 0, 0] },
                                    "tabposition": "wn",
                                    "background": notebookBgColor,
                                    "bordercolor": notebookBgColor,
                                    },
        "TNotebook.Tab": {"configure": {"padding": [5, 10],
                                        "tabposition": "wn",
                                        "background": notebookUnselColor,
                                        "foreground": notebookSelColor,
                                        "font" : (notebookFont, textSizeSmall, 'bold')},
                          "map":       {"background": [("selected", notebookSelColor)],
                                        "foreground": [("selected", notebookBgColor)],
                                        "expand": [("selected", [0, 0, 0, 0])] }
                                        }})
s.theme_use("MyStyle")


#style = ttk.Style(master)
s.configure('lefttab.TNotebook', tabposition='wn')
s.configure("TNotebook", borderwidth=0, background=notebookBgColor)
s.configure("TNotebook.Tab", borderwidth=0, background=notebookBgColor)
s.configure('My.TSpinbox', arrowsize=25)

#Puis on crée le notebook
myNotebook = ttk.Notebook(master, style='lefttab.TNotebook')
myNotebook.pack(padx=0, pady=0)

# Frame d'information
infoIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/info.png")
infoFrame = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
myNotebook.add(infoFrame, image=infoIcon)

# Frame des index et dépassements
indexIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/index.png")
indexFrame = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
myNotebook.add(indexFrame, image=indexIcon)

#Frame PRODUCTEUR
prodIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/prod.png")
productFrame = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
myNotebook.add(productFrame, image=prodIcon)

# Frame des tensions & puissances
tensionIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/tension.png")
tensionFrame = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
myNotebook.add(tensionFrame, image=tensionIcon)

# Frame(s) du graphique des intensités soutirées
intensiteIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/graph.png")
intensiteFrame  = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
intensiteFrameT = tk.Frame(intensiteFrame, width=1024, height=100, bg=notebookBgColor)
intensiteFrameB = tk.Frame(intensiteFrame, width=1024, height=500, bg=notebookBgColor)
intensiteFrameL = tk.Frame(intensiteFrameB, width=824, height=500, bg=notebookBgColor)
intensiteFrameR = tk.Frame(intensiteFrameB, width=200, height=500, bg=notebookBgColor)
intensiteFrameT.pack(side="top", fill="both", expand=False)
intensiteFrameB.pack(side="bottom", fill="both", expand=False)
intensiteFrameL.pack(side="left", fill="both", expand=False)
intensiteFrameR.pack(side="right", fill="both", expand=False)
myNotebook.add(intensiteFrame, image=intensiteIcon)
canvas= tk.Canvas(intensiteFrameL, width=824, height=600, bg=graphBg, bd=0, highlightthickness=0)
canvas.pack(expand=tk.YES, fill=tk.BOTH)

# Frame du registre
registreIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/registre.png")
registreFrame = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
myNotebook.add(registreFrame, image=registreIcon)

# Frame des statuts
statusIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/status.png")
statusFrame  = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
myNotebook.add(statusFrame, image=statusIcon)

# Frame du registre
paramIcon  = tk.PhotoImage(file=config.get('PATH','iconPath') + "/param.png")
paramFrame = tk.Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
paramFrameT = tk.Frame(paramFrame, width=1024, height=500, bg=notebookBgColor)
paramFrameB = tk.Frame(paramFrame, width=1024, height=100, bg=notebookBgColor)
paramFrameT.pack(side="top", fill="both", expand=False)
paramFrameB.pack(side="bottom", fill="both", expand=False)
myNotebook.add(paramFrame, image=paramIcon)


signalIcon      = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi0.png")


#On instancie le notebook
myNotebook.pack()




#===============================================================================
#=== Bouton REBOOT                                                           ===
#===============================================================================
def reboot():
    modalConfirm = askyesno(title='Confirmation',
                    message='Are you sure that you want to REBOOT ?')
    if modalConfirm:
        os.system('sudo reboot')

#===============================================================================
#=== Bouton CMD                                                              ===
#===============================================================================
def cmd():
    root = tk.Tk()
    termf = tk.Frame(root, height=1024, width=600)

    termf.pack(fill=tk.BOTH, expand=tk.YES)
    wid = termf.winfo_id()
    os.system('xterm -into %d -geometry 1024x600 -sb &' % wid)

#===============================================================================
#=== Boutons SCALE                                                           ===
#===============================================================================
def changeXScale():
    global xscale, v
    xscale = v.get()
    return xscale

#===============================================================================
#=== Boutons Switch DB Active                                                ===
#===============================================================================
def switchDB():
    flagDBActive    = config.get('POSTGRESQL','active')

    if flagDBActive == "True" :
        config.set('POSTGRESQL', 'active', 'False')
        ButtonDBActive.config(image=OFFButton, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    else :
        config.set('POSTGRESQL', 'active', 'True')
        ButtonDBActive.config(image=ONButton, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)

    flagDBActive    = config.get('POSTGRESQL','active')


#===============================================================================
#=== Scale DB                                                                ===
#===============================================================================
def timerUpDB():
    refreshDB = int(config.get('POSTGRESQL','refreshDB'))
    if refreshDB < 600 :
        refreshDB = refreshDB + 1
        config.set('POSTGRESQL', 'refreshDB', str(refreshDB))
        timerDB.set(str(refreshDB) + " s")

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)


def timerDownDB():
    refreshDB = int(config.get('POSTGRESQL','refreshDB'))
    if refreshDB > 1 :
        refreshDB = refreshDB - 1
        config.set('POSTGRESQL', 'refreshDB', str(refreshDB))
        timerDB.set(str(refreshDB) + " s")

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)


#===============================================================================
#=== Boutons Switch MQ Active                                                ===
#===============================================================================
def switchMQ():
    flagMQActive    = config.get('MQTT','MQTTactive')

    if flagMQActive == "True" :
        config.set('MQTT', 'MQTTactive', 'False')
        ButtonMQActive.config(image=OFFButton, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    else :
        config.set('MQTT', 'MQTTactive', 'True')
        ButtonMQActive.config(image=ONButton, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)

    flagMQActive    = config.get('MQTT','MQTTactive')


#===============================================================================
#=== Scale MQTT                                                              ===
#===============================================================================
def timerUpMQ():
    refreshMQ = int(config.get('MQTT','refreshMQTT'))
    if refreshMQ < 600 :
        refreshMQ = refreshMQ + 1
        config.set('MQTT', 'refreshMQTT', str(refreshMQ))
        timerMQTT.set(str(refreshMQ) + " s")

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)


def timerDownMQ():
    refreshMQ = int(config.get('MQTT','refreshMQTT'))
    if refreshMQ > 1 :
        refreshMQ = refreshMQ - 1
        config.set('MQTT', 'refreshMQTT', str(refreshMQ))
        timerMQTT.set(str(refreshMQ) + " s")

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)


#===============================================================================
#=== Boutons Switch FILE Active                                              ===
#===============================================================================
def switchFile():
    flagFileActive    = config.get('PARAM','traceActive')

    if flagFileActive == "True" :
        config.set('PARAM', 'traceActive', 'False')
        ButtonFileActive.config(image=OFFButton, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    else :
        config.set('PARAM', 'traceActive', 'True')
        ButtonFileActive.config(image=ONButton, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)

    flagFileActive    = config.get('PARAM','traceActive')

#===============================================================================
#=== Scale File                                                              ===
#===============================================================================
def timerUpFile():
    refreshFile = int(config.get('PARAM','traceFreq'))
    if refreshFile < 600 :
        refreshFile = refreshFile + 1
        config.set('PARAM', 'traceFreq', str(refreshFile))
        timerFile.set(str(refreshFile) + " s")

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)


def timerDownFile():
    refreshFile = int(config.get('PARAM','traceFreq'))
    if refreshFile > 1 :
        refreshFile = refreshFile - 1
        config.set('PARAM', 'traceFreq', str(refreshFile))
        timerFile.set(str(refreshFile) + " s")

    with open(r'LinkyRPi.conf', 'w') as configfile :
        config.write(configfile)


#=======================================================================================#
#=== Initialisation de la UI en fonction de divers paramètres reçus                  ===#
#=======================================================================================#
def initGUI(analysedDict) :

    if ldebug>0 : print("Initialisation de la GUI...")

    #Definition des voyants et boutons
    if ldebug>1 : print(" - Chargement des icones")
    global voyantNoir, voyantBleu, voyantBlanc, voyantRouge, voyantHC, voyantHP, voyantWE, miniVoyantNoir, miniVoyantVert
    global signalIcon, cmdIcon, rebootIcon, ONButton, OFFButton, flecheD, flecheG, boutonFonce, boutonClair
    voyantNoir      = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/NOIR.png")
    voyantBleu      = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/BLEU.png")
    voyantBlanc     = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/BLANC.png")
    voyantRouge     = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/ROUGE.png")
    voyantVert      = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/VERT.png")
    miniVoyantNoir  = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/miniNOIR.png")
    miniVoyantVert  = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/miniVERT.png")
    voyantHC        = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/HC.png")
    voyantHP        = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/HP.png")
    voyantWE        = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/WE.png")
    boutonClair     = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/boutonClair.png")
    boutonFonce     = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/boutonFonce.png")



    #On définit les caractéristiques de la GUI
    if ldebug>1 : print(" - Chargement de la configuration")
    notebookBgColor  = config.get('GUICSS','notebookBgColor')
    notebookBgLight  = config.get('GUICSS','notebookBgLight')
    notebookBgMedium = config.get('GUICSS','notebookBgMedium')
    graphBg          = config.get('GUICSS','graphBg')
    textFont         = config.get('GUICSS','textFont')
    textSizeBig      = config.get('GUICSS','textSizeBig')
    textSizeMedium   = config.get('GUICSS','textSizeMedium')
    textSizeSmall    = config.get('GUICSS','textSizeSmall')
    labelBg          = config.get('GUICSS','labelBg')
    labelColor       = config.get('GUICSS','labelColor')
    colorPhase1      = config.get('GUICSS','phase1')
    colorPhase2      = config.get('GUICSS','phase2')
    colorPhase3      = config.get('GUICSS','phase3')
    valueColorWar    = config.get('GUICSS','valueColorWar')
    titleColor       = config.get('GUICSS','titleColor')

    # Frame producteur (seulement en mode PRODUCTEUR)
    if "Fonctionnement" in analysedDict :
        if analysedDict["Fonctionnement"] != "Producteur" :
            if ldebug>2 : print("   - Frame 'Producteur' instanciée")
            productFrame.destroy()
    else :
        productFrame.destroy()
        if ldebug>2 : print("   - Pas de frame 'Producteur'")


    # Frame du REGISTRE (uniquement si la TIC est en mode STANDARD)
    if analysedDict["ModeTIC"] == "Historique" :
        registreFrame.destroy()
        if ldebug>2 : print(" - TIC en mode 'Historique'")



    #===============================================================================
    #=== Population de la frame INFORMATIONS                                     ===
    #===============================================================================
    if ldebug>2 : print("   - Instantiation de la frame 'Informations'")
    INFOTITLE = tk.StringVar()
    INFOTITLE.set("Informations compteur & abonnement")
    infoTitle = tk.Label(infoFrame, textvariable = INFOTITLE, font=(textFont,textSizeBig), bg=labelBg, fg=titleColor, relief=tk.GROOVE)
    infoTitle.grid(row=0, column=0, columnspan = 6, padx=15, ipadx=15, ipady=15)

    if "PRM" in analysedDict :
        FieldPRM = tk.StringVar()
        FieldPRM.set(analysedDict["PRM"])
        LabelPRM = tk.Label(infoFrame, text="Point de livraison (PRM) :", font=(textFont,textSizeBig,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelPRM.grid(row=1, column=0, sticky=tk.E, padx=10, pady=(20,10))
        valuePRM = tk.Label(infoFrame, textvariable = FieldPRM, font=(textFont,textSizeBig), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePRM.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=10, pady=(20,10))

    FieldAddresseCompteur = tk.StringVar()
    FieldAddresseCompteur.set(analysedDict["AdresseCompteur"])
    LabelAddresseCompteur = tk.Label(infoFrame, text="Adresse du compteur :", font=(textFont,textSizeBig,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelAddresseCompteur.grid(row=2, column=0, sticky=tk.E, padx=10, pady=(15,10))
    valueAddresseCompteur = tk.Label(infoFrame, textvariable = FieldAddresseCompteur, font=(textFont,textSizeBig), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueAddresseCompteur.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=10, pady=(15,10))

    FieldNomCompteur = tk.StringVar()
    FieldNomCompteur.set(analysedDict["NomCompteur"])
    LabelNomCompteur = tk.Label(infoFrame, text="Modèle de compteur :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelNomCompteur.grid(row=3, column=0, sticky=tk.E, padx=10, pady=(30,10))
    valueNomCompteur = tk.Label(infoFrame, textvariable = FieldNomCompteur, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueNomCompteur.grid(row=3, column=1, columnspan=5, sticky=tk.W, padx=10, pady=(30,10))

    FieldIntensiteSouscrite = tk.StringVar()
    FieldPuissanceSouscrite = tk.StringVar()
    if analysedDict["TypeCompteur"] == "MONO" :
        FieldIntensiteSouscrite.set(str(analysedDict["IntensiteSouscrite"]) + " kVA")
        FieldPuissanceSouscrite.set("(" + str(analysedDict["IntensiteSouscrite"] * 5) + " A)")
    else :
        FieldIntensiteSouscrite.set(str(analysedDict["IntensiteSouscrite"]) + " kVA")
        FieldPuissanceSouscrite.set("(" + str(analysedDict["IntensiteSouscrite"] * 5 / 3) + " A)")
    LabelIntensiteSouscrite = tk.Label(infoFrame, text="Abonnement :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelIntensiteSouscrite.grid(row=4, column=0, sticky=tk.E, padx=10, pady=(30,10))
    valueIntensiteSouscrite = tk.Label(infoFrame, textvariable = FieldIntensiteSouscrite, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueIntensiteSouscrite.grid(row=4, column=1, sticky=tk.W, padx=(10,2), pady=(30,10))
    valuePuissanceSouscrite = tk.Label(infoFrame, textvariable = FieldPuissanceSouscrite, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valuePuissanceSouscrite.grid(row=4, column=2, sticky=tk.W, padx=1, pady=(30,10))

    if "PuissanceCoupure" in analysedDict :
        FieldPuissanceCoupure = tk.StringVar()
        FieldPuissanceCoupure.set(str(analysedDict["PuissanceCoupure"]) + " kVA")
        LabelPuissanceCoupure = tk.Label(infoFrame, text="Puissance de coupure :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelPuissanceCoupure.grid(row=5, column=0, sticky=tk.E, padx=10, pady=10)
        valuePuissanceCoupure = tk.Label(infoFrame, textvariable = FieldPuissanceCoupure, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceCoupure.grid(row=5, column=1, sticky=tk.W, padx=10, pady=10)


    FieldTarifSouscrit = tk.StringVar()
    FieldTarifSouscrit.set(analysedDict["TarifSouscrit"])
    LabelTarifSouscrit = tk.Label(infoFrame, text="Option tarifaire :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelTarifSouscrit.grid(row=6, column=0, sticky=tk.E, padx=10, pady=(30,10))
    valueTarifSouscrit = tk.Label(infoFrame, textvariable = FieldTarifSouscrit, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueTarifSouscrit.grid(row=6, column=1, columnspan=3, sticky=tk.W, padx=10, pady=(30,10))

    global HPHCIcon
    global JOURIcon
    global DEMAINIcon
    if (analysedDict["TarifSouscrit"] == "Heures Creuses") or (analysedDict["TarifSouscrit"] == "Heures Creuses et Week-end") :
        FieldHorairesHC = tk.StringVar()
        FieldHorairesHC.set("(" + analysedDict["HorairesHC"] + ")")
        valueHorairesHC = tk.Label(infoFrame, textvariable = FieldHorairesHC, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHorairesHC.grid(row=6, column=3, columnspan=2, sticky=tk.W, padx=10, pady=(30,10))
        LabelEnCours = tk.Label(infoFrame, text="En cours :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelEnCours.grid(row=7, column=0, sticky=tk.E, padx=10, pady=30)
        HPHCIcon = tk.Label(infoFrame, image=voyantNoir, borderwidth=0)
        HPHCIcon.grid(row=7, column=1, padx=2, pady=2)

    elif analysedDict["TarifSouscrit"] == "TEMPO" :
        FieldHorairesHC = tk.StringVar()
        FieldHorairesHC.set("(" + analysedDict["HorairesHC"] + ")")
        valueHorairesHC = tk.Label(infoFrame, textvariable = FieldHorairesHC, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHorairesHC.grid(row=6, column=2, columnspan=2, sticky=tk.W, padx=10, pady=(30,10))
        LabelEnCours = tk.Label(infoFrame, text="En cours :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelEnCours.grid(row=7, column=0, sticky=tk.E, padx=10, pady=10)
        HPHCIcon = tk.Label(infoFrame, image=voyantNoir, borderwidth=0)
        HPHCIcon.grid(row=7, column=1, padx=2, pady=2)
        JOURIcon = tk.Label(infoFrame, image=voyantNoir, borderwidth=0)
        JOURIcon.grid(row=7, column=2, sticky=tk.W, padx=2, pady=2)
        LabelDEMAIN = tk.Label(infoFrame, text="Demain :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelDEMAIN.grid(row=7, column=3, sticky=tk.W, padx=10, pady=30)
        DEMAINIcon = tk.Label(infoFrame, image=voyantNoir, borderwidth=0)
        DEMAINIcon.grid(row=7, column=4, sticky=tk.W, padx=2, pady=2)

    elif analysedDict["TarifSouscrit"] == "EJP" :
        FieldHorairesHC = tk.StringVar()
        FieldHorairesHC.set("(" + analysedDict["HorairesHC"] + ")")
        valueHorairesHC = tk.Label(infoFrame, textvariable = FieldHorairesHC, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHorairesHC.grid(row=6, column=3, columnspan=2, sticky=tk.W, padx=10, pady=(30,10))
        LabelEnCours = tk.Label(infoFrame, text="En cours :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelEnCours.grid(row=4, column=0, sticky=tk.E, padx=10, pady=10)
        HPHCIcon = tk.Label(infoFrame, image=voyantNoir, borderwidth=0)
        HPHCIcon.grid(row=7, column=1, padx=2, pady=2)
        JOURIcon = tk.Label(infoFrame, image=voyantNoir, borderwidth=0)
        JOURIcon.grid(row=7, column=2, sticky=tk.W, padx=2, pady=2)
        LabelDEMAIN = tk.Label(infoFrame, text="Demain :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelDEMAIN.grid(row=7, column=3, sticky=tk.W, padx=10, pady=30)
        DEMAINIcon = tk.Label(infoFrame, image=voyantNoir, borderwidth=0)
        DEMAINIcon.grid(row=7, column=4, sticky=tk.W, padx=2, pady=2)

    global DATE
    if "DateHeureLinky" in analysedDict :
        DATE = tk.StringVar()
        DATE.set(analysedDict["DateHeureLinky"])
        valueDATE = tk.Label(infoFrame, textvariable = DATE, font=(textFont,textSizeBig), bg=labelBg, fg=valueColorWar)
        valueDATE.grid(row=8, column=0, columnspan = 6, padx=15, ipadx=15, ipady=15)





    #===============================================================================
    #=== Population de la frame INDEX                                            ===
    #===============================================================================
    if ldebug>2 : print("   - Instantiation de la frame 'Index'")
    global BASE, HCHC, HCHP, HWE, EJPHN, EJPHPM
    global BBRHCJB, BBRHPJB, BBRHCJW, BBRHPJW, BBRHCJR, BBRHPJR
    global IndexTotal, IndexHPH, IndexHPB, IndexHCH, IndexHCB

    INDEXTITLE = tk.StringVar()
    INDEXTITLE.set("Index de consommation")
    indexTitle = tk.Label(indexFrame, textvariable = INDEXTITLE, font=(textFont,textSizeBig), bg=labelBg, fg=titleColor, relief=tk.GROOVE)
    indexTitle.grid(row=0, column=0, columnspan = 6, padx=15, ipadx=15, ipady=15)

    if (analysedDict["TarifSouscrit"] == "Tarif de base") :
        BASE = tk.StringVar()
        valueIndex = int(analysedDict["IndexBase"]) / 1000
        BASE.set("{:,}".format(valueIndex))
        LabelBASE = tk.Label(indexFrame, text="Index option Base :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelBASE.grid(row=1, column=0, sticky=tk.E, padx=10, pady=(30,10))
        valueBASE = tk.Label(indexFrame, textvariable = BASE, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueBASE.grid(row=1, column=1, sticky=tk.E, padx=10, pady=(30,10))
        unitBASE = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitBASE.grid(row=1, column=2, sticky=tk.E, padx=10, pady=(30,10))

    elif (analysedDict["TarifSouscrit"] == "Heures Creuses") :
        voyantIndexHP = tk.Label(indexFrame, image=voyantHP, borderwidth=0)
        voyantIndexHP.grid(row=1, column=1, columnspan=2, padx=2, pady=(15,5))
        voyantIndexHC = tk.Label(indexFrame, image=voyantHC, borderwidth=0)
        voyantIndexHC.grid(row=1, column=3, columnspan=2, padx=2, pady=(15,5))

        LabelConsoHP = tk.Label(indexFrame, text="Heures Pleines", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHP.grid(row=2, column=1, columnspan = 2, padx=10, pady=(20,10))
        LabelConsoHC = tk.Label(indexFrame, text="Heures Creuses", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHC.grid(row=2, column=3, columnspan = 2, padx=10, pady=(20,10))

        LabelConsoHPH = tk.Label(indexFrame, text="Saison Haute", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHPH.grid(row=3, column=1, padx=10, pady=(20,10))
        LabelConsoHPB = tk.Label(indexFrame, text="Saison Basse", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHPB.grid(row=3, column=2, padx=10, pady=(20,10))
        LabelConsoHCH = tk.Label(indexFrame, text="Saison Haute", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHCH.grid(row=3, column=3, padx=10, pady=(20,10))
        LabelConsoHCB = tk.Label(indexFrame, text="Saison Basse", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHCB.grid(row=3, column=4, padx=10, pady=(20,10))

        LabelIndexS = tk.Label(indexFrame, text="Index saisons :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelIndexS.grid(row=4, column=0, sticky=tk.E, padx=10, pady=10)

        IndexHPH = tk.StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex4"]) / 1000
        IndexHPH.set("{:,}".format(valueIndex))
        valueHPH = tk.Label(indexFrame, textvariable = IndexHPH, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHPH.grid(row=4, column=1, padx=10, pady=10)

        IndexHPB = tk.StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex2"]) / 1000
        IndexHPB.set("{:,}".format(valueIndex))
        valueHPB = tk.Label(indexFrame, textvariable = IndexHPB, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHPB.grid(row=4, column=2, padx=10, pady=10)

        IndexHCH = tk.StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex3"]) / 1000
        IndexHCH.set("{:,}".format(valueIndex))
        valueHCH = tk.Label(indexFrame, textvariable = IndexHCH, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHCH.grid(row=4, column=3, padx=10, pady=10)

        IndexHCB = tk.StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex1"]) / 1000
        IndexHCB.set("{:,}".format(valueIndex))
        valueHCB = tk.Label(indexFrame, textvariable = IndexHCB, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHCB.grid(row=4, column=4, padx=10, pady=10)

        unitIndexS = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitIndexS.grid(row=4, column=5, sticky=tk.W, padx=10, pady=10)

        LabelIndex = tk.Label(indexFrame, text="Index HP/HC :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelIndex.grid(row=5, column=0, sticky=tk.E, padx=10, pady=10)

        HCHP = tk.StringVar()
        valueIndex = int(analysedDict["IndexHP"]) / 1000
        HCHP.set("{:,}".format(valueIndex))
        valueHCHP = tk.Label(indexFrame, textvariable = HCHP, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHCHP.grid(row=5, column=1, columnspan = 2, padx=10, pady=10)

        HCHC = tk.StringVar()
        valueIndex = int(analysedDict["IndexHP"]) / 1000
        HCHC.set("{:,}".format(valueIndex))
        valueHCHC = tk.Label(indexFrame, textvariable = HCHC, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHCHC.grid(row=5, column=3, columnspan = 2, padx=10, pady=10)

        unitIndex = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitIndex.grid(row=5, column=5, sticky=tk.W, padx=10, pady=10)

        IndexTotal = tk.StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        LabelTOTAL = tk.Label(indexFrame, text="Index total :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTOTAL.grid(row=6, column=0, sticky=tk.E, padx=10, pady=(15,30))
        valueTOTAL = tk.Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=6, column=1, columnspan = 4, padx=10, pady=(15,30))
        unitTOTAL = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=6, column=5, sticky=tk.W, padx=10, pady=(15,30))


    elif (analysedDict["TarifSouscrit"] == "Heures Creuses et Week-end") :
        voyantIndexHP = tk.Label(indexFrame, image=voyantHP, borderwidth=0)
        voyantIndexHP.grid(row=1, column=1, columnspan=1, padx=2, pady=(15,5))
        voyantIndexHC = tk.Label(indexFrame, image=voyantHC, borderwidth=0)
        voyantIndexHC.grid(row=1, column=2, columnspan=1, padx=2, pady=(15,5))
        voyantIndexWE = tk.Label(indexFrame, image=voyantWE, borderwidth=0)
        voyantIndexWE.grid(row=1, column=3, columnspan=1, padx=2, pady=(15,5))

        HCHC = tk.StringVar()
        valueIndex = int(analysedDict["IndexHC"]) / 1000
        HCHC.set("{:,}".format(valueIndex))
        HCHP = tk.StringVar()
        valueIndex = int(analysedDict["IndexHP"]) / 1000
        HCHP.set("{:,}".format(valueIndex))
        HWE = tk.StringVar()
        valueIndex = int(analysedDict["IndexWE"]) / 1000
        HWE.set("{:,}".format(valueIndex))
        LabelConsoHP = tk.Label(indexFrame, text="Heures P", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHP.grid(row=2, column=1, padx=10, pady=(20,10))
        LabelConsoHC = tk.Label(indexFrame, text="Heures C", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHC.grid(row=2, column=2, padx=10, pady=(20,10))
        LabelConsoWE = tk.Label(indexFrame, text="Heures WE", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoWE.grid(row=2, column=3, padx=10, pady=(20,10))
        LabelIndex = tk.Label(indexFrame, text="Index HP/HC/WE :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelIndex.grid(row=3, column=0, sticky=tk.E, padx=10, pady=10)
        valueHCHP = tk.Label(indexFrame, textvariable = HCHP, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHCHP.grid(row=3, column=1, sticky=tk.E, padx=10, pady=10)
        valueHCHC = tk.Label(indexFrame, textvariable = HCHC, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHCHC.grid(row=3, column=2, sticky=tk.E, padx=10, pady=10)
        valueWEND = tk.Label(indexFrame, textvariable = HWE, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueWEND.grid(row=3, column=3, sticky=tk.E, padx=10, pady=10)
        unitIndex = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitIndex.grid(row=3, column=4, sticky=tk.E, padx=10, pady=10)

        IndexTotal = tk.StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        LabelTOTAL = tk.Label(indexFrame, text="Index total :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTOTAL.grid(row=5, column=0, sticky=tk.E, padx=10, pady=(15,30))
        valueTOTAL = tk.Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=5, column=1, columnspan = 3, padx=10, pady=(15,30))
        unitTOTAL = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=5, column=4, sticky=tk.E, padx=10, pady=(15,30))


    elif (analysedDict["TarifSouscrit"] == "EJP") :
        EJPHN = tk.StringVar()
        valueIndex = int(analysedDict["IndexEJPNormale"]) / 1000
        EJPHN.set("{:,}".format(valueIndex))
        EJPHPM = tk.StringVar()
        valueIndex = int(analysedDict["IndexEJPPointe"]) / 1000
        EJPHN.set("{:,}".format(valueIndex))
        LabelConsoEN = tk.Label(indexFrame, text="Heures Normales", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoEN.grid(row=1, column=1, sticky=tk.E, padx=30, pady=(20,10))
        LabelConsoEP = tk.Label(indexFrame, text="Heures de Pointe", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoEP.grid(row=1, column=2, sticky=tk.E, padx=30, pady=(20,10))
        LabelIndex = tk.Label(indexFrame, text="Index EJP :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelIndex.grid(row=2, column=0, sticky=tk.E, padx=30, pady=10)
        valueEJPHN = tk.Label(indexFrame, textvariable = EJPHN, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueEJPHN.grid(row=2, column=1, sticky=tk.E, padx=30, pady=10)
        valueEJPHPM = tk.Label(indexFrame, textvariable = EJPHPM, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueEJPHPM.grid(row=2, column=2, sticky=tk.E, padx=30, pady=10)
        unitIndex = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitIndex.grid(row=2, column=3, sticky=tk.E, padx=30, pady=10)

        IndexTotal = tk.StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        LabelTOTAL = tk.Label(indexFrame, text="Index total :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTOTAL.grid(row=3, column=0, sticky=tk.E, padx=30, pady=(15,30))
        valueTOTAL = tk.Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=3, column=1, columnspan = 2, padx=30, pady=(15,30))
        unitTOTAL = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=3, column=4, sticky=tk.E, padx=30, pady=(15,30))

    elif (analysedDict["TarifSouscrit"] == "TEMPO") :
        BBRHCJB = tk.StringVar()
        valueIndex = int(analysedDict["IndexHCJB"]) / 1000
        BBRHCJB.set("{:,}".format(valueIndex))
        BBRHPJB = tk.StringVar()
        valueIndex = int(analysedDict["IndexHPJB"]) / 1000
        BBRHPJB.set("{:,}".format(valueIndex))
        BBRHCJW = tk.StringVar()
        valueIndex = int(analysedDict["IndexHCJW"]) / 1000
        BBRHCJW.set("{:,}".format(valueIndex))
        BBRHPJW = tk.StringVar()
        valueIndex = int(analysedDict["IndexHPJW"]) / 1000
        BBRHPJW.set("{:,}".format(valueIndex))
        BBRHCJR = tk.StringVar()
        valueIndex = int(analysedDict["IndexHCJR"]) / 1000
        BBRHCJR.set("{:,}".format(valueIndex))
        BBRHPJR = tk.StringVar()
        valueIndex = int(analysedDict["IndexHPJR"]) / 1000
        BBRHPJR.set("{:,}".format(valueIndex))

        LabelConsoHP = tk.Label(indexFrame, text="Heures Pleines", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHP.grid(row=1, column=1, sticky=tk.E, padx=30, pady=(20,10))
        LabelConsoHC = tk.Label(indexFrame, text="Heures Creuses", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelConsoHC.grid(row=1, column=2, sticky=tk.E, padx=30, pady=(20,10))
        LabelIndexB = tk.Label(indexFrame, text="Index Bleu :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelIndexB.grid(row=2, column=0, sticky=tk.E, padx=30, pady=10)
        valueBBRHPJB = tk.Label(indexFrame, textvariable = BBRHPJB, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueBBRHPJB.grid(row=2, column=1, sticky=tk.E, padx=30, pady=10)
        valueBBRHCJB = tk.Label(indexFrame, textvariable = BBRHCJB, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueBBRHCJB.grid(row=2, column=2, sticky=tk.E, padx=30, pady=10)
        unitIndexB = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitIndexB.grid(row=2, column=3, sticky=tk.E, padx=30, pady=10)
        LabelIndexW = tk.Label(indexFrame, text="Index Blanc :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelIndexW.grid(row=3, column=0, sticky=tk.E, padx=30, pady=10)
        valueBBRHPJW = tk.Label(indexFrame, textvariable = BBRHPJW, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueBBRHPJW.grid(row=3, column=1, sticky=tk.E, padx=30, pady=10)
        valueBBRHCJW = tk.Label(indexFrame, textvariable = BBRHCJW, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueBBRHCJW.grid(row=3, column=2, sticky=tk.E, padx=30, pady=10)
        unitIndexW = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitIndexW.grid(row=3, column=3, sticky=tk.E, padx=30, pady=10)
        LabelIndexR = tk.Label(indexFrame, text="Index Rouge :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelIndexR.grid(row=4, column=0, sticky=tk.E, padx=30, pady=10)
        valueBBRHPJR = tk.Label(indexFrame, textvariable = BBRHPJR, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueBBRHPJR.grid(row=4, column=1, sticky=tk.E, padx=30, pady=10)
        valueBBRHCJR = tk.Label(indexFrame, textvariable = BBRHCJR, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueBBRHCJR.grid(row=4, column=2, sticky=tk.E, padx=30, pady=10)
        unitIndexR = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitIndexR.grid(row=4, column=3, sticky=tk.E, padx=30, pady=10)

        IndexTotal = tk.StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        LabelTOTAL = tk.Label(indexFrame, text="Index total :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTOTAL.grid(row=5, column=0, sticky=tk.E, padx=30, pady=(15,30))
        valueTOTAL = tk.Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=5, column=1, columnspan = 2, padx=30, pady=(15,30))
        unitTOTAL = tk.Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=5, column=4, sticky=tk.E, padx=30, pady=(15,30))

    if analysedDict["ModeTIC"] == "Historique" :
        if analysedDict["TypeCompteur"] == "MONO" :
            global DepassementPuissance
            DepassementPuissance = tk.StringVar()
            LabelDepassementPuissance = tk.Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelDepassementPuissance.grid(row=6, column=0, columnspan = 3, sticky=tk.E, padx=30, pady=(45,10))
            valueDepassementPuissance = tk.Label(indexFrame, textvariable = DepassementPuissance, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissance.grid(row=6, column=3, sticky=tk.W, padx=30, pady=(45,10))
        else :
            global DepassementPuissancePhase1
            DepassementPuissancePhase1 = tk.StringVar()
            LabelDepassementPuissanceP1 = tk.Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite - Phase 1 :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelDepassementPuissanceP1.grid(row=6, column=0, columnspan = 3, sticky=tk.E, padx=30, pady=(45,10))
            valueDepassementPuissanceP1 = tk.Label(indexFrame, textvariable = DepassementPuissanceP1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissanceP1.grid(row=6, column=3, sticky=tk.W, padx=30, pady=(45,10))

            global DepassementPuissancePhase2
            DepassementPuissancePhase2 = tk.StringVar()
            LabelDepassementPuissanceP2 = tk.Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite - Phase 2 :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelDepassementPuissanceP2.grid(row=7, column=0, columnspan = 3, sticky=tk.E, padx=30, pady=(15,10))
            valueDepassementPuissanceP2 = tk.Label(indexFrame, textvariable = DepassementPuissanceP2, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissanceP2.grid(row=7, column=3, sticky=tk.W, padx=30, pady=(45,10))

            global DepassementPuissancePhase3
            DepassementPuissancePhase3 = tk.StringVar()
            LabelDepassementPuissanceP3 = tk.Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite - Phase 3 :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelDepassementPuissanceP3.grid(row=8, column=0, columnspan = 3, sticky=tk.E, padx=30, pady=(15,10))
            valueDepassementPuissanceP3 = tk.Label(indexFrame, textvariable = DepassementPuissanceP3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissanceP3.grid(row=8, column=3, sticky=tk.W, padx=30, pady=(45,10))



    #===============================================================================
    #=== Population de la frame TENSIONS & PUISSANCES                            ===
    #===============================================================================
    if ldebug>2 : print("   - Instanciation de la frame 'Tensions et puissances'")
    global PresenceDesPotentiels, PuissanceApparente, PuissanceApparentePhase1, PuissanceApparentePhase2, PuissanceApparentePhase3
    global PuissanceMaxAtteinte, PuissanceMaxAtteintePhase1, PuissanceMaxAtteintePhase2, PuissanceMaxAtteintePhase3
    global PuissanceApparenteMaxN1, PuissanceApparenteMaxN1Phase1, PuissanceApparenteMaxN1Phase2, PuissanceApparenteMaxN1Phase3
    global TensionEfficacePhase1, TensionEfficacePhase2, TensionEfficacePhase3, TensionMoyennePhase1, TensionMoyennePhase2, TensionMoyennePhase3

    PresenceDesPotentiels         = tk.StringVar()
    PuissanceApparente            = tk.StringVar()
    PuissanceApparentePhase1      = tk.StringVar()
    PuissanceApparentePhase2      = tk.StringVar()
    PuissanceApparentePhase3      = tk.StringVar()
    PuissanceMaxAtteinte          = tk.StringVar()
    PuissanceMaxAtteintePhase1    = tk.StringVar()
    PuissanceMaxAtteintePhase2    = tk.StringVar()
    PuissanceMaxAtteintePhase3    = tk.StringVar()
    PuissanceApparenteMaxN1       = tk.StringVar()
    PuissanceApparenteMaxN1Phase1 = tk.StringVar()
    PuissanceApparenteMaxN1Phase2 = tk.StringVar()
    PuissanceApparenteMaxN1Phase3 = tk.StringVar()
    TensionEfficacePhase1         = tk.StringVar()
    TensionEfficacePhase2         = tk.StringVar()
    TensionEfficacePhase3         = tk.StringVar()
    TensionMoyennePhase1          = tk.StringVar()
    TensionMoyennePhase2          = tk.StringVar()
    TensionMoyennePhase3          = tk.StringVar()

    TENSIONTITLE = tk.StringVar()
    TENSIONTITLE.set("Tensions & Puissances")
    tensionTitle = tk.Label(tensionFrame, textvariable = TENSIONTITLE, font=(textFont,textSizeBig), bg=labelBg, fg=titleColor, relief=tk.GROOVE)
    tensionTitle.grid(row=0, column=0, columnspan = 6, padx=15, ipadx=15, ipady=15)


    if analysedDict["TypeCompteur"] == "MONO" :
        if "TensionEfficacePhase1" in analysedDict :
            LabelTensionEfficacePhase1 = tk.Label(tensionFrame, text="Tension efficace :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelTensionEfficacePhase1.grid(row=1, column=0, sticky=tk.E, padx=30, pady=(30,10))
            valueTensionEfficacePhase1 = tk.Label(tensionFrame, textvariable = TensionEfficacePhase1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valueTensionEfficacePhase1.grid(row=1, column=1, sticky=tk.E, padx=30, pady=(30,10))
            unitTensionEfficacePhase1 = tk.Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            unitTensionEfficacePhase1.grid(row=1, column=2, sticky=tk.W, padx=30, pady=(30,10))

        if "TensionMoyennePhase1" in analysedDict :
            LabelTensionMoyennePhase1 = tk.Label(tensionFrame, text="Tension moyenne :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelTensionMoyennePhase1.grid(row=2, column=0, sticky=tk.E, padx=30, pady=10)
            valueTensionMoyennePhase1 = tk.Label(tensionFrame, textvariable = TensionMoyennePhase1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valueTensionMoyennePhase1.grid(row=2, column=1, sticky=tk.E, padx=30, pady=10)
            unitTensionMoyennePhase1 = tk.Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            unitTensionMoyennePhase1.grid(row=2, column=2, sticky=tk.W, padx=30, pady=10)

        if "PuissanceApparente" in analysedDict :
            LabelPuissanceApparente = tk.Label(tensionFrame, text="Puissance apprente :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelPuissanceApparente.grid(row=3, column=0, sticky=tk.E, padx=30, pady=(55,10))
            valuePuissanceApparente = tk.Label(tensionFrame, textvariable = PuissanceApparente, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valuePuissanceApparente.grid(row=3, column=1, sticky=tk.E, padx=30, pady=(55,10))
            unitPuissanceApparente = tk.Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            unitPuissanceApparente.grid(row=3, column=2, sticky=tk.W, padx=30, pady=(55,10))

        if "PuissanceMaxAtteinte" in analysedDict :
            LabelPuissanceMaxAtteinte = tk.Label(tensionFrame, text="Puissance maximale atteinte :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelPuissanceMaxAtteinte.grid(row=4, column=0, sticky=tk.E, padx=30, pady=10)
            valuePuissanceMaxAtteinte = tk.Label(tensionFrame, textvariable = PuissanceMaxAtteinte, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valuePuissanceMaxAtteinte.grid(row=4, column=1, sticky=tk.E, padx=30, pady=10)
            unitPuissanceMaxAtteinte= tk.Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            unitPuissanceMaxAtteinte.grid(row=4, column=2, sticky=tk.W, padx=30, pady=10)

        if "PuissanceApparenteMaxN-1" in analysedDict :
            LabelPuissanceApparenteMaxN1 = tk.Label(tensionFrame, text="(Hier :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelPuissanceApparenteMaxN1.grid(row=4, column=3, sticky=tk.E, padx=30, pady=10)
            valuePuissanceApparenteMaxN1 = tk.Label(tensionFrame, textvariable = PuissanceApparenteMaxN1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valuePuissanceApparenteMaxN1.grid(row=4, column=4, sticky=tk.E, padx=30, pady=10)
            unitPuissanceApparenteMaxN1= tk.Label(tensionFrame, text="VA)", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            unitPuissanceApparenteMaxN1.grid(row=4, column=5, sticky=tk.W, padx=30, pady=10)

    else :
        LabelPhase1 = tk.Label(tensionFrame, text="Phase 1", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=colorPhase1)
        LabelPhase1.grid(row=1, column=1, padx=10, pady=(20,10))
        LabelPhase2 = tk.Label(tensionFrame, text="Phase 2", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=colorPhase2)
        LabelPhase2.grid(row=1, column=2, padx=10, pady=(20,10))
        LabelPhase3 = tk.Label(tensionFrame, text="Phase 3", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=colorPhase3)
        LabelPhase3.grid(row=1, column=3, padx=10, pady=(20,10))

        LabelTensionEfficace = tk.Label(tensionFrame, text="Tension efficace :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTensionEfficace.grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        valueTensionEfficacePhase1 = tk.Label(tensionFrame, textvariable = TensionEfficacePhase1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTensionEfficacePhase1.grid(row=2, column=1, sticky=tk.E, padx=10, pady=10)
        valueTensionEfficacePhase2 = tk.Label(tensionFrame, textvariable = TensionEfficacePhase2, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTensionEfficacePhase2.grid(row=2, column=2, sticky=tk.E, padx=10, pady=10)
        valueTensionEfficacePhase3 = tk.Label(tensionFrame, textvariable = TensionEfficacePhase3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTensionEfficacePhase3.grid(row=2, column=3, sticky=tk.E, padx=10, pady=10)
        unitTensionEfficace = tk.Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitTensionEfficace.grid(row=2, column=4, sticky=tk.E, padx=10, pady=10)

        LabelTensionMoyenne = tk.Label(tensionFrame, text="Tension moyenne :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTensionMoyenne.grid(row=3, column=0, sticky=tk.E, padx=10, pady=10)
        valueTensionMoyennePhase1 = tk.Label(tensionFrame, textvariable = TensionMoyennePhase1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTensionMoyennePhase1.grid(row=3, column=1, sticky=tk.E, padx=10, pady=10)
        valueTensionMoyennePhase2 = tk.Label(tensionFrame, textvariable = TensionMoyennePhase2, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTensionMoyennePhase2.grid(row=3, column=2, sticky=tk.E, padx=10, pady=10)
        valueTensionMoyennePhase3 = tk.Label(tensionFrame, textvariable = TensionMoyennePhase3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTensionMoyennePhase3.grid(row=3, column=3, sticky=tk.E, padx=10, pady=10)
        unitTensionMoyenne = tk.Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitTensionMoyenne.grid(row=3, column=4, sticky=tk.E, padx=10, pady=10)

        LabelPuissanceApparente = tk.Label(tensionFrame, text="Puissance apprente :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelPuissanceApparente.grid(row=4, column=0, sticky=tk.E, padx=10, pady=(55,10))
        valuePuissanceApparentePhase1 = tk.Label(tensionFrame, textvariable = PuissanceApparentePhase1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparentePhase1.grid(row=4, column=1, sticky=tk.E, padx=10, pady=(55,10))
        valuePuissanceApparentePhase2 = tk.Label(tensionFrame, textvariable = PuissanceApparentePhase2, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparentePhase2.grid(row=4, column=2, sticky=tk.E, padx=10, pady=(55,10))
        valuePuissanceApparentePhase3 = tk.Label(tensionFrame, textvariable = PuissanceApparentePhase3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparentePhase3.grid(row=4, column=3, sticky=tk.E, padx=10, pady=(55,10))
        unitTensionMoyenne = tk.Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitTensionMoyenne.grid(row=4, column=4, sticky=tk.E, padx=10, pady=(55,10))

        LabelPuissanceMaxAtteinte = tk.Label(tensionFrame, text="Puissance maximale atteinte :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelPuissanceMaxAtteinte.grid(row=5, column=0, sticky=tk.E, padx=10, pady=10)
        valuePuissanceMaxAtteintePhase1 = tk.Label(tensionFrame, textvariable = PuissanceMaxAtteintePhase1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceMaxAtteintePhase1.grid(row=5, column=1, sticky=tk.E, padx=10, pady=10)
        valuePuissanceMaxAtteintePhase2 = tk.Label(tensionFrame, textvariable = PuissanceMaxAtteintePhase3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceMaxAtteintePhase2.grid(row=5, column=2, sticky=tk.E, padx=10, pady=10)
        valuePuissanceMaxAtteintePhase3 = tk.Label(tensionFrame, textvariable = PuissanceMaxAtteintePhase3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceMaxAtteintePhase3.grid(row=5, column=3, sticky=tk.E, padx=10, pady=10)
        unitPuissanceMaxAtteinte = tk.Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitPuissanceMaxAtteinte.grid(row=5, column=4, sticky=tk.E, padx=10, pady=10)

        LabelPuissanceApparenteMaxN1 = tk.Label(tensionFrame, text="Puissance maximale hier :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelPuissanceApparenteMaxN1.grid(row=6, column=0, sticky=tk.E, padx=10, pady=10)
        valuePuissanceApparenteMaxN1Phase1 = tk.Label(tensionFrame, textvariable = PuissanceApparenteMaxN1Phase1, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparenteMaxN1Phase1.grid(row=6, column=1, sticky=tk.E, padx=10, pady=10)
        valuePuissanceApparenteMaxN1Phase2 = tk.Label(tensionFrame, textvariable = PuissanceApparenteMaxN1Phase3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparenteMaxN1Phase2.grid(row=6, column=2, sticky=tk.E, padx=10, pady=10)
        valuePuissanceApparenteMaxN1Phase3 = tk.Label(tensionFrame, textvariable = PuissanceApparenteMaxN1Phase3, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparenteMaxN1Phase3.grid(row=6, column=3, sticky=tk.E, padx=10, pady=10)
        unitPuissanceApparenteMaxN1= tk.Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        unitPuissanceApparenteMaxN1.grid(row=6, column=4, sticky=tk.E, padx=10, pady=10)

        if analysedDict["ModeTIC"] == "Historique" :
            LabelPresenceDesPotentiels = tk.Label(tensionFrame, text="Présence des potentiels :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            LabelPresenceDesPotentiels.grid(row=7, column=0, sticky=tk.E, padx=10, pady=(55,10))
            valuePresenceDesPotentiels = tk.Label(tensionFrame, textvariable = PresenceDesPotentiels, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
            valuePresenceDesPotentiels.grid(row=7, column=1, columnspan=3, sticky=tk.W, padx=10, pady=(55,10))



    #===============================================================================
    #=== Population de la frame Intensités                                       ===
    #===============================================================================
    if ldebug>2 : print("   - Instantiation de la frame 'Intensités'")
    global xscale, xscaleButton, IINST, IINST1, IINST2, IINST3, v
    IINST  = tk.StringVar()
    IINST1 = tk.StringVar()
    IINST2 = tk.StringVar()
    IINST3 = tk.StringVar()

    COURBETITLE = tk.StringVar()
    COURBETITLE.set("Courbes d'intensités")
    courbeTitle = tk.Label(intensiteFrameT, textvariable = COURBETITLE, font=(textFont,textSizeBig), bg=labelBg, fg=titleColor, relief=tk.GROOVE)
    courbeTitle.grid(row=0, column=0, padx=300, ipadx=15, ipady=15)

    if analysedDict["TypeCompteur"] == "MONO" :
        iMax = analysedDict["IntensiteSouscrite"] * 5
    else :
        iMax = analysedDict["IntensiteSouscrite"] * 5 / 3

    # Tracé des axes
    canvas.create_line ((49,20),(49,491),(790,491), width=3, arrow="both", arrowshape=(10,25,5), fill=config.get('GUICSS','graphAxis'))

    #Tracé de la limite d'intensité
    canvas.create_line ((40,90),(780,90), width=1, dash=(8,4), fill = config.get('GUICSS','graphLandmark'))
    canvas.create_text ((20,90),text = str(iMax) + "A", fill = config.get('GUICSS','graphLabelColor'), font = (config.get('GUICSS','graphLabelFont'), config.get('GUICSS','graphValueSize')))

    # Radio button pour le changement d'échelle du graph
    xscale = 20
    v = tk.IntVar()
    scaleValues = [("20", 20), ("50", 50), ("100", 100), ("350", 350), ("700", 700)]

    tk.Label(intensiteFrameR,
             text="Scale X",
             font=(textFont,textSizeBig),
             bg=labelBg,
             fg=labelColor,
             justify = tk.LEFT,
             padx = 30,
             pady = 20).pack()

    for scale, val in scaleValues:
        tk.Radiobutton(intensiteFrameR,
                  text=scale,
                  font=(textFont,textSizeMedium),
                  fg=notebookBgColor,
                  bg=notebookBgColor,
                  borderwidth=0,
                  image=boutonFonce,
                  compound=tk.CENTER,
                  selectimage=boutonClair,
                  selectcolor=notebookBgColor,
                  highlightbackground=notebookBgColor,
                  indicatoron = 0,
                  padx = 0,
                  pady = 0,
                  variable=v,
                  command=changeXScale,
                  value=val).pack(anchor=tk.W)
    v.set("20")

    tk.Label(intensiteFrameR, font=(textFont,textSizeMedium), bg=labelBg, fg=colorPhase1, padx=6, pady=5).pack(anchor=tk.W)
    IINST1.set("Phase 1 : " + str(analysedDict["IntensiteInstantaneePhase1"]) + " A")
    valueIINST1 = tk.Label(intensiteFrameR, textvariable = IINST1, font=(textFont,textSizeMedium), bg=labelBg, fg=colorPhase1, padx=6, pady=5).pack(anchor=tk.W)
    if "IntensiteInstantaneePhase2" in analysedDict :
        IINST1.set("Phase 2 : " + str(analysedDict["IntensiteInstantaneePhase2"]) + " A")
        valueIINST2 = tk.Label(intensiteFrameR, textvariable = IINST2, font=(textFont,textSizeMedium), bg=labelBg, fg=colorPhase2, padx=6, pady=5).pack(anchor=tk.W)
    if "IntensiteInstantaneePhase3" in analysedDict :
        IINST3.set("Phase 3 : " + str(analysedDict["IntensiteInstantaneePhase3"]) + " A")
        valueIINST3 = tk.Label(intensiteFrameR, textvariable = IINST3, font=(textFont,textSizeMedium), bg=labelBg, fg=colorPhase3, padx=6, pady=5).pack(anchor=tk.W)


    #===============================================================================
    #=== Population de la frame REGISTRE                                         ===
    #===============================================================================
    if ldebug>2 : print("   - Instantiation de la frame 'Registre'")
    REGISTRETITLE = tk.StringVar()
    REGISTRETITLE.set("Etat du registre du compteur")
    registreTitle = tk.Label(registreFrame, textvariable = REGISTRETITLE, font=(textFont,textSizeBig), bg=labelBg, fg=titleColor, relief=tk.GROOVE)
    registreTitle.grid(row=0, column=0, columnspan = 12, padx=15, ipadx=15, ipady=15)

    # Population de la frame INFORMATION en mode TIC STANDARD
    if analysedDict["ModeTIC"] == "Standard" :
        global CONTACT
        CONTACT = tk.StringVar()
        LabelContactSec = tk.Label(registreFrame, text="Contact sec : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelContactSec.grid(row=1, column=0, sticky=tk.E, padx=10, pady=(20,2))
        valueContactSec = tk.Label(registreFrame, textvariable = CONTACT, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueContactSec.grid(row=1, column=1, sticky=tk.W, padx=10, pady=(20,2))

        global COUPURE
        COUPURE = tk.StringVar()
        LabelOrganeDeCoupure = tk.Label(registreFrame, text="Organe de coupure : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelOrganeDeCoupure.grid(row=2, column=0, sticky=tk.E, padx=10, pady=2)
        valueOrganeDeCoupure = tk.Label(registreFrame, textvariable = COUPURE, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueOrganeDeCoupure.grid(row=2, column=1, sticky=tk.W, padx=10, pady=2)

        global CACHE
        CACHE = tk.StringVar()
        LabelCacheBorneDistributeur = tk.Label(registreFrame, text="État du cache-bornes distributeur : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelCacheBorneDistributeur.grid(row=3, column=0, sticky=tk.E, padx=10, pady=2)
        valueCacheBorneDistributeur = tk.Label(registreFrame, textvariable = CACHE, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueCacheBorneDistributeur.grid(row=3, column=1, sticky=tk.W, padx=10, pady=2)

        global SURTENSION
        SURTENSION = tk.StringVar()
        LabelSurtensionPhase = tk.Label(registreFrame, text="Surtension sur une des phases : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelSurtensionPhase.grid(row=4, column=0, sticky=tk.E, padx=10, pady=2)
        valueSurtensionPhase = tk.Label(registreFrame, textvariable = SURTENSION, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueSurtensionPhase.grid(row=4, column=1, sticky=tk.W, padx=10, pady=2)

        global DEPASSEMENT
        DEPASSEMENT = tk.StringVar()
        LabelDepassementPuissanceRef = tk.Label(registreFrame, text="Dépassement de la puissance de référence : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelDepassementPuissanceRef.grid(row=5, column=0, sticky=tk.E, padx=10, pady=2)
        valueDepassementPuissanceRef = tk.Label(registreFrame, textvariable = DEPASSEMENT, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueDepassementPuissanceRef.grid(row=5, column=1, sticky=tk.W, padx=10, pady=2)

        global FONCTIONNEMENT
        FONCTIONNEMENT = tk.StringVar()
        LabelFonctionnement = tk.Label(registreFrame, text="Fonctionnement producteur/consommateur : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelFonctionnement.grid(row=6, column=0, sticky=tk.E, padx=10, pady=2)
        valueFonctionnement = tk.Label(registreFrame, textvariable = FONCTIONNEMENT, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueFonctionnement.grid(row=6, column=1, sticky=tk.W, padx=10, pady=2)

        global SENSNRJ
        SENSNRJ = tk.StringVar()
        LabelSensEnergieActive = tk.Label(registreFrame, text="Sens de l’énergie active : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelSensEnergieActive.grid(row=7, column=0, sticky=tk.E, padx=10, pady=2)
        valueSensEnergieActive = tk.Label(registreFrame, textvariable = SENSNRJ, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueSensEnergieActive.grid(row=7, column=1, sticky=tk.W, padx=10, pady=2)

        global TARIFF
        TARIFF = tk.StringVar()
        LabelTarifEnCoursF = tk.Label(registreFrame, text="Tarif en cours sur le contrat fourniture : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTarifEnCoursF.grid(row=8, column=0, sticky=tk.E, padx=10, pady=2)
        valueTarifEnCoursF = tk.Label(registreFrame, textvariable = TARIFF, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTarifEnCoursF.grid(row=8, column=1, sticky=tk.W, padx=10, pady=2)

        global TARIFD
        TARIFD = tk.StringVar()
        LabelTarifEnCoursD = tk.Label(registreFrame, text="Tarif en cours sur le contrat distributeur : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelTarifEnCoursD.grid(row=9, column=0, sticky=tk.E, padx=10, pady=2)
        valueTarifEnCoursD = tk.Label(registreFrame, textvariable = TARIFD, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueTarifEnCoursD.grid(row=9, column=1, sticky=tk.W, padx=10, pady=2)

        global HORLOGE
        HORLOGE = tk.StringVar()
        LabelHorlogeDegradee = tk.Label(registreFrame, text="Mode dégradée de l’horloge : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelHorlogeDegradee.grid(row=10, column=0, sticky=tk.E, padx=10, pady=2)
        valueHorlogeDegradee = tk.Label(registreFrame, textvariable = HORLOGE, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueHorlogeDegradee.grid(row=10, column=1, sticky=tk.W, padx=10, pady=2)

        global ETATTIC
        ETATTIC = tk.StringVar()
        LabelModeTIC = tk.Label(registreFrame, text="État de la sortie télé-information : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelModeTIC.grid(row=11, column=0, sticky=tk.E, padx=10, pady=2)
        valueModeTIC = tk.Label(registreFrame, textvariable = ETATTIC, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueModeTIC.grid(row=11, column=1, sticky=tk.W, padx=10, pady=2)

        global EURIDIS
        EURIDIS = tk.StringVar()
        LabelSortieCommEuridis = tk.Label(registreFrame, text="État de la sortie communication Euridis : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelSortieCommEuridis.grid(row=12, column=0, sticky=tk.E, padx=10, pady=2)
        valueSortieCommEuridis = tk.Label(registreFrame, textvariable = EURIDIS, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueSortieCommEuridis.grid(row=12, column=1, sticky=tk.W, padx=10, pady=2)

        global STATCPL
        STATCPL = tk.StringVar()
        LabelStatutCPL = tk.Label(registreFrame, text="Statut du CPL : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelStatutCPL.grid(row=13, column=0, sticky=tk.E, padx=10, pady=2)
        valueStatutCPL = tk.Label(registreFrame, textvariable = STATCPL, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueStatutCPL.grid(row=13, column=1, sticky=tk.W, padx=10, pady=2)

        global SYNCCPL
        SYNCCPL = tk.StringVar()
        LabelSynchroCPL = tk.Label(registreFrame, text="Synchronisation CPL : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelSynchroCPL.grid(row=14, column=0, sticky=tk.E, padx=10, pady=2)
        valueSynchroCPL = tk.Label(registreFrame, textvariable = SYNCCPL, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueSynchroCPL.grid(row=14, column=1, sticky=tk.W, padx=10, pady=2)

        global TEMPOJOUR
        TEMPOJOUR = tk.StringVar()
        LabelCouleurTEMPOJour = tk.Label(registreFrame, text="Couleur du jour pour le contrat historique TEMPO : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelCouleurTEMPOJour.grid(row=15, column=0, sticky=tk.E, padx=10, pady=2)
        valueCouleurTEMPOJour = tk.Label(registreFrame, textvariable = TEMPOJOUR, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueCouleurTEMPOJour.grid(row=15, column=1, sticky=tk.W, padx=10, pady=2)

        global TEMPODEMAIN
        TEMPODEMAIN = tk.StringVar()
        LabelCouleurTEMPODemain = tk.Label(registreFrame, text="Couleur du lendemain pour le contrat historique TEMPO : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelCouleurTEMPODemain.grid(row=16, column=0, sticky=tk.E, padx=10, pady=2)
        valueCouleurTEMPODemain = tk.Label(registreFrame, textvariable = TEMPODEMAIN, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueCouleurTEMPODemain.grid(row=16, column=1, sticky=tk.W, padx=10, pady=2)

        global PREAVISPOINTE
        PREAVISPOINTE = tk.StringVar()
        LabelPreavisPointesMobiles = tk.Label(registreFrame, text="Préavis pointes mobiles : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelPreavisPointesMobiles.grid(row=17, column=0, sticky=tk.E, padx=10, pady=2)
        valuePreavisPointesMobiles = tk.Label(registreFrame, textvariable = PREAVISPOINTE, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePreavisPointesMobiles.grid(row=17, column=1, sticky=tk.W, padx=10, pady=2)

        global POINTEMOBILE
        POINTEMOBILE = tk.StringVar()
        LabelPointeMobile = tk.Label(registreFrame, text="Pointe mobile (PM) : ", font=(textFont,textSizeSmall,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelPointeMobile.grid(row=18, column=0, sticky=tk.E, padx=10, pady=2)
        valuePointeMobile = tk.Label(registreFrame, textvariable = POINTEMOBILE, font=(textFont,textSizeSmall), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valuePointeMobile.grid(row=18, column=1, sticky=tk.W, padx=10, pady=2)


    #===============================================================================
    #=== Population de la frame STATUS                                           ===
    #===============================================================================
    if ldebug>2 : print("   - Instantiation de la frame 'Status'")
    MTIC = tk.StringVar()
    MTIC.set(analysedDict["ModeTIC"])
    LabelMTIC = tk.Label(statusFrame, text="Mode de la TIC :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelMTIC.grid(row=5, column=0, sticky=tk.E, padx=10, pady=10)
    valueMTIC = tk.Label(statusFrame, textvariable = MTIC, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueMTIC.grid(row=5, column=1, columnspan=8, sticky=tk.W, padx=10, pady=10)

    if analysedDict["ModeTIC"] == "Standard" :
        VTIC = tk.StringVar()
        VTIC.set(analysedDict["VersionTIC"])
        LabelVTIC = tk.Label(statusFrame, text="Version :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelVTIC.grid(row=5, column=9, sticky=tk.W, padx=10, pady=10)
        valueVTIC = tk.Label(statusFrame, textvariable = VTIC, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueVTIC.grid(row=5, column=10, sticky=tk.W, padx=10, pady=10)

        DATELINKY = tk.StringVar()
        DATELINKY.set(analysedDict["DateHeureLinky"])
        LabelDATE = tk.Label(statusFrame, text="Horodatage Linky :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelDATE.grid(row=7, column=0, sticky=tk.E, padx=10, pady=(10,30))
        valueDATE = tk.Label(statusFrame, textvariable = DATE, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueDATE.grid(row=7, column=1, columnspan=9, sticky=tk.W, padx=10, pady=(10,30))

        global MSG1, MSG2
        MSG1 = tk.StringVar()
        MSG2 = tk.StringVar()
        if "MSG1" in analysedDict :
            MSG1.set(analysedDict["MessageCourt"])
        else :
            MSG1.set("")
        LabelMSG1 = tk.Label(statusFrame, text="Message court :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelMSG1.grid(row=8, column=0, sticky=tk.E, padx=10, pady=5)
        valueMSG1 = tk.Label(statusFrame, textvariable = MSG1, font=(textFont,textSizeMedium, "italic"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueMSG1.grid(row=8, column=1, columnspan=10, sticky=tk.W, padx=10, pady=5)
        if "MSG2" in analysedDict :
            MSG2.set(analysedDict["MessageUltraCourt"])
        else :
            MSG2.set("")
        LabelMSG2 = tk.Label(statusFrame, text="Message ultra court :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelMSG2.grid(row=9, column=0, sticky=tk.E, padx=10, pady=5)
        valueMSG2 = tk.Label(statusFrame, textvariable = MSG2, font=(textFont,textSizeMedium, "italic"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueMSG2.grid(row=9, column=1, columnspan=10, sticky=tk.W, padx=10, pady=5)

        global Relais1Icon, Relais2Icon, Relais3Icon, Relais4Icon, Relais5Icon, Relais6Icon, Relais7Icon, Relais8Icon
        LabelRelais = tk.Label(statusFrame, text="Relais :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelRelais.grid(row=10, column=0, sticky=tk.E, padx=10, pady=(30,10))
        Relais1Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais1Icon.grid(row=10, column=1, padx=2, pady=(30,1))
        Relais2Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais2Icon.grid(row=10, column=2, padx=2, pady=(30,1))
        Relais3Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais3Icon.grid(row=10, column=3, padx=2, pady=(30,1))
        Relais4Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais4Icon.grid(row=10, column=4, padx=2, pady=(30,1))
        Relais5Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais5Icon.grid(row=10, column=5, padx=2, pady=(30,1))
        Relais6Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais6Icon.grid(row=10, column=6, padx=2, pady=(30,1))
        Relais7Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais7Icon.grid(row=10, column=7, padx=2, pady=(30,1))
        Relais8Icon = tk.Label(statusFrame, image=miniVoyantNoir, borderwidth=0)
        Relais8Icon.grid(row=10, column=8, padx=2, pady=(30,1))
        LabelR1 = tk.Label(statusFrame, text="1", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR1.grid(row=11, column=1, padx=2, pady=0)
        LabelR2 = tk.Label(statusFrame, text="2", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR2.grid(row=11, column=2, padx=2, pady=0)
        LabelR3 = tk.Label(statusFrame, text="3", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR3.grid(row=11, column=3, padx=2, pady=0)
        LabelR4 = tk.Label(statusFrame, text="4", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR4.grid(row=11, column=4, padx=2, pady=0)
        LabelR5 = tk.Label(statusFrame, text="5", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR5.grid(row=11, column=5, padx=2, pady=0)
        LabelR6 = tk.Label(statusFrame, text="6", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR6.grid(row=11, column=6, padx=2, pady=0)
        LabelR7 = tk.Label(statusFrame, text="7", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR7.grid(row=11, column=7, padx=2, pady=0)
        LabelR8 = tk.Label(statusFrame, text="8", font=(textFont), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelR8.grid(row=11, column=8, padx=2, pady=0)


    else :
        MotEtat = tk.StringVar()
        MotEtat.set(analysedDict["MotEtat"])
        LabelMotEtat = tk.Label(statusFrame, text="Mot d'état du compteur :", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        LabelMotEtat.grid(row=5, column=2, sticky=tk.E, padx=10, pady=10)
        valueMotEtat = tk.Label(statusFrame, textvariable = MotEtat, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
        valueMotEtat.grid(row=5, column=3, sticky=tk.W, padx=10, pady=10)




#===============================================================================
#=== Init de la frame PARAMETRES                                             ===
#===============================================================================
def initParam() :
    global ButtonDBActive, ValueDebug, scaleDBVal, scaleFileVal, timerDB, timerFile, timerMQTT, ButtonMQActive
    global cmdIcon, rebootIcon, ONButton, OFFButton, flecheD, flecheG
    global valueDB, DBSTATE, valueMQ, MQSTATE

    if ldebug>2 : print("   - Instantiation de la frame 'Paramètres'")

    cmdIcon         = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/cmd.png")
    rebootIcon      = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/reboot.png")
    ONButton        = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/ON.png")
    OFFButton       = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/OFF.png")
    flecheD         = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/flecheDR.png")
    flecheG         = tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/flecheGA.png")

    flagDBActive    = config.get('POSTGRESQL','active')
    refreshDB       = config.get('POSTGRESQL','refreshDB')
    debugLevel      = config.get('PARAM','debugLevel')
    refreshPlage    = config.get('PARAM','refreshPlage')
    refreshStats    = config.get('PARAM','refreshStats')
    refreshIndex    = config.get('PARAM','refreshIndex')
    flagFileActive  = config.get('PARAM','traceActive')
    refreshFile     = config.get('PARAM','traceFreq')
    LinkyRPiVersion = config.get('PARAM','version')
    MQTTActive      = config.get('MQTT','MQTTActive')
    refreshMQTT     = config.get('MQTT','refreshMQTT')

    PARAMTITLE = tk.StringVar()
    PARAMTITLE.set("Paramètres de l'application")
    paramTitle = tk.Label(paramFrameT, textvariable = PARAMTITLE, font=(textFont,textSizeBig), bg=labelBg, fg=titleColor, relief=tk.GROOVE)
    paramTitle.grid(row=0, column=0, columnspan = 12, padx=300, ipadx=15, ipady=15)

    #Paramétrage du module d'envoi vers la DB
    DBSTATE = tk.StringVar()
    LabelDBActive = tk.Label(paramFrameT, text="Enregistrement en DB : ", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelDBActive.grid(row=1, column=0, sticky=tk.E, padx=10, pady=(50,15))
    if flagDBActive == "True" :
        ButtonDBActive = tk.Button(paramFrameT, image=ONButton, bg=labelBg, borderwidth=0, command=switchDB, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    else :
        ButtonDBActive = tk.Button(paramFrameT, image=OFFButton, bg=labelBg, borderwidth=0, command=switchDB, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonDBActive.grid(row=1, column=1, sticky=tk.W, padx=10, pady=(50,15))

    ButtonDBMoins = tk.Button(paramFrameT, image=flecheG, bg=labelBg, borderwidth=0, command=timerDownDB, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonDBMoins.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(50,15))
    timerDB = tk.StringVar()
    timerDB.set(str(refreshDB) + " s")
    DBRefreshValue = tk.Label(paramFrameT, textvariable=timerDB, font=(textFont,textSizeMedium), relief=tk.RIDGE, bg=labelBg, fg=labelColor)
    DBRefreshValue.grid(row=1, column=3, sticky=tk.W, padx=10, pady=(50,15), ipadx=3, ipady=3)
    ButtonDBPlus = tk.Button(paramFrameT, image=flecheD, bg=labelBg, borderwidth=0, command=timerUpDB, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonDBPlus.grid(row=1, column=4, sticky=tk.W, padx=10, pady=(50,15))
    valueDB = tk.Label(paramFrameT, textvariable = DBSTATE, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueDB.grid(row=1, column=5, columnspan=10, sticky=tk.W, padx=10, pady=(50,15))

    #Paramétrage du module d'envoi MQTT
    MQSTATE = tk.StringVar()
    LabelMQActive = tk.Label(paramFrameT, text="Envoi vers broker MQTT : ", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelMQActive.grid(row=2, column=0, sticky=tk.E, padx=10, pady=(15))
    if MQTTActive == "True" :
        ButtonMQActive = tk.Button(paramFrameT, image=ONButton, bg=labelBg, borderwidth=0, command=switchMQ, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    else :
        ButtonMQActive = tk.Button(paramFrameT, image=OFFButton, bg=labelBg, borderwidth=0, command=switchMQ, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonMQActive.grid(row=2, column=1, sticky=tk.W, padx=10, pady=15)

    ButtonMQMoins = tk.Button(paramFrameT, image=flecheG, bg=labelBg, borderwidth=0, command=timerDownMQ, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonMQMoins.grid(row=2, column=2, sticky=tk.W, padx=10, pady=(5))
    timerMQTT = tk.StringVar()
    timerMQTT.set(str(refreshMQTT) + " s")
    MQRefreshValue = tk.Label(paramFrameT, textvariable=timerMQTT, font=(textFont,textSizeMedium), relief=tk.RIDGE, bg=labelBg, fg=labelColor)
    MQRefreshValue.grid(row=2, column=3, sticky=tk.W, padx=10, pady=(15), ipadx=3, ipady=3)
    ButtonMQPlus = tk.Button(paramFrameT, image=flecheD, bg=labelBg, borderwidth=0, command=timerUpMQ, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonMQPlus.grid(row=2, column=4, sticky=tk.W, padx=10, pady=(15))
    valueMQ = tk.Label(paramFrameT, textvariable = MQSTATE, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueMQ.grid(row=2, column=5, columnspan=10, sticky=tk.W, padx=10, pady=15)

    #Paramétrage du module d'écriture dans un fichier texte
    LabelFileActive = tk.Label(paramFrameT, text="Enregistrement en Fichier : ", font=(textFont,textSizeMedium,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelFileActive.grid(row=3, column=0, sticky=tk.E, padx=10, pady=15)
    if flagFileActive == "True" :
        ButtonFileActive = tk.Button(paramFrameT, image=ONButton, bg=labelBg, borderwidth=0, command=switchFile, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    else :
        ButtonFileActive = tk.Button(paramFrameT, image=OFFButton, bg=labelBg, borderwidth=0, command=switchFile, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonFileActive.grid(row=3, column=1, sticky=tk.W, padx=10, pady=15)

    ButtonFileMoins = tk.Button(paramFrameT, image=flecheG, bg=labelBg, borderwidth=0, command=timerDownFile, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonFileMoins.grid(row=3, column=2, sticky=tk.W, padx=10, pady=15)
    timerFile = tk.StringVar()
    timerFile.set(str(refreshFile) + " s")
    FileRefreshValue = tk.Label(paramFrameT, textvariable=timerFile, font=(textFont,textSizeMedium), relief=tk.RIDGE, bg=labelBg, fg=labelColor)
    FileRefreshValue.grid(row=3, column=3, sticky=tk.W, padx=10, pady=15, ipadx=3, ipady=3)
    ButtonFilePlus = tk.Button(paramFrameT, image=flecheD, bg=labelBg, borderwidth=0, command=timerUpFile, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    ButtonFilePlus.grid(row=3, column=4, sticky=tk.W, padx=10, pady=15)

    # Boutons du bas de l'écran
    cmdButton = tk.Button(paramFrameB, text="Cmd", command=cmd, image=cmdIcon, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    cmdButton.grid(row=0, column=0, padx=(120,80))

    rebootButton = tk.Button(paramFrameB, text="Reboot", command=reboot, image=rebootIcon, bg=labelBg, borderwidth=0, activebackground=labelBg, highlightbackground=labelBg, highlightcolor=labelBg, highlightthickness=0)
    rebootButton.grid(row=0, column=1, padx=20)


    #Etat de la DB
    OScmd = "ps aux|grep 'LinkyRPiDB.py'|grep -v grep|awk '{print $2}'"
    result = subprocess.run(OScmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')#    if trameDict["DBSTATE"] :
    if result == '' :
        valueDB.config(fg="red")
        DBSTATE.set("No Run")
    else :
        valueDB.config(fg="green")
        DBSTATE.set("PID = " + result.rstrip("\n"))

    #Etat du client MQTT
    OScmd = "ps aux|grep 'LinkyRPiMQTT.py'|grep -v grep|awk '{print $2}'"
    result = subprocess.run(OScmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')#    if trameDict["MQSTATE"] :
    if result == '' :
        valueMQ.config(fg="red")
        MQSTATE.set("No Run")
    else :
        valueMQ.config(fg="green")
        MQSTATE.set("PID = " + result.rstrip("\n"))



#===============================================================================
#=== Init de la frame STATUS                                                 ===
#===============================================================================
def initStatus() :
    if ldebug>2 : print(" - Init de la frame 'Status'")

    STATUSTITLE = tk.StringVar()
    STATUSTITLE.set("Statut de l'application et du compteur")
    statusTitle = tk.Label(statusFrame, textvariable = STATUSTITLE, font=(textFont,textSizeBig), bg=labelBg, fg=titleColor, relief=tk.GROOVE)
    statusTitle.grid(row=0, column=0, columnspan = 12, padx=15, ipadx=15, ipady=15)

    global LISTEN, valueListener
    LISTEN = tk.StringVar()
    LabelListener = tk.Label(statusFrame, text="Etat du process Lintener :", font=(textFont,textSizeBig,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelListener.grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
    valueListener = tk.Label(statusFrame, textvariable = LISTEN, font=(textFont,textSizeBig), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueListener.grid(row=1, column=1, columnspan=10, sticky=tk.W, padx=10, pady=10)

    global DSTATE, valueDispatch
    DSTATE = tk.StringVar()
    LabelDi = tk.Label(statusFrame, text="Etat du proc. Dispatcher :", font=(textFont,textSizeBig,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelDi.grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
    valueDispatch = tk.Label(statusFrame, textvariable = DSTATE, font=(textFont,textSizeBig), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueDispatch.grid(row=2, column=1, columnspan=10, sticky=tk.W, padx=10, pady=10)

    global LANIP, valueIP
    LANIP = tk.StringVar()
    LabelIP = tk.Label(statusFrame, text="Adresse IP (eth0):", font=(textFont,textSizeBig,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelIP.grid(row=3, column=0, sticky=tk.E, padx=10, pady=10)
    valueIP = tk.Label(statusFrame, textvariable = LANIP, font=(textFont,textSizeBig), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueIP.grid(row=3, column=1, columnspan=8, sticky=tk.W, padx=10, pady=10)

    global WLANIP, nomWiFi, forceSignal, signalLabel, valueI2
    WLANIP     = tk.StringVar()
    nomWiFi    = tk.StringVar()
    forceSignal= tk.StringVar()
    LabelI2 = tk.Label(statusFrame, text="(wlan0):", font=(textFont,textSizeBig,"bold"), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    LabelI2.grid(row=4, column=0, sticky=tk.E, padx=10, pady=10)
    valueI2 = tk.Label(statusFrame, textvariable = WLANIP, font=(textFont,textSizeBig), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    valueI2.grid(row=4, column=1, columnspan=8, sticky=tk.W, padx=10, pady=10)
    SSIDI2 = tk.Label(statusFrame, textvariable = nomWiFi, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    SSIDI2.grid(row=4, column=9, columnspan=2, sticky=tk.W, padx=10, pady=10)
    signalI2 = tk.Label(statusFrame, textvariable = forceSignal, font=(textFont,textSizeMedium), relief=tk.FLAT, bg=labelBg, fg=labelColor)
    signalI2.grid(row=4, column=11, sticky=tk.W, padx=10, pady=10)
    signalLabel = tk.Label(statusFrame, image=signalIcon, borderwidth=0)
    signalLabel.grid(row=4, column=12, sticky=tk.E, padx=10, pady=(5,10))


    cmd = "ifconfig eth0|grep 'inet '|cut -d' ' -f 10"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
    if (result != '') and (result != 'wlan0: error fetching interface information: Device not found') :
        valueIP.config(fg="green")
    LANIP.set(result.rstrip("\n"))

    #Etat de la connexion WiFi
    cmd = "ifconfig wlan0|grep 'inet '|cut -d' ' -f 10"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
    if result != '' :
        valueI2.config(fg="green")
        WLANIP.set(result.rstrip("\n"))
        cmd2 = "iwconfig wlan0|grep Quality|cut -d '=' -f 2|cut -d ' ' -f 1"
        result2 = subprocess.run(cmd2,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
        forceSignal.set(result2.rstrip("\n"))
        forceValue = int(result2.split("/")[0]) / int(result2.split("/")[1]) * 100
        cmd2 = "iwconfig wlan0|grep ESSID|cut -d ':' -f 2"
        result2 = subprocess.run(cmd2,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
        nomWiFi.set(result2.rstrip("\n"))
    else :
        forceValue = 0

    if forceValue >= 75 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi4.png")
    elif forceValue >= 50 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi3.png")
    elif forceValue >= 25 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi2.png")
    elif forceValue > 0 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi1.png")
    else :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi0.png")

    signalLabel.configure(image=img2)
    signalLabel.image=img2

    #Etat du process listener
    cmd = "ps aux|grep 'LinkyRPiListen.py'|grep -v grep|awk '{print $2}'"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
    if result == '' :
        valueListener.config(fg="red")
        LISTEN.set("Not runnung")
    else :
        valueListener.config(fg="green")
        LISTEN.set("Running, PID = " + result.rstrip("\n"))

    #Etat du Dispatcher
    cmd = "ps aux|grep 'LinkyRPiDispatch.py'|grep -v grep|awk '{print $2}'"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')#    if trameDict["DISTATE"] :
    if result == '' :
        valueDispatch.config(fg="red")
        DSTATE.set("Not runnung")
    else :
        valueDispatch.config(fg="green")
        DSTATE.set("Running, PID = " + result.rstrip("\n"))

    master.update_idletasks()
    master.update()


#===============================================================================
#=== Etat général du système                                                 ===
#===============================================================================
def refreshStatus():

    global analysedDict, DATE

    if ldebug>2 : print(" - Refresh des données 'Status'")

    #Etat de la connexion LAN
    cmd = "ifconfig eth0|grep 'inet '|cut -d' ' -f 10"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
    if (result != '') and (result != 'wlan0: error fetching interface information: Device not found') :
        valueIP.config(fg="green")
    LANIP.set(result.rstrip("\n"))

    #Etat de la connexion WiFi
    cmd = "ifconfig wlan0|grep 'inet '|cut -d' ' -f 10"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
    if result != '' :
        valueI2.config(fg="green")
        WLANIP.set(result.rstrip("\n"))
        cmd2 = "iwconfig wlan0|grep Quality|cut -d '=' -f 2|cut -d ' ' -f 1"
        result2 = subprocess.run(cmd2,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
        forceSignal.set(result2.rstrip("\n"))
        forceValue = int(result2.split("/")[0]) / int(result2.split("/")[1]) * 100
        cmd2 = "iwconfig wlan0|grep ESSID|cut -d ':' -f 2"
        result2 = subprocess.run(cmd2,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
        nomWiFi.set(result2.rstrip("\n"))
    else :
        forceValue = 0

    if forceValue >= 75 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi4.png")
    elif forceValue >= 50 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi3.png")
    elif forceValue >= 25 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi2.png")
    elif forceValue > 0 :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi1.png")
    else :
        img2=tk.PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi0.png")

    signalLabel.configure(image=img2)
    signalLabel.image=img2

    #Etat du process listener
    cmd = "ps aux|grep 'LinkyRPiListen.py'|grep -v grep|awk '{print $2}'"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
    if result == '' :
        valueListener.config(fg="red")
        LISTEN.set("Not runnung")
    else :
        valueListener.config(fg="green")
        LISTEN.set("Running, PID = " + result.rstrip("\n"))

    #Etat du Dispatcher
    cmd = "ps aux|grep 'LinkyRPiDispatch.py'|grep -v grep|awk '{print $2}'"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')#    if trameDict["DISTATE"] :
    if result == '' :
        valueDispatch.config(fg="red")
        DSTATE.set("Not runnung")
    else :
        valueDispatch.config(fg="green")
        DSTATE.set("Running, PID = " + result.rstrip("\n"))

    #Registre
    if "ContactSec" in analysedDict :
        CONTACT.set(analysedDict["ContactSec"])
    if "OrganeDeCoupure" in analysedDict :
        COUPURE.set(analysedDict["OrganeDeCoupure"])
    if "CacheBorneDistributeur" in analysedDict :
        CACHE.set(analysedDict["CacheBorneDistributeur"])
    if "SurtensionPhase" in analysedDict :
        SURTENSION.set(analysedDict["SurtensionPhase"])
    if "DepassementPuissanceRef" in analysedDict :
        DEPASSEMENT.set(analysedDict["DepassementPuissanceRef"])
    if "Fonctionnement" in analysedDict :
        FONCTIONNEMENT.set(analysedDict["Fonctionnement"])
    if "SensEnergieActive" in analysedDict :
        SENSNRJ.set(analysedDict["SensEnergieActive"])
    if "TarifEnCoursF" in analysedDict :
        TARIFF.set(analysedDict["TarifEnCoursF"])
    if "TarifEnCoursD" in analysedDict :
        TARIFD.set(analysedDict["TarifEnCoursD"])
    if "HorlogeDegradee" in analysedDict :
        HORLOGE.set(analysedDict["HorlogeDegradee"])
    if "ModeTIC" in analysedDict :
        ETATTIC.set(analysedDict["ModeTIC"])
    if "SortieCommEuridis" in analysedDict :
        EURIDIS.set(analysedDict["SortieCommEuridis"])
    if "StatutCPL" in analysedDict :
        STATCPL.set(analysedDict["StatutCPL"])
    if "SynchroCPL" in analysedDict :
        SYNCCPL.set(analysedDict["SynchroCPL"])
    if "CouleurTEMPOJour" in analysedDict :
        TEMPOJOUR.set(analysedDict["CouleurTEMPOJour"])
    if "CouleurTEMPODemain" in analysedDict :
        TEMPODEMAIN.set(analysedDict["CouleurTEMPODemain"])
    if "PreavisPointesMobiles" in analysedDict :
        PREAVISPOINTE.set(analysedDict["PreavisPointesMobiles"])
    if "PointeMobile" in analysedDict :
        POINTEMOBILE.set(analysedDict["PointeMobile"])


    master.update_idletasks()
    master.update()

    master.after(config.get('PARAM','refreshStats'), refreshStatus)


#===============================================================================
#=== Refresh des plages horaires                                             ===
#===============================================================================
def refreshPlages():

    global analysedDict

    if ldebug>1 : print(" - Refresh des plages horaires")

    if "PeriodeTarifaireEnCours" in analysedDict :
        if analysedDict["PeriodeTarifaireEnCours"] == 'HC' :
            HPHCIcon.configure(image=voyantHC)
            HPHCIcon.image=voyantHC

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HP' :
            HPHCIcon.configure(image=voyantHP)
            HPHCIcon.image=voyantHP

        elif analysedDict["PeriodeTarifaireEnCours"] == 'WE' :
            HPHCIcon.configure(image=voyantWE)
            HPHCIcon.image=voyantWE

        elif analysedDict["PeriodeTarifaireEnCours"] == 'PM' :
            HPHCIcon.configure(image=voyantRouge)
            HPHCIcon.image=voyantRouge

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HN' :
            HPHCIcon.configure(image=voyantVert)
            HPHCIcon.image=voyantVert

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HPJB' :
            HPHCIcon.configure(image=voyantHP)
            HPHCIcon.image=voyantHP
            JOURIcon.configure(image=voyantBleu)
            JOURIcon.image=voyantBleu

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HCJB' :
            HPHCIcon.configure(image=voyantHC)
            HPHCIcon.image=voyantHC
            JOURIcon.configure(image=voyantBleu)
            JOURIcon.image=voyantBleu

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HPJW' :
            HPHCIcon.configure(image=voyantHP)
            HPHCIcon.image=voyantHP
            JOURIcon.configure(image=voyantBlanc)
            JOURIcon.image=voyantBlanc

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HCJW' :
            HPHCIcon.configure(image=voyantHC)
            HPHCIcon.image=voyantHC
            JOURIcon.configure(image=voyantBlanc)
            JOURIcon.image=voyantBlanc

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HPJR' :
            HPHCIcon.configure(image=voyantHP)
            HPHCIcon.image=voyantHP
            JOURIcon.configure(image=voyantRouge)
            JOURIcon.image=voyantRouge

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HCJR' :
            HPHCIcon.configure(image=voyantHC)
            HPHCIcon.image=voyantHC
            JOURIcon.configure(image=voyantRouge)
            JOURIcon.image=voyantRouge

    #DEMAIN
    if analysedDict["TarifSouscrit"] in ["TEMPO","EJP"] :
        if "CouleurDemain" in analysedDict :
            if analysedDict["CouleurDemain"] == "Bleu" :
                DEMAINIcon.configure(image=voyantBleu)
                DEMAINIcon.image=voyantHC
            elif analysedDict["CouleurDemain"] == "Blanc" :
                DEMAINIcon.configure(image=voyantBlanc)
                DEMAINIcon.image=voyantHC
            elif analysedDict["CouleurDemain"] == "Rouge" :
                DEMAINIcon.configure(image=voyantRouge)
                DEMAINIcon.image=voyantHC
            else :
                DEMAINIcon.configure(image=voyantNoir)
                DEMAINIcon.image=voyantHC
            #EPJ : on utilise aussi DEMAINIcon (dictionnaire : ProfilProchainJourPointe)

    master.update_idletasks()
    master.update()

    master.after(config.get('PARAM','refreshPlage'), refreshPlages)



#===============================================================================
#=== Refresh des index                                                       ===
#===============================================================================
def refreshIndex():
    global analysedDict

    if ldebug>1 : print(" - Refresh des index")

    if "IndexBase" in analysedDict :
        valueIndex = int(analysedDict["IndexBase"]) / 1000
        BASE.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex1" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex1"]) / 1000
        if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
            IndexHCB.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex2" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex2"]) / 1000
        if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
            IndexHPB.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex3" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex3"]) / 1000
        if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
            IndexHCH.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex4" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex4"]) / 1000
        if (analysedDict["TarifSouscrit"] == "Heures Creuses") :
            IndexHPH.set("{:,}".format(valueIndex))


    if "IndexHC" in analysedDict :
        valueIndex = int(analysedDict["IndexHC"]) / 1000
        HCHC.set("{:,}".format(valueIndex))

    if "IndexHP" in analysedDict :
        valueIndex = int(analysedDict["IndexHP"]) / 1000
        HCHP.set("{:,}".format(valueIndex))

    if "IndexTotal" in analysedDict :
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))

    if "IndexWE" in analysedDict :
        valueIndex = int(analysedDict["IndexWE"]) / 1000
        HWE.set("{:,}".format(valueIndex))

    if "IndexEJPNormale" in analysedDict :
        valueIndex = int(analysedDict["IndexEJPNormale"]) / 1000
        EJPHN.set("{:,}".format(valueIndex))

    if "IndexEJPPointe" in analysedDict :
        valueIndex = int(analysedDict["IndexEJPPointe"]) / 1000
        EJPHN.set("{:,}".format(valueIndex))

    if "IndexHCJB" in analysedDict :
        valueIndex = int(analysedDict["IndexHCJB"]) / 1000
        BBRHCJB.set("{:,}".format(valueIndex))

    if "IndexHPJB" in analysedDict :
        valueIndex = int(analysedDict["IndexHPJB"]) / 1000
        BBRHPJB.set("{:,}".format(valueIndex))

    if "IndexHCJW" in analysedDict :
        valueIndex = int(analysedDict["IndexHCJW"]) / 1000
        BBRHCJW.set("{:,}".format(valueIndex))

    if "IndexHPJW" in analysedDict :
        valueIndex = int(analysedDict["IndexHPJW"]) / 1000
        BBRHPJW.set("{:,}".format(valueIndex))

    if "IndexHCJR" in analysedDict :
        valueIndex = int(analysedDict["IndexHCJR"]) / 1000
        BBRHCJR.set("{:,}".format(valueIndex))

    if "IndexHPJR" in analysedDict :
        valueIndex = int(analysedDict["IndexHPJR"]) / 1000
        BBRHPJR.set("{:,}".format(valueIndex))

    if "DepassementPuissance" in analysedDict :
        DepassementPuissance.set(analysedDict["DepassementPuissance"])

    if "DepassementPuissanceP1" in analysedDict :
        DepassementPuissanceP1.set(analysedDict["DepassementPuissanceP1"])

    if "DepassementPuissanceP2" in analysedDict :
        DepassementPuissanceP2.set(analysedDict["DepassementPuissanceP2"])

    if "DepassementPuissanceP3" in analysedDict :
        DepassementPuissanceP3.set(analysedDict["DepassementPuissanceP3"])

    master.update_idletasks()
    master.update()

    master.after(config.get('PARAM','refreshIndex'), refreshIndex)



#=======================================================================================#
#=== Calcul des coordonnées de la courbe                                             ===#
#=======================================================================================#
def intensite(intensite, liste, xscale, iMax) :

    if ldebug>3 : print(" - Calcul des coordonnées de la courbe")

    newListe = []

    # Ici on gere la liste des valeurs d'intensité et on la limite à 700 valeurs (car max 700 pixels pour la courbe)
    if len(liste) < 700 :
        liste.append(intensite)
    else :
        liste.pop(0)
        liste.append(intensite)

    # i correspond à la 1ere valeur de la liste qu'on va considérer (en fonction de l'échelle choisie)
    if len(liste) < xscale :
        i = 0
    else :
        i = len(liste) - xscale


    # Ici on crée une liste de tuples
    # Chaque tuple correspond à un point de la courge à tracer (x,y)
    # On la recalcule à chaque fois car l'échelle peut avoir changé entre temps
    coords.clear()
    xPlage = 700

    x = 0
    while i < len(liste) :
        xplot = 50 + int((x * (700 / xscale)))
        yplot = 490 - int((liste[i] * (400 / iMax)))
        coords.append((xplot, yplot))
        i = i + 1
        x = x + 1

    newListe = liste
    return coords, newListe


#=======================================================================================#
#=== Refresh des tensions et puissances                                              ===#
#=======================================================================================#
def refreshTension(analysedDict) :

    if ldebug>1 : print(" - Refresh des tensions")

    if "TensionEfficacePhase1" in analysedDict :
        TensionEfficacePhase1.set(analysedDict["TensionEfficacePhase1"])

    if "TensionEfficacePhase2" in analysedDict :
        TensionEfficacePhase2.set(analysedDict["TensionEfficacePhase2"])

    if "TensionEfficacePhase3" in analysedDict :
        TensionEfficacePhase3.set(analysedDict["TensionEfficacePhase3"])

    if "TensionMoyennePhase1" in analysedDict :
        TensionMoyennePhase1.set(analysedDict["TensionMoyennePhase1"])

    if "TensionMoyennePhase2" in analysedDict :
        TensionMoyennePhase2.set(analysedDict["TensionMoyennePhase2"])

    if "TensionMoyennePhase3" in analysedDict :
        TensionMoyennePhase3.set(analysedDict["TensionMoyennePhase3"])

    if "PuissanceApparente" in analysedDict :
        PuissanceApparente.set(analysedDict["PuissanceApparente"])

    if "PuissanceApparentePhase1" in analysedDict :
        PuissanceApparentePhase1.set(analysedDict["PuissanceApparentePhase1"])

    if "PuissanceApparentePhase2" in analysedDict :
        PuissanceApparentePhase2.set(analysedDict["PuissanceApparentePhase2"])

    if "PuissanceApparentePhase3" in analysedDict :
        PuissanceApparentePhase3.set(analysedDict["PuissanceApparentePhase3"])

    if "PuissanceMaxAtteinte" in analysedDict :
        PuissanceMaxAtteinte.set(analysedDict["PuissanceMaxAtteinte"])

    if "PuissanceMaxAtteintePhase1" in analysedDict :
        PuissanceMaxAtteintePhase1.set(analysedDict["PuissanceMaxAtteintePhase1"])

    if "PuissanceMaxAtteintePhase2" in analysedDict :
        PuissanceMaxAtteintePhase2.set(analysedDict["PuissanceMaxAtteintePhase2"])

    if "PuissanceMaxAtteintePhase3" in analysedDict :
        PuissanceMaxAtteintePhase3.set(analysedDict["PuissanceMaxAtteintePhase3"])

    if "PuissanceApparenteMaxN-1" in analysedDict :
        PuissanceApparenteMaxN1.set(analysedDict["PuissanceApparenteMaxN-1"])

    if "PuissanceApparenteMaxN-1Phase1" in analysedDict :
        PuissanceApparenteMaxN1Phase1.set(analysedDict["PuissanceApparenteMaxN-1Phase1"])

    if "PuissanceApparenteMaxN-1Phase2" in analysedDict :
        PuissanceApparenteMaxN1Phase2.set(analysedDict["PuissanceApparenteMaxN-1Phase2"])

    if "PuissanceApparenteMaxN-1Phase3" in analysedDict :
        PuissanceApparenteMaxN1Phase3.set(analysedDict["PuissanceApparenteMaxN-1Phase3"])

    if "PresenceDesPotentiels" in analysedDict :
        PresenceDesPotentiels.set(analysedDict["PresenceDesPotentiels"])

#=======================================================================================#
#=== Refresh des voyants du RELAIS                                                   ===#
#=======================================================================================#
def refreshRelais(analysedDict) :

    if ldebug>1 : print(" - Refresh du relais")

    if "Relais" in analysedDict :
        if analysedDict["Relais"][0] == "0" :
            Relais1Icon.configure(image=miniVoyantNoir)
        else :
            Relais1Icon.configure(image=miniVoyantVert)

        if analysedDict["Relais"][1] == "0" :
            Relais2Icon.configure(image=miniVoyantNoir)
        else :
            Relais2Icon.configure(image=miniVoyantVert)

        if analysedDict["Relais"][2] == "0" :
            Relais3Icon.configure(image=miniVoyantNoir)
        else :
            Relais3Icon.configure(image=miniVoyantVert)

        if analysedDict["Relais"][3] == "0" :
            Relais4Icon.configure(image=miniVoyantNoir)
        else :
            Relais4Icon.configure(image=miniVoyantVert)

        if analysedDict["Relais"][4] == "0" :
            Relais5Icon.configure(image=miniVoyantNoir)
        else :
            Relais5Icon.configure(image=miniVoyantVert)

        if analysedDict["Relais"][5] == "0" :
            Relais6Icon.configure(image=miniVoyantNoir)
        else :
            Relais6Icon.configure(image=miniVoyantVert)

        if analysedDict["Relais"][6] == "0" :
            Relais7Icon.configure(image=miniVoyantNoir)
        else :
            Relais7Icon.configure(image=miniVoyantVert)

        if analysedDict["Relais"][7] == "0" :
            Relais8Icon.configure(image=miniVoyantNoir)
        else :
            Relais8Icon.configure(image=miniVoyantVert)




#=======================================================================================#
#=== Procédure principale                                                            ===#
#=======================================================================================#

initUI = False
trameReceived = False

global iMax
liste = []
listeP1 = []
listeP2 = []
listeP3 = []
coords = []
coordsP1 = []
coordsP2 = []
coordsP3 = []

colorPhase1     = config.get('GUICSS','phase1')
colorPhase2     = config.get('GUICSS','phase2')
colorPhase3     = config.get('GUICSS','phase3')

oldTime = datetime.now()

initStatus()
initParam()

if ldebug>0 : print("Mise en écoute")

#On part en boucle infinie
while True:

    # On lit une trame dans la queue
    try :
        msg = mq.receive(timeout = 1)
        msgJson = json.loads(msg[0])
        #print(json.dumps(msgJson, indent=4))
        analysedDict = dict(msgJson)
        trameReceived = True
    except Exception as e:
        #La queue est vide, on reboucle direct
        #print("Queue vide")
        trameReceived = False

    if trameReceived :

        #On initialise la UI (seulement à réception de la 1ere trame)
        if not initUI :
            if ldebug>1 : print("Première trame reçue")
            if ldebug>8 : print("------------------------------------>")
            if ldebug>8 : print(analysedDict)
            if ldebug>8 : print("<------------------------------------")

            initGUI(analysedDict)
            refreshStatus()
            refreshIndex()
            refreshPlages()
            myNotebook.select(infoFrame)
            initUI = True

        refreshTension(analysedDict)
        refreshRelais(analysedDict)


        # Mise à jour de l'heure affichée
        if "DateHeureLinky" in analysedDict :
            DATE.set(analysedDict["DateHeureLinky"])

        # Calcul de l'intensité max et des intensités instantannées
        # Nb: les intensités instantannées sont calculées sur base de la puissance instantannée et de la tension instantannée,
        #     suivant la formule P = U.I
        #     Cela donne une intensité instantannée plus précise que celle fournie par le compteur qui est donnée sous forme d'Entier

        #Pour compteurs Monophasés
        if analysedDict["TypeCompteur"] == "MONO" :
            iMax = analysedDict["IntensiteSouscrite"] * 5
            u1 = analysedDict["TensionEfficacePhase1"]
            p1 = analysedDict["PuissanceApparente"]

            if (u1 == 0) :
                i1 = 0
            else :
                i1 = p1 / u1

            # Trace de la courbe d'intensité pour compteur monophasé ou triphasé phase 1
            if "IntensiteInstantaneePhase1" in analysedDict :
                IINST1.set("P1 : " + format(i1,'.3f') + " A")
                coords, newListe = intensite(i1, liste, xscale, iMax)

                liste = []
                liste = newListe
                # On efface la courbe
                if len(liste) > 2 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    canvas.delete(courbeP)

                #Et on la recrée
                if len(liste) > 1 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    courbeP = canvas.create_line(fill=colorPhase1, *coords)


        #Pour compteurs Triphasés
        else :
            iMax = analysedDict["IntensiteSouscrite"] * 5 / 3
            u1 = analysedDict["TensionEfficacePhase1"]
            p1 = analysedDict["PuissanceApparentePhase1"]
            u2 = analysedDict["TensionEfficacePhase2"]
            p2 = analysedDict["PuissanceApparentePhase2"]
            u3 = analysedDict["TensionEfficacePhase3"]
            p3 = analysedDict["PuissanceApparentePhase3"]

            if (u1 == 0) :
                i1 = 0
            else :
                i1 = p1 / u1

            if (u2 == 0) :
                i2 = 0
            else :
                i2 = p2 / u2

            if (u3 == 0) :
                i3 = 0
            else :
                i3 = p3 / u3

            # Trace de la courbe d'intensité pour compteur monophasé ou triphasé phase 1
            if "IntensiteInstantaneePhase1" in analysedDict :
                IINST1.set("P1 : " + format(i1,'.3f') + " A")
                coordsP1, newListe = intensite(i1, listeP1, xscale, iMax)

                listeP1 = []
                listeP1 = newListe
                # On efface la courbe
                if len(listeP1) > 2 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    canvas.delete(courbeP1)

                #Et on la recrée
                if len(listeP1) > 1 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    courbeP1 = canvas.create_line(fill=colorPhase1, *coordsP1)

            # Trace de la courbe d'intensité pour compteur triphasé (phase 2)
            if "IntensiteInstantaneePhase2" in analysedDict :
                IINST2.set("P2 : " + format(i2,'.3f') + " A")
                coordsP2, newListe = intensite(i2, listeP2, xscale, iMax)

                listeP2 = []
                listeP2 = newListe
                # On efface la courbe
                if len(listeP2) > 2 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    canvas.delete(courbeP2)

                #Et on la recrée
                if len(listeP2) > 1 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    courbeP2 = canvas.create_line(fill=colorPhase2, *coordsP2)

            # Trace de la courbe d'intensité pour compteur triphasé (phase 3)
            if "IntensiteInstantaneePhase3" in analysedDict :
                IINST3.set("P3 : " + format(i3,'.3f') + " A")
                coordsP3, newListe = intensite(i3, listeP3, xscale, iMax)

                listeP3 = []
                listeP3 = newListe
                # On efface la courbe
                if len(listeP3) > 2 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    canvas.delete(courbeP3)

                #Et on la recrée
                if len(listeP3) > 1 :
                    #canvas.pack(expand=YES, fill=BOTH)
                    courbeP3 = canvas.create_line(fill=colorPhase3, *coordsP3)





    # Et on provoque le refresh de la GUI
    master.update_idletasks()
    master.update()
