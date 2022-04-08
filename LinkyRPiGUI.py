#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Mickael Masci"
from tkinter import *
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

# On se connecte à la queue POSIX via laquelle le backend envoie les trames décodées
queueName = config.get('POSIX','queueGUI')
queueDepth = int(config.get('POSIX','depthGUI'))
mq = posix_ipc.MessageQueue(queueName, posix_ipc.O_CREAT, max_messages=queueDepth)

# Dans le cas où la variable d'environnement DISPLAY ne serait pas définie, on la définie
# Ceci afin d'indiquer sur quel écran on veut afficher la UI (0.0 étant l'écran connecté au port HDMI du Raspberry)
if os.environ.get('DISPLAY','') == '':
    #print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

# On desactive le screen saver parce que ça fait chier et que le réveil via l'écran tactile ne fonctionne pas des masses
cmd = "xset -dpms"
result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')
cmd = "xset s off"
result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')

master = Tk()

#===============================================================================
#=== Bouton QUIT                                                             ===
#===============================================================================
def quit():
    modalConfirm = askyesno(title='Confirmation',
                    message='Are you sure that you want to SHUTDOWN ?')
    if modalConfirm:
        os.system('sudo shutdown -h now')

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
    root = Tk()
    termf = Frame(root, height=1024, width=600)

    termf.pack(fill=BOTH, expand=YES)
    wid = termf.winfo_id()
    os.system('xterm -into %d -geometry 1024x600 -sb &' % wid)

#===============================================================================
#=== Boutons SCALE                                                           ===
#===============================================================================
def changeXScale():
    global xscale

    if xscale == 20 :
        xscale = 50
    elif xscale == 50 :
        xscale = 100
    elif xscale == 100 :
        xscale = 350
    elif xscale == 350 :
        xscale = 700
    else :
        xscale = 20
    xscaleButton.config(text=xscale)
    return xscale




#=======================================================================================#
#=== Initialisation de la UI en fonction de divers paramètres reçus                  ===#
#=======================================================================================#
def initGUI(analysedDict) :

    #Definition des voyants et boutons
    global voyantNoir, voyantBleu, voyantBlanc, voyantRouge, voyantHC, voyantHP, miniVoyantNoir, miniVoyantVert
    global signalIcon, cmdIcon, rebootIcon, quitIcon, buttonBlue
    voyantNoir      = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/NOIR.png")
    voyantBleu      = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/BLEU.png")
    voyantBlanc     = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/BLANC.png")
    voyantRouge     = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/ROUGE.png")
    voyantVert      = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/VERT.png")
    miniVoyantNoir  = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/miniNOIR.png")
    miniVoyantVert  = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/miniVERT.png")
    voyantHC        = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/HC.png")
    voyantHP        = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/HP.png")
    signalIcon      = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi0.png")
    cmdIcon         = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/cmd.png")
    rebootIcon      = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/reboot.png")
    quitIcon        = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/Quit.png")
    buttonBlue      = PhotoImage(master=master, file=config.get('PATH','iconPath') + "/button_bleu.png")

    #On définit les caractéristiques de la GUI
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


    if ldebug>0 : print("Initialisation de la GUI...")

    # On instancie la frame principale de la UI
    master.attributes('-alpha', 0.0)
    master.iconify()
    master.title("Linky TIC analyser")
    master.geometry("1024x600")
    master.minsize(1024,600)
    master.maxsize(1024,600)
    master.configure(bg=notebookBgColor)
    master.config(cursor="none")    # On désactive le curseur parcequ'on a un écran tactile :)
    master.overrideredirect(1)      # On supprime le bord

    #On commence par créer le style de notre UI
    s = ttk.Style()
    s.theme_create( "MyStyle", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] },
                                        "background": notebookBgColor,
                                        "bordercolor": "#FF0000",
                                        "darkcolor": "#00FF00",
                                        "foreground": "#0000FF",
                                        "lightcolor": "FFFF00",
                                        },
            "TNotebook.Tab": {"configure": {"padding": [20, 10],
                                            "background": notebookBgColor,
                                            "foreground": config.get('GUICSS','notebookSelColor'),
                                            "font" : (config.get('GUICSS','notebookFont'), textSizeSmall, 'bold')},
                              "map":       {"background": [("selected", config.get('GUICSS','notebookSelColor'))],
                                            "foreground": [("selected", notebookBgColor)],
                                            "expand": [("selected", [1, 1, 1, 0])] }
                                            }})
    s.theme_use("MyStyle")



    #Puis on crée le notebook
    myNotebook = ttk.Notebook(master)
    myNotebook.pack(padx=0, pady=0)

    # Frame d'information
    infoFrame = Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
    myNotebook.add(infoFrame, text="Informations")

    # Frame des index et dépassements
    indexFrame = Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
    myNotebook.add(indexFrame, text="Index")

    # Frame producteur (seulement en mode PRODUCTEUR)
    if "Fonctionnement" in analysedDict :
        if analysedDict["Fonctionnement"] == "Producteur" :
            productFrame = Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
            myNotebook.add(productFrame, text="Production")

    # Frame des tensions & puissances
    tensionFrame = Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
    myNotebook.add(tensionFrame, text="Tensions & Puissances")


    # Frame(s) du graphique des intensités soutirées
    global canvas
    intensiteFrame  = Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
    intensiteFrameL = Frame(intensiteFrame, width=824, height=600, bg=notebookBgColor)
    intensiteFrameR = Frame(intensiteFrame, width=200, height=600, bg=notebookBgMedium)
    intensiteFrameL.pack(side="left", fill="both", expand=False)
    intensiteFrameR.pack(side="right", fill="both", expand=False)
    myNotebook.add(intensiteFrame, text="Intensités")
    canvas= Canvas(intensiteFrameL, width=824, height=600, bg=graphBg)
    canvas.pack(expand=YES, fill=BOTH)

    # Frame des statuts
    statusFrame  = Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
    statusFrameL = Frame(statusFrame, width=724, height=600, bg=notebookBgColor)
    statusFrameR = Frame(statusFrame, width=300, height=600, bg=notebookBgLight)
    statusFrameL.pack(side="left", fill="both", expand=False)
    statusFrameR.pack(side="right", fill="both", expand=False)
    myNotebook.add(statusFrame, text="Status")

    # Frame du REGISTRE (uniquement si la TIC est en mode STANDARD)
    if analysedDict["ModeTIC"] == "Standard" :
        registreFrame = Frame(myNotebook, width=1024, height=600, bg=notebookBgColor)
        myNotebook.add(registreFrame, text="Registre")

    #On instancie le notebook
    myNotebook.select(infoFrame)
    myNotebook.pack()


    #===============================================================================
    #=== Population de la frame INFORMATIONS                                     ===
    #===============================================================================
    if "PRM" in analysedDict :
        FieldPRM = StringVar()
        FieldPRM.set(analysedDict["PRM"])
        labelPRM = Label(infoFrame, text="Point de livraison (PRM) :", font=(textFont,textSizeBig,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelPRM.grid(row=0, column=0, sticky=E, padx=10, pady=(20,10))
        valuePRM = Label(infoFrame, textvariable = FieldPRM, font=(textFont,textSizeBig), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePRM.grid(row=0, column=1, columnspan=3, sticky=W, padx=10, pady=(20,10))

    FieldAddresseCompteur = StringVar()
    FieldAddresseCompteur.set(analysedDict["AdresseCompteur"])
    labelAddresseCompteur = Label(infoFrame, text="Adresse du compteur :", font=(textFont,textSizeBig,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelAddresseCompteur.grid(row=1, column=0, sticky=E, padx=10, pady=(15,10))
    valueAddresseCompteur = Label(infoFrame, textvariable = FieldAddresseCompteur, font=(textFont,textSizeBig), relief=FLAT, bg=labelBg, fg=labelColor)
    valueAddresseCompteur.grid(row=1, column=1, columnspan=3, sticky=W, padx=10, pady=(15,10))

    global DATE
    if "DateHeureLinky" in analysedDict :
        DATE = StringVar()
        DATE.set(analysedDict["DateHeureLinky"])
        valueDATE = Label(infoFrame, textvariable = DATE, font=(textFont,textSizeBig), relief=GROOVE, bg=labelBg, fg=valueColorWar)
        valueDATE.grid(row=0, column=4, rowspan=2, columnspan = 2, padx=15, ipadx=15, ipady=15)

    FieldNomCompteur = StringVar()
    FieldNomCompteur.set(analysedDict["NomCompteur"])
    labelNomCompteur = Label(infoFrame, text="Modèle de compteur :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelNomCompteur.grid(row=2, column=0, sticky=E, padx=10, pady=(30,10))
    valueNomCompteur = Label(infoFrame, textvariable = FieldNomCompteur, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
    valueNomCompteur.grid(row=2, column=1, columnspan=5, sticky=W, padx=10, pady=(30,10))

    FieldIntensiteSouscrite = StringVar()
    FieldPuissanceSouscrite = StringVar()
    if analysedDict["TypeCompteur"] == "MONO" :
        FieldIntensiteSouscrite.set(str(analysedDict["IntensiteSouscrite"]) + " kVA")
        FieldPuissanceSouscrite.set("(" + str(analysedDict["IntensiteSouscrite"] * 5) + " A)")
    else :
        FieldIntensiteSouscrite.set(str(analysedDict["IntensiteSouscrite"]) + " kVA")
        FieldPuissanceSouscrite.set("(" + str(analysedDict["IntensiteSouscrite"] * 5 / 3) + " A)")
    labelIntensiteSouscrite = Label(infoFrame, text="Abonnement :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelIntensiteSouscrite.grid(row=3, column=0, sticky=E, padx=10, pady=(30,10))
    valueIntensiteSouscrite = Label(infoFrame, textvariable = FieldIntensiteSouscrite, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
    valueIntensiteSouscrite.grid(row=3, column=1, sticky=W, padx=(10,2), pady=(30,10))
    valuePuissanceSouscrite = Label(infoFrame, textvariable = FieldPuissanceSouscrite, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
    valuePuissanceSouscrite.grid(row=3, column=2, sticky=W, padx=1, pady=(30,10))

    if "PuissanceCoupure" in analysedDict :
        FieldPuissanceCoupure = StringVar()
        FieldPuissanceCoupure.set(str(analysedDict["PuissanceCoupure"]) + " kVA")
        labelPuissanceCoupure = Label(infoFrame, text="Puissance de coupure :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelPuissanceCoupure.grid(row=4, column=0, sticky=E, padx=10, pady=10)
        valuePuissanceCoupure = Label(infoFrame, textvariable = FieldPuissanceCoupure, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceCoupure.grid(row=4, column=1, sticky=W, padx=10, pady=10)


    FieldTarifSouscrit = StringVar()
    FieldTarifSouscrit.set(analysedDict["TarifSouscrit"])
    labelTarifSouscrit = Label(infoFrame, text="Option tarifaire :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelTarifSouscrit.grid(row=5, column=0, sticky=E, padx=10, pady=(30,10))
    valueTarifSouscrit = Label(infoFrame, textvariable = FieldTarifSouscrit, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
    valueTarifSouscrit.grid(row=5, column=1, columnspan=3, sticky=W, padx=10, pady=(30,10))

    global HPHCIcon
    global JOURIcon
    global DEMAINIcon
    if (analysedDict["TarifSouscrit"] == "Heures Creuses") or (analysedDict["TarifSouscrit"] == "Heures Creuses et Week-end") :
        FieldHorairesHC = StringVar()
        FieldHorairesHC.set("(" + analysedDict["HorairesHC"] + ")")
        valueHorairesHC = Label(infoFrame, textvariable = FieldHorairesHC, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHorairesHC.grid(row=5, column=3, columnspan=2, sticky=W, padx=10, pady=(30,10))
        labelEnCours = Label(infoFrame, text="En cours :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelEnCours.grid(row=6, column=0, sticky=E, padx=10, pady=30)
        HPHCIcon = Label(infoFrame, image=voyantNoir, borderwidth=0)
        HPHCIcon.grid(row=6, column=1, padx=2, pady=2)

    elif analysedDict["TarifSouscrit"] == "Tempo" :
        FieldHorairesHC = StringVar()
        FieldHorairesHC.set("(" + analysedDict["HorairesHC"] + ")")
        valueHorairesHC = Label(infoFrame, textvariable = FieldHorairesHC, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHorairesHC.grid(row=5, column=2, columnspan=2, sticky=W, padx=10, pady=(30,10))
        labelEnCours = Label(infoFrame, text="En cours :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelEnCours.grid(row=6, column=0, sticky=E, padx=10, pady=10)
        HPHCIcon = Label(infoFrame, image=voyantNoir, borderwidth=0)
        HPHCIcon.grid(row=6, column=1, padx=2, pady=2)
        JOURIcon = Label(infoFrame, image=voyantNoir, borderwidth=0)
        JOURIcon.grid(row=6, column=2, sticky=W, padx=2, pady=2)
        labelDEMAIN = Label(infoFrame, text="Demain :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelDEMAIN.grid(row=6, column=3, sticky=W, padx=10, pady=30)
        DEMAINIcon = Label(infoFrame, image=voyantNoir, borderwidth=0)
        DEMAINIcon.grid(row=6, column=4, sticky=W, padx=2, pady=2)

    elif analysedDict["TarifSouscrit"] == "EJP" :
        FieldHorairesHC = StringVar()
        FieldHorairesHC.set("(" + analysedDict["HorairesHC"] + ")")
        valueHorairesHC = Label(infoFrame, textvariable = FieldHorairesHC, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHorairesHC.grid(row=5, column=3, columnspan=2, sticky=W, padx=10, pady=(30,10))
        labelEnCours = Label(infoFrame, text="En cours :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelEnCours.grid(row=6, column=0, sticky=E, padx=10, pady=10)
        HPHCIcon = Label(infoFrame, image=voyantNoir, borderwidth=0)
        HPHCIcon.grid(row=6, column=1, padx=2, pady=2)
        JOURIcon = Label(infoFrame, image=voyantNoir, borderwidth=0)
        JOURIcon.grid(row=6, column=2, sticky=W, padx=2, pady=2)
        labelDEMAIN = Label(infoFrame, text="Demain :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelDEMAIN.grid(row=6, column=3, sticky=W, padx=10, pady=30)
        DEMAINIcon = Label(infoFrame, image=voyantNoir, borderwidth=0)
        DEMAINIcon.grid(row=6, column=4, sticky=W, padx=2, pady=2)





    #===============================================================================
    #=== Population de la frame INDEX                                            ===
    #===============================================================================
    global BASE, HCHC, HCHP, HWE, EJPHN, EJPHPM
    global BBRHCJB, BBRHPJB, BBRHCJW, BBRHPJW, BBRHCJR, BBRHPJR
    global IndexTotal, IndexHPH, IndexHPB, IndexHCH, IndexHCB

    if (analysedDict["TarifSouscrit"] == "Tarif de base") :
        BASE = StringVar()
        valueIndex = int(analysedDict["IndexBase"]) / 1000
        BASE.set("{:,}".format(valueIndex))
        labelBASE = Label(indexFrame, text="Index option Base :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelBASE.grid(row=0, column=0, sticky=E, padx=10, pady=(30,10))
        valueBASE = Label(indexFrame, textvariable = BASE, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueBASE.grid(row=0, column=1, sticky=E, padx=10, pady=(30,10))
        unitBASE = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitBASE.grid(row=0, column=2, sticky=E, padx=10, pady=(30,10))

    elif (analysedDict["TarifSouscrit"] == "Heures Creuses") :
        voyantIndexHP = Label(indexFrame, image=voyantHP, borderwidth=0)
        voyantIndexHP.grid(row=0, column=1, columnspan=2, padx=2, pady=(15,5))
        voyantIndexHC = Label(indexFrame, image=voyantHC, borderwidth=0)
        voyantIndexHC.grid(row=0, column=3, columnspan=2, padx=2, pady=(15,5))

        labelConsoHP = Label(indexFrame, text="Heures Pleines", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHP.grid(row=1, column=1, columnspan = 2, padx=10, pady=(20,10))
        labelConsoHC = Label(indexFrame, text="Heures Creuses", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHC.grid(row=1, column=3, columnspan = 2, padx=10, pady=(20,10))

        labelConsoHPH = Label(indexFrame, text="Saison Haute", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHPH.grid(row=2, column=1, padx=10, pady=(20,10))
        labelConsoHPB = Label(indexFrame, text="Saison Basse", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHPB.grid(row=2, column=2, padx=10, pady=(20,10))
        labelConsoHCH = Label(indexFrame, text="Saison Haute", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHCH.grid(row=2, column=3, padx=10, pady=(20,10))
        labelConsoHCB = Label(indexFrame, text="Saison Basse", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHCB.grid(row=2, column=4, padx=10, pady=(20,10))

        labelIndexS = Label(indexFrame, text="Index saisonnier :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelIndexS.grid(row=3, column=0, sticky=E, padx=10, pady=10)

        IndexHPH = StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex4"]) / 1000
        IndexHPH.set("{:,}".format(valueIndex))
        valueHPH = Label(indexFrame, textvariable = IndexHPH, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHPH.grid(row=3, column=1, padx=10, pady=10)

        IndexHPB = StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex2"]) / 1000
        IndexHPB.set("{:,}".format(valueIndex))
        valueHPB = Label(indexFrame, textvariable = IndexHPB, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHPB.grid(row=3, column=2, padx=10, pady=10)

        IndexHCH = StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex3"]) / 1000
        IndexHCH.set("{:,}".format(valueIndex))
        valueHCH = Label(indexFrame, textvariable = IndexHCH, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHCH.grid(row=3, column=3, padx=10, pady=10)

        IndexHCB = StringVar()
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex1"]) / 1000
        IndexHCB.set("{:,}".format(valueIndex))
        valueHCB = Label(indexFrame, textvariable = IndexHCB, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHCB.grid(row=3, column=4, padx=10, pady=10)

        unitIndexS = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitIndexS.grid(row=3, column=5, sticky=W, padx=10, pady=10)

        labelIndex = Label(indexFrame, text="Index HP/HC :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelIndex.grid(row=4, column=0, sticky=E, padx=10, pady=10)

        HCHP = StringVar()
        valueIndex = int(analysedDict["IndexHP"]) / 1000
        HCHP.set("{:,}".format(valueIndex))
        valueHCHP = Label(indexFrame, textvariable = HCHP, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHCHP.grid(row=4, column=1, columnspan = 2, padx=10, pady=10)

        HCHC = StringVar()
        valueIndex = int(analysedDict["IndexHP"]) / 1000
        HCHC.set("{:,}".format(valueIndex))
        valueHCHC = Label(indexFrame, textvariable = HCHC, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHCHC.grid(row=4, column=3, columnspan = 2, padx=10, pady=10)

        unitIndex = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitIndex.grid(row=4, column=5, sticky=W, padx=10, pady=10)

        IndexTotal = StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        labelTOTAL = Label(indexFrame, text="Index total :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTOTAL.grid(row=5, column=0, sticky=E, padx=10, pady=(15,30))
        valueTOTAL = Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=5, column=1, columnspan = 4, padx=10, pady=(15,30))
        unitTOTAL = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=5, column=5, sticky=W, padx=10, pady=(15,30))


    elif (analysedDict["TarifSouscrit"] == "Heures Creuses et Week-end") :
        HCHC = StringVar()
        valueIndex = int(analysedDict["IndexHC"]) / 1000
        HCHC.set("{:,}".format(valueIndex))
        HCHP = StringVar()
        valueIndex = int(analysedDict["IndexHP"]) / 1000
        HCHP.set("{:,}".format(valueIndex))
        HWE = StringVar()
        valueIndex = int(analysedDict["IndexWE"]) / 1000
        HWE.set("{:,}".format(valueIndex))
        labelConsoHP = Label(indexFrame, text="Heures Pleines", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHP.grid(row=0, column=1, padx=10, pady=(20,10))
        labelConsoHC = Label(indexFrame, text="Heures Creuses", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHC.grid(row=0, column=2, padx=10, pady=(20,10))
        labelConsoWE = Label(indexFrame, text="Heures Week-End", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoWE.grid(row=0, column=3, padx=10, pady=(20,10))
        labelIndex = Label(indexFrame, text="Index HP/HC :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelIndex.grid(row=1, column=0, sticky=E, padx=10, pady=10)
        valueHCHP = Label(indexFrame, textvariable = HCHP, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHCHP.grid(row=1, column=1, sticky=E, padx=10, pady=10)
        valueHCHC = Label(indexFrame, textvariable = HCHC, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHCHC.grid(row=1, column=2, sticky=E, padx=10, pady=10)
        valueWEND = Label(indexFrame, textvariable = HWE, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueWEND.grid(row=1, column=3, sticky=E, padx=10, pady=10)
        unitIndex = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitIndex.grid(row=1, column=4, sticky=E, padx=10, pady=10)

        IndexTotal = StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        labelTOTAL = Label(indexFrame, text="Consommation totale :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTOTAL.grid(row=2, column=0, sticky=E, padx=10, pady=(15,30))
        valueTOTAL = Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=2, column=1, columnspan = 3, padx=10, pady=(15,30))
        unitTOTAL = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=2, column=4, sticky=E, padx=10, pady=(15,30))

    elif (analysedDict["TarifSouscrit"] == "EJP") :
        EJPHN = StringVar()
        valueIndex = int(analysedDict["IndexEJPNormale"]) / 1000
        EJPHN.set("{:,}".format(valueIndex))
        EJPHPM = StringVar()
        valueIndex = int(analysedDict["IndexEJPPointe"]) / 1000
        EJPHN.set("{:,}".format(valueIndex))
        labelConsoEN = Label(indexFrame, text="Heures Normales", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoEN.grid(row=0, column=1, sticky=E, padx=30, pady=(20,10))
        labelConsoEP = Label(indexFrame, text="Heures de Pointe Mobile", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoEP.grid(row=0, column=2, sticky=E, padx=30, pady=(20,10))
        labelIndex = Label(indexFrame, text="Index EJP :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelIndex.grid(row=1, column=0, sticky=E, padx=30, pady=10)
        valueEJPHN = Label(indexFrame, textvariable = EJPHN, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueEJPHN.grid(row=1, column=1, sticky=E, padx=30, pady=10)
        valueEJPHPM = Label(indexFrame, textvariable = EJPHPM, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueEJPHPM.grid(row=1, column=2, sticky=E, padx=30, pady=10)
        unitIndex = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitIndex.grid(row=1, column=3, sticky=E, padx=30, pady=10)

        IndexTotal = StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        labelTOTAL = Label(indexFrame, text="Consommation totale :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTOTAL.grid(row=2, column=0, sticky=E, padx=30, pady=(15,30))
        valueTOTAL = Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=2, column=1, columnspan = 2, padx=30, pady=(15,30))
        unitTOTAL = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=2, column=4, sticky=E, padx=30, pady=(15,30))

    elif (analysedDict["TarifSouscrit"] == "Tempo") :
        BBRHCJB = StringVar()
        valueIndex = int(analysedDict["IndexHCJB"]) / 1000
        BBRHCJB.set("{:,}".format(valueIndex))
        BBRHPJB = StringVar()
        valueIndex = int(analysedDict["IndexHPJB"]) / 1000
        BBRHPJB.set("{:,}".format(valueIndex))
        BBRHCJW = StringVar()
        valueIndex = int(analysedDict["IndexHCJW"]) / 1000
        BBRHCJW.set("{:,}".format(valueIndex))
        BBRHPJW = StringVar()
        valueIndex = int(analysedDict["IndexHPJW"]) / 1000
        BBRHPJW.set("{:,}".format(valueIndex))
        BBRHCJR = StringVar()
        valueIndex = int(analysedDict["IndexHCJR"]) / 1000
        BBRHCJR.set("{:,}".format(valueIndex))
        BBRHPJR = StringVar()
        valueIndex = int(analysedDict["IndexHPJR"]) / 1000
        BBRHPJR.set("{:,}".format(valueIndex))

        labelConsoHP = Label(indexFrame, text="Heures Pleines", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHP.grid(row=0, column=1, sticky=E, padx=30, pady=(20,10))
        labelConsoHC = Label(indexFrame, text="Heures Creuses", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelConsoHC.grid(row=0, column=2, sticky=E, padx=30, pady=(20,10))
        labelIndexB = Label(indexFrame, text="Index Jours Bleus :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelIndexB.grid(row=1, column=0, sticky=E, padx=30, pady=10)
        valueBBRHPJB = Label(indexFrame, textvariable = BBRHPJB, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueBBRHPJB.grid(row=1, column=1, sticky=E, padx=30, pady=10)
        valueBBRHCJB = Label(indexFrame, textvariable = BBRHCJB, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueBBRHCJB.grid(row=1, column=2, sticky=E, padx=30, pady=10)
        unitIndexB = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitIndexB.grid(row=1, column=3, sticky=E, padx=30, pady=10)
        labelIndexW = Label(indexFrame, text="Index Jours Blancs :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelIndexW.grid(row=2, column=0, sticky=E, padx=30, pady=10)
        valueBBRHPJW = Label(indexFrame, textvariable = BBRHPJW, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueBBRHPJW.grid(row=2, column=1, sticky=E, padx=30, pady=10)
        valueBBRHCJW = Label(indexFrame, textvariable = BBRHCJW, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueBBRHCJW.grid(row=2, column=2, sticky=E, padx=30, pady=10)
        unitIndexW = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitIndexW.grid(row=2, column=3, sticky=E, padx=30, pady=10)
        labelIndexR = Label(indexFrame, text="Index Jours Rouges :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelIndexR.grid(row=3, column=0, sticky=E, padx=30, pady=10)
        valueBBRHPJR = Label(indexFrame, textvariable = BBRHPJR, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueBBRHPJR.grid(row=3, column=1, sticky=E, padx=30, pady=10)
        valueBBRHCJR = Label(indexFrame, textvariable = BBRHCJR, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueBBRHCJR.grid(row=3, column=2, sticky=E, padx=30, pady=10)
        unitIndexR = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitIndexR.grid(row=3, column=3, sticky=E, padx=30, pady=10)

        IndexTotal = StringVar()
        valueIndex = int(analysedDict["IndexTotal"]) / 1000
        IndexTotal.set("{:,}".format(valueIndex))
        labelTOTAL = Label(indexFrame, text="Consommation totale :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTOTAL.grid(row=4, column=0, sticky=E, padx=30, pady=(15,30))
        valueTOTAL = Label(indexFrame, textvariable = IndexTotal, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTOTAL.grid(row=4, column=1, columnspan = 2, padx=30, pady=(15,30))
        unitTOTAL = Label(indexFrame, text="kWh", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitTOTAL.grid(row=4, column=4, sticky=E, padx=30, pady=(15,30))

    if analysedDict["ModeTIC"] == "Historique" :
        if analysedDict["TypeCompteur"] == "MONO" :
            global DepassementPuissance
            DepassementPuissance = StringVar()
            labelDepassementPuissance = Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelDepassementPuissance.grid(row=5, column=0, columnspan = 3, sticky=E, padx=30, pady=(45,10))
            valueDepassementPuissance = Label(indexFrame, textvariable = DepassementPuissance, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissance.grid(row=5, column=3, sticky=W, padx=30, pady=(45,10))
        else :
            global DepassementPuissancePhase1
            DepassementPuissancePhase1 = StringVar()
            labelDepassementPuissanceP1 = Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite - Phase 1 :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelDepassementPuissanceP1.grid(row=5, column=0, columnspan = 3, sticky=E, padx=30, pady=(45,10))
            valueDepassementPuissanceP1 = Label(indexFrame, textvariable = DepassementPuissanceP1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissanceP1.grid(row=5, column=3, sticky=W, padx=30, pady=(45,10))

            global DepassementPuissancePhase2
            DepassementPuissancePhase2 = StringVar()
            labelDepassementPuissanceP2 = Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite - Phase 2 :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelDepassementPuissanceP2.grid(row=6, column=0, columnspan = 3, sticky=E, padx=30, pady=(15,10))
            valueDepassementPuissanceP2 = Label(indexFrame, textvariable = DepassementPuissanceP2, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissanceP2.grid(row=6, column=3, sticky=W, padx=30, pady=(45,10))

            global DepassementPuissancePhase3
            DepassementPuissancePhase3 = StringVar()
            labelDepassementPuissanceP3 = Label(indexFrame, text="Avertissement de Dépassement de Puissance Souscrite - Phase 3 :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelDepassementPuissanceP3.grid(row=7, column=0, columnspan = 3, sticky=E, padx=30, pady=(15,10))
            valueDepassementPuissanceP3 = Label(indexFrame, textvariable = DepassementPuissanceP3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valueDepassementPuissanceP3.grid(row=7, column=3, sticky=W, padx=30, pady=(45,10))



    #===============================================================================
    #=== Population de la frame TENSIONS & PUISSANCES                            ===
    #===============================================================================
    global PresenceDesPotentiels, PuissanceApparente, PuissanceApparentePhase1, PuissanceApparentePhase2, PuissanceApparentePhase3
    global PuissanceMaxAtteinte, PuissanceMaxAtteintePhase1, PuissanceMaxAtteintePhase2, PuissanceMaxAtteintePhase3
    global PuissanceApparenteMaxN1, PuissanceApparenteMaxN1Phase1, PuissanceApparenteMaxN1Phase2, PuissanceApparenteMaxN1Phase3
    global TensionEfficacePhase1, TensionEfficacePhase2, TensionEfficacePhase3, TensionMoyennePhase1, TensionMoyennePhase2, TensionMoyennePhase3

    PresenceDesPotentiels         = StringVar()
    PuissanceApparente            = StringVar()
    PuissanceApparentePhase1      = StringVar()
    PuissanceApparentePhase2      = StringVar()
    PuissanceApparentePhase3      = StringVar()
    PuissanceMaxAtteinte          = StringVar()
    PuissanceMaxAtteintePhase1    = StringVar()
    PuissanceMaxAtteintePhase2    = StringVar()
    PuissanceMaxAtteintePhase3    = StringVar()
    PuissanceApparenteMaxN1       = StringVar()
    PuissanceApparenteMaxN1Phase1 = StringVar()
    PuissanceApparenteMaxN1Phase2 = StringVar()
    PuissanceApparenteMaxN1Phase3 = StringVar()
    TensionEfficacePhase1         = StringVar()
    TensionEfficacePhase2         = StringVar()
    TensionEfficacePhase3         = StringVar()
    TensionMoyennePhase1          = StringVar()
    TensionMoyennePhase2          = StringVar()
    TensionMoyennePhase3          = StringVar()

    if analysedDict["TypeCompteur"] == "MONO" :
        if "TensionEfficacePhase1" in analysedDict :
            labelTensionEfficacePhase1 = Label(tensionFrame, text="Tension efficace :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelTensionEfficacePhase1.grid(row=0, column=0, sticky=E, padx=30, pady=(30,10))
            valueTensionEfficacePhase1 = Label(tensionFrame, textvariable = TensionEfficacePhase1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valueTensionEfficacePhase1.grid(row=0, column=1, sticky=E, padx=30, pady=(30,10))
            unitTensionEfficacePhase1 = Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            unitTensionEfficacePhase1.grid(row=0, column=2, sticky=W, padx=30, pady=(30,10))

        if "TensionMoyennePhase1" in analysedDict :
            labelTensionMoyennePhase1 = Label(tensionFrame, text="Tension moyenne :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelTensionMoyennePhase1.grid(row=1, column=0, sticky=E, padx=30, pady=10)
            valueTensionMoyennePhase1 = Label(tensionFrame, textvariable = TensionMoyennePhase1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valueTensionMoyennePhase1.grid(row=1, column=1, sticky=E, padx=30, pady=10)
            unitTensionMoyennePhase1 = Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            unitTensionMoyennePhase1.grid(row=1, column=2, sticky=W, padx=30, pady=10)

        if "PuissanceApparente" in analysedDict :
            labelPuissanceApparente = Label(tensionFrame, text="Puissance apprente :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelPuissanceApparente.grid(row=2, column=0, sticky=E, padx=30, pady=(55,10))
            valuePuissanceApparente = Label(tensionFrame, textvariable = PuissanceApparente, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valuePuissanceApparente.grid(row=2, column=1, sticky=E, padx=30, pady=(55,10))
            unitPuissanceApparente = Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            unitPuissanceApparente.grid(row=2, column=2, sticky=W, padx=30, pady=(55,10))

        if "PuissanceMaxAtteinte" in analysedDict :
            labelPuissanceMaxAtteinte = Label(tensionFrame, text="Puissance maximale atteinte :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelPuissanceMaxAtteinte.grid(row=3, column=0, sticky=E, padx=30, pady=10)
            valuePuissanceMaxAtteinte = Label(tensionFrame, textvariable = PuissanceMaxAtteinte, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valuePuissanceMaxAtteinte.grid(row=3, column=1, sticky=E, padx=30, pady=10)
            unitPuissanceMaxAtteinte= Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            unitPuissanceMaxAtteinte.grid(row=3, column=2, sticky=W, padx=30, pady=10)

        if "PuissanceApparenteMaxN-1" in analysedDict :
            labelPuissanceApparenteMaxN1 = Label(tensionFrame, text="(Hier :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelPuissanceApparenteMaxN1.grid(row=3, column=3, sticky=E, padx=30, pady=10)
            valuePuissanceApparenteMaxN1 = Label(tensionFrame, textvariable = PuissanceApparenteMaxN1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valuePuissanceApparenteMaxN1.grid(row=3, column=4, sticky=E, padx=30, pady=10)
            unitPuissanceApparenteMaxN1= Label(tensionFrame, text="VA)", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            unitPuissanceApparenteMaxN1.grid(row=3, column=5, sticky=W, padx=30, pady=10)

    else :
        labelPhase1 = Label(tensionFrame, text="Phase 1", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=colorPhase1)
        labelPhase1.grid(row=0, column=1, padx=10, pady=(20,10))
        labelPhase2 = Label(tensionFrame, text="Phase 2", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=colorPhase2)
        labelPhase2.grid(row=0, column=2, padx=10, pady=(20,10))
        labelPhase3 = Label(tensionFrame, text="Phase 3", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=colorPhase3)
        labelPhase3.grid(row=0, column=3, padx=10, pady=(20,10))

        labelTensionEfficace = Label(tensionFrame, text="Tension efficace :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTensionEfficace.grid(row=1, column=0, sticky=E, padx=10, pady=10)
        valueTensionEfficacePhase1 = Label(tensionFrame, textvariable = TensionEfficacePhase1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTensionEfficacePhase1.grid(row=1, column=1, sticky=E, padx=10, pady=10)
        valueTensionEfficacePhase2 = Label(tensionFrame, textvariable = TensionEfficacePhase2, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTensionEfficacePhase2.grid(row=1, column=2, sticky=E, padx=10, pady=10)
        valueTensionEfficacePhase3 = Label(tensionFrame, textvariable = TensionEfficacePhase3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTensionEfficacePhase3.grid(row=1, column=3, sticky=E, padx=10, pady=10)
        unitTensionEfficace = Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitTensionEfficace.grid(row=1, column=4, sticky=E, padx=10, pady=10)

        labelTensionMoyenne = Label(tensionFrame, text="Tension moyenne :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTensionMoyenne.grid(row=2, column=0, sticky=E, padx=10, pady=10)
        valueTensionMoyennePhase1 = Label(tensionFrame, textvariable = TensionMoyennePhase1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTensionMoyennePhase1.grid(row=2, column=1, sticky=E, padx=10, pady=10)
        valueTensionMoyennePhase2 = Label(tensionFrame, textvariable = TensionMoyennePhase2, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTensionMoyennePhase2.grid(row=2, column=2, sticky=E, padx=10, pady=10)
        valueTensionMoyennePhase3 = Label(tensionFrame, textvariable = TensionMoyennePhase3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTensionMoyennePhase3.grid(row=2, column=3, sticky=E, padx=10, pady=10)
        unitTensionMoyenne = Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitTensionMoyenne.grid(row=2, column=4, sticky=E, padx=10, pady=10)

        labelPuissanceApparente = Label(tensionFrame, text="Puissance apprente :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelPuissanceApparente.grid(row=3, column=0, sticky=E, padx=10, pady=(55,10))
        valuePuissanceApparentePhase1 = Label(tensionFrame, textvariable = PuissanceApparentePhase1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparentePhase1.grid(row=3, column=1, sticky=E, padx=10, pady=(55,10))
        valuePuissanceApparentePhase2 = Label(tensionFrame, textvariable = PuissanceApparentePhase2, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparentePhase2.grid(row=3, column=2, sticky=E, padx=10, pady=(55,10))
        valuePuissanceApparentePhase3 = Label(tensionFrame, textvariable = PuissanceApparentePhase3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparentePhase3.grid(row=3, column=3, sticky=E, padx=10, pady=(55,10))
        unitTensionMoyenne = Label(tensionFrame, text="VA", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitTensionMoyenne.grid(row=3, column=4, sticky=E, padx=10, pady=(55,10))

        labelPuissanceMaxAtteinte = Label(tensionFrame, text="Puissance maximale atteinte :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelPuissanceMaxAtteinte.grid(row=4, column=0, sticky=E, padx=10, pady=10)
        valuePuissanceMaxAtteintePhase1 = Label(tensionFrame, textvariable = PuissanceMaxAtteintePhase1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceMaxAtteintePhase1.grid(row=4, column=1, sticky=E, padx=10, pady=10)
        valuePuissanceMaxAtteintePhase2 = Label(tensionFrame, textvariable = PuissanceMaxAtteintePhase3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceMaxAtteintePhase2.grid(row=4, column=2, sticky=E, padx=10, pady=10)
        valuePuissanceMaxAtteintePhase3 = Label(tensionFrame, textvariable = PuissanceMaxAtteintePhase3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceMaxAtteintePhase3.grid(row=4, column=3, sticky=E, padx=10, pady=10)
        unitPuissanceMaxAtteinte = Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitPuissanceMaxAtteinte.grid(row=4, column=4, sticky=E, padx=10, pady=10)

        labelPuissanceApparenteMaxN1 = Label(tensionFrame, text="Puissance maximale atteinte :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelPuissanceApparenteMaxN1.grid(row=5, column=0, sticky=E, padx=10, pady=10)
        valuePuissanceApparenteMaxN1Phase1 = Label(tensionFrame, textvariable = PuissanceApparenteMaxN1Phase1, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparenteMaxN1Phase1.grid(row=5, column=1, sticky=E, padx=10, pady=10)
        valuePuissanceApparenteMaxN1Phase2 = Label(tensionFrame, textvariable = PuissanceApparenteMaxN1Phase3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparenteMaxN1Phase2.grid(row=5, column=2, sticky=E, padx=10, pady=10)
        valuePuissanceApparenteMaxN1Phase3 = Label(tensionFrame, textvariable = PuissanceApparenteMaxN1Phase3, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePuissanceApparenteMaxN1Phase3.grid(row=5, column=3, sticky=E, padx=10, pady=10)
        unitPuissanceApparenteMaxN1= Label(tensionFrame, text="V", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        unitPuissanceApparenteMaxN1.grid(row=5, column=4, sticky=E, padx=10, pady=10)

        if analysedDict["ModeTIC"] == "Historique" :
            labelPresenceDesPotentiels = Label(tensionFrame, text="Présence des potentiels :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
            labelPresenceDesPotentiels.grid(row=6, column=0, sticky=E, padx=10, pady=(55,10))
            valuePresenceDesPotentiels = Label(tensionFrame, textvariable = PresenceDesPotentiels, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
            valuePresenceDesPotentiels.grid(row=6, column=1, columnspan=3, sticky=W, padx=10, pady=(55,10))



    #===============================================================================
    #=== Population de la frame Intensités                                       ===
    #===============================================================================
    global xscale, xscaleButton, IINST, IINST1, IINST2, IINST3
    IINST  = StringVar()
    IINST1 = StringVar()
    IINST2 = StringVar()
    IINST3 = StringVar()

    if analysedDict["TypeCompteur"] == "MONO" :
        iMax = analysedDict["IntensiteSouscrite"] * 5
    else :
        iMax = analysedDict["IntensiteSouscrite"] * 5 / 3

    # Tracé des axes
    canvas.create_line ((49,20),(49,491),(790,491), width=3, arrow="both", arrowshape=(10,25,5), fill=config.get('GUICSS','graphAxis'))

    #Tracé de la limite d'intensité
    canvas.create_line ((40,90),(780,90), width=1, dash=(8,4), fill = config.get('GUICSS','graphLandmark'))
    canvas.create_text ((20,90),text = str(iMax) + "A", fill = config.get('GUICSS','graphLabelColor'), font = (config.get('GUICSS','graphLabelFont'), config.get('GUICSS','graphValueSize')))

    #Bouton pour modifier l'échelle X
    buttonFont = font.Font(family=config.get('GUICSS','notebookFont'), size=textSizeBig, weight='bold')
    xscaleLabel = Label(intensiteFrameR, text="Scale X", font=(textFont,textSizeSmall,"bold"), relief=FLAT, fg=notebookBgMedium, borderwidth=0, bg=notebookBgMedium)
    xscaleLabel.grid(row=0, column=0, padx=5, pady=2, sticky=S)
    xscale = 20
    xscaleButton = Button(intensiteFrameR, text=xscale, command=changeXScale, image=buttonBlue, relief=FLAT, compound="center", font=buttonFont, borderwidth=0, bg=notebookBgMedium)
    xscaleButton.grid(row=1, column=0)


    if analysedDict["TypeCompteur"] == "MONO" :
        IINST.set("Phase 1 : " + str(analysedDict["IntensiteInstantanee"]) + " A")
        valueIINST = Label(intensiteFrameR, textvariable = IINST, font=(textFont,textSizeMedium), relief=GROOVE, bg=notebookBgLight, fg=colorPhase1)
        valueIINST.grid(row=4, column=0, padx=2, pady=(80,10))
    else :
        IINST1.set("Phase 1 : " + str(analysedDict["IntensiteInstantaneePhase1"]) + " A")
        valueIINST1 = Label(intensiteFrameR, textvariable = IINST1, font=(textFont,textSizeMedium), relief=GROOVE, bg=notebookBgLight, fg=colorPhase1)
        valueIINST1.grid(row=4, column=0, padx=2, pady=(80,10))
        IINST1.set("Phase 2 : " + str(analysedDict["IntensiteInstantaneePhase2"]) + " A")
        valueIINST2 = Label(intensiteFrameR, textvariable = IINST2, font=(textFont,textSizeMedium), relief=GROOVE, bg=notebookBgLight, fg=colorPhase2)
        valueIINST2.grid(row=5, column=0, padx=2, pady=10)
        IINST3.set("Phase 3 : " + str(analysedDict["IntensiteInstantaneePhase3"]) + " A")
        valueIINST3 = Label(intensiteFrameR, textvariable = IINST3, font=(textFont,textSizeMedium), relief=GROOVE, bg=notebookBgLight, fg=colorPhase3)
        valueIINST3.grid(row=6, column=0, padx=2, pady=10)



    #===============================================================================
    #=== Population de la frame STATUS                                           ===
    #===============================================================================
    global LISTEN, valueListener
    LISTEN = StringVar()
    labelListener = Label(statusFrameL, text="Etat du process Lintener :", font=(textFont,textSizeBig,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelListener.grid(row=0, column=0, sticky=E, padx=10, pady=10)
    valueListener = Label(statusFrameL, textvariable = LISTEN, font=(textFont,textSizeBig), relief=FLAT, bg=labelBg, fg=labelColor)
    valueListener.grid(row=0, column=1, columnspan=10, sticky=W, padx=10, pady=10)

    global DBSTATE, valueDB
    DBSTATE = StringVar()
    labelDB = Label(statusFrameL, text="Etat du process DB :", font=(textFont,textSizeBig,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelDB.grid(row=1, column=0, sticky=E, padx=10, pady=10)
    valueDB = Label(statusFrameL, textvariable = DBSTATE, font=(textFont,textSizeBig), relief=FLAT, bg=labelBg, fg=labelColor)
    valueDB.grid(row=1, column=1, columnspan=10, sticky=W, padx=10, pady=10)

    global LANIP, valueIP
    LANIP = StringVar()
    labelIP = Label(statusFrameL, text="Adresse IP (eth0):", font=(textFont,textSizeBig,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelIP.grid(row=2, column=0, sticky=E, padx=10, pady=10)
    valueIP = Label(statusFrameL, textvariable = LANIP, font=(textFont,textSizeBig), relief=FLAT, bg=labelBg, fg=labelColor)
    valueIP.grid(row=2, column=1, columnspan=8, sticky=W, padx=10, pady=10)

    global WLANIP, nomWiFi, forceSignal, signalLabel, valueI2
    WLANIP     = StringVar()
    nomWiFi    = StringVar()
    forceSignal= StringVar()
    labelI2 = Label(statusFrameL, text="(wlan0):", font=(textFont,textSizeBig,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelI2.grid(row=3, column=0, sticky=E, padx=10, pady=10)
    valueI2 = Label(statusFrameL, textvariable = WLANIP, font=(textFont,textSizeBig), relief=FLAT, bg=labelBg, fg=labelColor)
    valueI2.grid(row=3, column=1, columnspan=8, sticky=W, padx=10, pady=10)
    SSIDI2 = Label(statusFrameL, textvariable = nomWiFi, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
    SSIDI2.grid(row=3, column=9, columnspan=2, sticky=W, padx=10, pady=10)
    signalI2 = Label(statusFrameL, textvariable = forceSignal, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
    signalI2.grid(row=3, column=11, sticky=W, padx=10, pady=10)
    signalLabel = Label(statusFrameL, image=signalIcon, borderwidth=0)
    signalLabel.grid(row=3, column=12, sticky=E, padx=10, pady=(5,10))

    MTIC = StringVar()
    MTIC.set(analysedDict["ModeTIC"])
    labelMTIC = Label(statusFrameL, text="Mode de la TIC :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
    labelMTIC.grid(row=4, column=0, sticky=E, padx=10, pady=10)
    valueMTIC = Label(statusFrameL, textvariable = MTIC, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
    valueMTIC.grid(row=4, column=1, columnspan=8, sticky=W, padx=10, pady=10)

    if analysedDict["ModeTIC"] == "Standard" :
        VTIC = StringVar()
        VTIC.set(analysedDict["VersionTIC"])
        labelVTIC = Label(statusFrameL, text="Version :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelVTIC.grid(row=4, column=9, sticky=W, padx=10, pady=10)
        valueVTIC = Label(statusFrameL, textvariable = VTIC, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueVTIC.grid(row=4, column=10, sticky=W, padx=10, pady=10)

        DATELINKY = StringVar()
        DATELINKY.set(analysedDict["DateHeureLinky"])
        labelDATE = Label(statusFrameL, text="Horodatage Linky :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelDATE.grid(row=5, column=0, sticky=E, padx=10, pady=(10,30))
        valueDATE = Label(statusFrameL, textvariable = DATELINKY, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueDATE.grid(row=5, column=1, columnspan=9, sticky=W, padx=10, pady=(10,30))

        global MSG1, MSG2
        MSG1 = StringVar()
        MSG2 = StringVar()
        if "MSG1" in analysedDict :
            MSG1.set(analysedDict["MessageCourt"])
        else :
            MSG1.set("")
        labelMSG1 = Label(statusFrameL, text="Message court :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelMSG1.grid(row=7, column=0, sticky=E, padx=10, pady=5)
        valueMSG1 = Label(statusFrameL, textvariable = MSG1, font=(textFont,textSizeMedium, "italic"), relief=FLAT, bg=labelBg, fg=labelColor)
        valueMSG1.grid(row=7, column=1, columnspan=10, sticky=W, padx=10, pady=5)
        if "MSG2" in analysedDict :
            MSG2.set(analysedDict["MessageUltraCourt"])
        else :
            MSG2.set("")
        labelMSG2 = Label(statusFrameL, text="Message ultra court :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelMSG2.grid(row=8, column=0, sticky=E, padx=10, pady=5)
        valueMSG2 = Label(statusFrameL, textvariable = MSG2, font=(textFont,textSizeMedium, "italic"), relief=FLAT, bg=labelBg, fg=labelColor)
        valueMSG2.grid(row=8, column=1, columnspan=10, sticky=W, padx=10, pady=5)

        global Relais1Icon, Relais2Icon, Relais3Icon, Relais4Icon, Relais5Icon, Relais6Icon, Relais7Icon, Relais8Icon
        labelRelais = Label(statusFrameL, text="Relais :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelRelais.grid(row=9, column=0, sticky=E, padx=10, pady=(40,10))
        Relais1Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais1Icon.grid(row=9, column=1, padx=2, pady=(40,1))
        Relais2Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais2Icon.grid(row=9, column=2, padx=2, pady=(40,1))
        Relais3Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais3Icon.grid(row=9, column=3, padx=2, pady=(40,1))
        Relais4Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais4Icon.grid(row=9, column=4, padx=2, pady=(40,1))
        Relais5Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais5Icon.grid(row=9, column=5, padx=2, pady=(40,1))
        Relais6Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais6Icon.grid(row=9, column=6, padx=2, pady=(40,1))
        Relais7Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais7Icon.grid(row=9, column=7, padx=2, pady=(40,1))
        Relais8Icon = Label(statusFrameL, image=miniVoyantNoir, borderwidth=0)
        Relais8Icon.grid(row=9, column=8, padx=2, pady=(40,1))
        labelR1 = Label(statusFrameL, text="1", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR1.grid(row=10, column=1, padx=2, pady=0)
        labelR2 = Label(statusFrameL, text="2", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR2.grid(row=10, column=2, padx=2, pady=0)
        labelR3 = Label(statusFrameL, text="3", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR3.grid(row=10, column=3, padx=2, pady=0)
        labelR4 = Label(statusFrameL, text="4", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR4.grid(row=10, column=4, padx=2, pady=0)
        labelR5 = Label(statusFrameL, text="5", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR5.grid(row=10, column=5, padx=2, pady=0)
        labelR6 = Label(statusFrameL, text="6", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR6.grid(row=10, column=6, padx=2, pady=0)
        labelR7 = Label(statusFrameL, text="7", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR7.grid(row=10, column=7, padx=2, pady=0)
        labelR8 = Label(statusFrameL, text="8", font=(textFont), relief=FLAT, bg=labelBg, fg=labelColor)
        labelR8.grid(row=10, column=8, padx=2, pady=0)


    else :
        MotEtat = StringVar()
        MotEtat.set(analysedDict["MotEtat"])
        labelMotEtat = Label(statusFrameL, text="Mot d'état du compteur :", font=(textFont,textSizeMedium,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelMotEtat.grid(row=4, column=2, sticky=E, padx=10, pady=10)
        valueMotEtat = Label(statusFrameL, textvariable = MotEtat, font=(textFont,textSizeMedium), relief=FLAT, bg=labelBg, fg=labelColor)
        valueMotEtat.grid(row=4, column=3, sticky=W, padx=10, pady=10)


    cmdButton = Button(statusFrameR, text="Cmd", command=cmd, image=cmdIcon, bg=labelBg)
    cmdButton.grid(row=0, column=0, pady=(5,80))

    rebootButton = Button(statusFrameR, text="Reboot", command=reboot, image=rebootIcon)
    rebootButton.grid(row=5, column=0, pady=(5,15))

    exitButton = Button(statusFrameR, text="Exit", command=quit, image=quitIcon)
    exitButton.grid(row=7, column=0)


    #===============================================================================
    #=== Population de la frame REGISTRE                                         ===
    #===============================================================================

    # Population de la frame INFORMATION en mode TIC STANDARD
    if analysedDict["ModeTIC"] == "Standard" :
        global CONTACT
        CONTACT = StringVar()
        labelContactSec = Label(registreFrame, text="Contact sec : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelContactSec.grid(row=0, column=0, sticky=E, padx=10, pady=2)
        valueContactSec = Label(registreFrame, textvariable = CONTACT, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueContactSec.grid(row=0, column=1, sticky=W, padx=10, pady=2)

        global COUPURE
        COUPURE = StringVar()
        labelOrganeDeCoupure = Label(registreFrame, text="Organe de coupure : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelOrganeDeCoupure.grid(row=1, column=0, sticky=E, padx=10, pady=2)
        valueOrganeDeCoupure = Label(registreFrame, textvariable = COUPURE, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueOrganeDeCoupure.grid(row=1, column=1, sticky=W, padx=10, pady=2)

        global CACHE
        CACHE = StringVar()
        labelCacheBorneDistributeur = Label(registreFrame, text="État du cache-bornes distributeur : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelCacheBorneDistributeur.grid(row=2, column=0, sticky=E, padx=10, pady=2)
        valueCacheBorneDistributeur = Label(registreFrame, textvariable = CACHE, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueCacheBorneDistributeur.grid(row=2, column=1, sticky=W, padx=10, pady=2)

        global SURTENSION
        SURTENSION = StringVar()
        labelSurtensionPhase = Label(registreFrame, text="Surtension sur une des phases : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelSurtensionPhase.grid(row=3, column=0, sticky=E, padx=10, pady=2)
        valueSurtensionPhase = Label(registreFrame, textvariable = SURTENSION, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueSurtensionPhase.grid(row=3, column=1, sticky=W, padx=10, pady=2)

        global DEPASSEMENT
        DEPASSEMENT = StringVar()
        labelDepassementPuissanceRef = Label(registreFrame, text="Dépassement de la puissance de référence : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelDepassementPuissanceRef.grid(row=4, column=0, sticky=E, padx=10, pady=2)
        valueDepassementPuissanceRef = Label(registreFrame, textvariable = DEPASSEMENT, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueDepassementPuissanceRef.grid(row=4, column=1, sticky=W, padx=10, pady=2)

        global FONCTIONNEMENT
        FONCTIONNEMENT = StringVar()
        labelFonctionnement = Label(registreFrame, text="Fonctionnement producteur/consommateur : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelFonctionnement.grid(row=5, column=0, sticky=E, padx=10, pady=2)
        valueFonctionnement = Label(registreFrame, textvariable = FONCTIONNEMENT, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueFonctionnement.grid(row=5, column=1, sticky=W, padx=10, pady=2)

        global SENSNRJ
        SENSNRJ = StringVar()
        labelSensEnergieActive = Label(registreFrame, text="Sens de l’énergie active : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelSensEnergieActive.grid(row=6, column=0, sticky=E, padx=10, pady=2)
        valueSensEnergieActive = Label(registreFrame, textvariable = SENSNRJ, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueSensEnergieActive.grid(row=6, column=1, sticky=W, padx=10, pady=2)

        global TARIFF
        TARIFF = StringVar()
        labelTarifEnCoursF = Label(registreFrame, text="Tarif en cours sur le contrat fourniture : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTarifEnCoursF.grid(row=7, column=0, sticky=E, padx=10, pady=2)
        valueTarifEnCoursF = Label(registreFrame, textvariable = TARIFF, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTarifEnCoursF.grid(row=7, column=1, sticky=W, padx=10, pady=2)

        global TARIFD
        TARIFD = StringVar()
        labelTarifEnCoursD = Label(registreFrame, text="Tarif en cours sur le contrat distributeur : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelTarifEnCoursD.grid(row=8, column=0, sticky=E, padx=10, pady=2)
        valueTarifEnCoursD = Label(registreFrame, textvariable = TARIFD, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueTarifEnCoursD.grid(row=8, column=1, sticky=W, padx=10, pady=2)

        global HORLOGE
        HORLOGE = StringVar()
        labelHorlogeDegradee = Label(registreFrame, text="Mode dégradée de l’horloge : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelHorlogeDegradee.grid(row=9, column=0, sticky=E, padx=10, pady=2)
        valueHorlogeDegradee = Label(registreFrame, textvariable = HORLOGE, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueHorlogeDegradee.grid(row=9, column=1, sticky=W, padx=10, pady=2)

        global ETATTIC
        ETATTIC = StringVar()
        labelModeTIC = Label(registreFrame, text="État de la sortie télé-information : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelModeTIC.grid(row=10, column=0, sticky=E, padx=10, pady=2)
        valueModeTIC = Label(registreFrame, textvariable = ETATTIC, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueModeTIC.grid(row=10, column=1, sticky=W, padx=10, pady=2)

        global EURIDIS
        EURIDIS = StringVar()
        labelSortieCommEuridis = Label(registreFrame, text="État de la sortie communication Euridis : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelSortieCommEuridis.grid(row=11, column=0, sticky=E, padx=10, pady=2)
        valueSortieCommEuridis = Label(registreFrame, textvariable = EURIDIS, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueSortieCommEuridis.grid(row=11, column=1, sticky=W, padx=10, pady=2)

        global STATCPL
        STATCPL = StringVar()
        labelStatutCPL = Label(registreFrame, text="Statut du CPL : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelStatutCPL.grid(row=12, column=0, sticky=E, padx=10, pady=2)
        valueStatutCPL = Label(registreFrame, textvariable = STATCPL, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueStatutCPL.grid(row=12, column=1, sticky=W, padx=10, pady=2)

        global SYNCCPL
        SYNCCPL = StringVar()
        labelSynchroCPL = Label(registreFrame, text="Synchronisation CPL : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelSynchroCPL.grid(row=13, column=0, sticky=E, padx=10, pady=2)
        valueSynchroCPL = Label(registreFrame, textvariable = SYNCCPL, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueSynchroCPL.grid(row=13, column=1, sticky=W, padx=10, pady=2)

        global TEMPOJOUR
        TEMPOJOUR = StringVar()
        labelCouleurTempoJour = Label(registreFrame, text="Couleur du jour pour le contrat historique tempo : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelCouleurTempoJour.grid(row=14, column=0, sticky=E, padx=10, pady=2)
        valueCouleurTempoJour = Label(registreFrame, textvariable = TEMPOJOUR, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueCouleurTempoJour.grid(row=14, column=1, sticky=W, padx=10, pady=2)

        global TEMPODEMAIN
        TEMPODEMAIN = StringVar()
        labelCouleurTempoDemain = Label(registreFrame, text="Couleur du lendemain pour le contrat historique tempo : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelCouleurTempoDemain.grid(row=15, column=0, sticky=E, padx=10, pady=2)
        valueCouleurTempoDemain = Label(registreFrame, textvariable = TEMPODEMAIN, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valueCouleurTempoDemain.grid(row=15, column=1, sticky=W, padx=10, pady=2)

        global PREAVISPOINTE
        PREAVISPOINTE = StringVar()
        labelPreavisPointesMobiles = Label(registreFrame, text="Préavis pointes mobiles : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelPreavisPointesMobiles.grid(row=16, column=0, sticky=E, padx=10, pady=2)
        valuePreavisPointesMobiles = Label(registreFrame, textvariable = PREAVISPOINTE, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePreavisPointesMobiles.grid(row=16, column=1, sticky=W, padx=10, pady=2)

        global POINTEMOBILE
        POINTEMOBILE = StringVar()
        labelPointeMobile = Label(registreFrame, text="Pointe mobile (PM) : ", font=(textFont,textSizeSmall,"bold"), relief=FLAT, bg=labelBg, fg=labelColor)
        labelPointeMobile.grid(row=17, column=0, sticky=E, padx=10, pady=2)
        valuePointeMobile = Label(registreFrame, textvariable = POINTEMOBILE, font=(textFont,textSizeSmall), relief=FLAT, bg=labelBg, fg=labelColor)
        valuePointeMobile.grid(row=17, column=1, sticky=W, padx=10, pady=2)


#===============================================================================
#=== Etat général du système                                                 ===
#===============================================================================
def refreshStatus():

    global analysedDict

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
        img2=PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi4.png")
    elif forceValue >= 50 :
        img2=PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi3.png")
    elif forceValue >= 25 :
        img2=PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi2.png")
    elif forceValue > 0 :
        img2=PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi1.png")
    else :
        img2=PhotoImage(master=master, file=config.get('PATH','iconPath') + "/wifi0.png")

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

    #Etat de la DB
    cmd = "ps aux|grep 'LinkyRPiDB.py'|grep -v grep|awk '{print $2}'"
    result = subprocess.run(cmd,stdout=subprocess.PIPE,shell=True).stdout.decode('utf-8')#    if trameDict["DBSTATE"] :
    if result == '' :
        valueDB.config(fg="red")
        DBSTATE.set("Not runnung")
    else :
        valueDB.config(fg="green")
        DBSTATE.set("Running, PID = " + result.rstrip("\n"))

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
    if "CouleurTempoJour" in analysedDict :
        TEMPOJOUR.set(analysedDict["CouleurTempoJour"])
    if "CouleurTempoDemain" in analysedDict :
        TEMPODEMAIN.set(analysedDict["CouleurTempoDemain"])
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
    if "PeriodeTarifaireEnCours" in analysedDict :
        if analysedDict["PeriodeTarifaireEnCours"] == 'HC' :
            HPHCIcon.configure(image=voyantHC)
            HPHCIcon.image=voyantHC

        elif analysedDict["PeriodeTarifaireEnCours"] == 'HP' :
            HPHCIcon.configure(image=voyantHP)
            HPHCIcon.image=voyantHP

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
    if analysedDict["TarifSouscrit"] in ["Tempo","EJP"] :
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

    if "IndexBase" in analysedDict :
        valueIndex = int(analysedDict["IndexBase"]) / 1000
        BASE.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex1" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex1"]) / 1000
        IndexHCB.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex2" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex2"]) / 1000
        IndexHPB.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex3" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex3"]) / 1000
        IndexHCH.set("{:,}".format(valueIndex))

    if "EnergieActiveSoutireeDistributeurIndex4" in analysedDict :
        valueIndex = int(analysedDict["EnergieActiveSoutireeDistributeurIndex4"]) / 1000
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

global canvas
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
        trameReceived = False

    if trameReceived :

        #On initialise la UI (seulement à réception de la 1ere trame)
        if not initUI :
            initGUI(analysedDict)
            refreshStatus()
            refreshIndex()
            refreshPlages()
            initUI = True

        refreshTension(analysedDict)
        refreshRelais(analysedDict)

        # Mise à jour de l'heure affichée
        if "DateHeureLinky" in analysedDict :
            DATE.set(analysedDict["DateHeureLinky"])

        # Trace de la courbe d'intensité pour compteur monophasé
        if "IntensiteInstantanee" in analysedDict :
            iMax = analysedDict["IntensiteSouscrite"] * 5
            IINST.set("Phase 1 : " + str(analysedDict["IntensiteInstantanee"]) + " A")
            coords, newListe = intensite(analysedDict["IntensiteInstantanee"], liste, xscale, iMax)

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

        # Trace de la courbe d'intensité pour compteur triphasé (phase 1)
        if "IntensiteInstantaneePhase1" in analysedDict :
            iMax = analysedDict["IntensiteInstantaneePhase1"] * 5 / 3
            IINST1.set("Phase 1 : " + str(analysedDict["IntensiteInstantaneePhase1"]) + " A")
            coords, newListe = intensite(analysedDict["IntensiteInstantaneePhase1"], liste, xscale, iMax)

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

        # Trace de la courbe d'intensité pour compteur triphasé (phase 2)
        if "IntensiteInstantaneePhase2" in analysedDict :
            iMax = analysedDict["IntensiteInstantaneePhase2"] * 5 / 3
            IINST2.set("Phase 2 : " + str(analysedDict["IntensiteInstantaneePhase2"]) + " A")
            coords, newListe = intensite(analysedDict["IntensiteInstantaneePhase2"], liste, xscale, iMax)

            liste = []
            liste = newListe
            # On efface la courbe
            if len(liste) > 2 :
                #canvas.pack(expand=YES, fill=BOTH)
                canvas.delete(courbeP)

            #Et on la recrée
            if len(liste) > 1 :
                #canvas.pack(expand=YES, fill=BOTH)
                courbeP = canvas.create_line(fill=colorPhase2, *coords)

        # Trace de la courbe d'intensité pour compteur triphasé (phase 3)
        if "IntensiteInstantaneePhase3" in analysedDict :
            iMax = analysedDict["IntensiteInstantaneePhase3"] * 5 / 3
            IINST3.set("Phase 3 : " + str(analysedDict["IntensiteInstantaneePhase3"]) + " A")
            coords, newListe = intensite(analysedDict["IntensiteInstantaneePhase3"], liste, xscale, iMax)

            liste = []
            liste = newListe
            # On efface la courbe
            if len(liste) > 2 :
                #canvas.pack(expand=YES, fill=BOTH)
                canvas.delete(courbeP)

            #Et on la recrée
            if len(liste) > 1 :
                #canvas.pack(expand=YES, fill=BOTH)
                courbeP = canvas.create_line(fill=colorPhase3, *coords)





    # Et on provoque le refresh de la GUI
    master.update_idletasks()
    master.update()
