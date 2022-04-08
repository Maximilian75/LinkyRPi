#===============================================================================
#=== Détermination du type de compteur sur base de la valeur ADCO/ADSC       ===
#===============================================================================
def detCptType(cptAddress):

    if cptAddress[4:6] == "61":
        cptName = "61 - Compteur monophasé 60 A généralisation Linky G3 \n Arrivée puissance haute - Millesime 20" + cptAddress[2:4]
        cptType = "MONO"
    elif cptAddress[4:6] == "62":
        cptName = "62 - Compteur monophasé 90 A généralisation Linky G1 \n Arrivée puissance basse - Millesime 20" + cptAddress[2:4]
        cptType = "MONO"
    elif cptAddress[4:6] == "63":
        cptName = "63 - Compteur triphasé 60 A généralisation Linky G1 \n Arrivée puissance basse - Millesime 20" + cptAddress[2:4]
        cptType = "TRI"
    elif cptAddress[4:6] == "64":
        cptName = "64 - Compteur monophasé 60 A généralisation Linky G3 \n Arrivée puissance basse - Millesime 20" + cptAddress[2:4]
        cptType = "MONO"
    elif cptAddress[4:6] == "70":
        cptName = "70 - Compteur monophasé Linky 60 A \n Mise au point G3 - Millesime 20" + cptAddress[2:4]
        cptType = "MONO"
    elif cptAddress[4:6] == "71":
        cptName = "71 - Compteur triphasé Linky 60 A \n Mise au point G3 - Millesime 20" + cptAddress[2:4]
        cptType = "TRI"
    elif cptAddress[4:6] == "75":
        cptName = "75 - Compteur monophasé 90 A généralisation Linky G3 \n Arrivée puissance basse - Millesime 20" + cptAddress[2:4]
        cptType = "MONO"
    elif cptAddress[4:6] == "76":
        cptName = "76 - Compteur triphasé 60 A généralisation Linky G3 \n Arrivée puissance basse - Millesime 20" + cptAddress[2:4]
        cptType = "TRI"
    else :
        cptName = (cptAddress[4:6] + " - Modèle de compteur non référencé \n Enedis-NOI-CPT_54E - Millesime 20" + cptAddress[2:4])
        cptType = ""

    return cptType, cptName;



#===============================================================================
#=== Analyse du RELAIS                                                       ===
#===============================================================================
# Voir découpage dans la doc Enedis-NOI-CPT_54E.pdf

def analyseRelais(relaisValue):

    s = "{0:{fill}8b}".format(int(relaisValue), fill='0')

    return s



#===============================================================================
#=== Analyse du REGISTRE                                                     ===
#===============================================================================
# Voir découpage dans la doc Enedis-NOI-CPT_54E.pdf

def analyseRegistre(registreValue):
    registre = {}

    #Conversion de la valeur ASCII en string binaire
    s = "{0:{fill}32b}".format(int(registreValue, 16), fill='0')

    if s[0] == "0" :
        registre.update({"ContactSec":"Fermé"})
    else :
        registre.update({"ContactSec":"Ouvert"})

    if int(s[1:4], 2) == 0 :
        registre.update({"OrganeDeCoupure":"Fermé"})
    elif int(s[1:4], 2) == 1 :
        registre.update({"OrganeDeCoupure":"Ouvert sur surpuissance"})
    elif int(s[1:4], 2) == 2 :
        registre.update({"OrganeDeCoupure":"Ouvert sur surtension"})
    elif int(s[1:4], 2) == 3 :
        registre.update({"OrganeDeCoupure":"Ouvert sur délestage"})
    elif int(s[1:4], 2) == 4 :
        registre.update({"OrganeDeCoupure":"Ouvert sur ordre CPL ou Euridis"})
    elif int(s[1:4], 2) == 5 :
        registre.update({"OrganeDeCoupure":"Ouvert sur une surchauffe avec une valeur du courant supérieure au courant de commutation maximal"})
    elif int(s[1:4], 2) == 6 :
        registre.update({"OrganeDeCoupure":"Ouvert sur une surchauffe avec une valeur de courant inférieure au courant de commutation maximal"})
    else :
        registre.update({"OrganeDeCoupure":"Statut inconnu : " + s[1:4]})

    if s[4] == "0" :
        registre.update({"CacheBorneDistributeur":"Fermé"})
    else :
        registre.update({"CacheBorneDistributeur":"Ouvert"})

    if s[6] == "0" :
        registre.update({"SurtensionPhase":"Non"})
    else :
        registre.update({"SurtensionPhase":"Oui"})

    if s[7] == "0" :
        registre.update({"DepassementPuissanceRef":"Non"})
    else :
        registre.update({"DepassementPuissanceRef":"Oui"})

    if s[8] == "0" :
        registre.update({"Fonctionnement":"Consommateur"})
    else :
        registre.update({"Fonctionnement":"Producteur"})

    if s[9] == "0" :
        registre.update({"SensEnergieActive":"Positive"})
    else :
        registre.update({"SensEnergieActive":"Négative"})

    if int(s[10:14], 2) == 0 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 1"})
    elif int(s[10:14], 2) == 1 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 2"})
    elif int(s[10:14], 2) == 2 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 3"})
    elif int(s[10:14], 2) == 3 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 4"})
    elif int(s[10:14], 2) == 4 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 5"})
    elif int(s[10:14], 2) == 5 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 6"})
    elif int(s[10:14], 2) == 6 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 7"})
    elif int(s[10:14], 2) == 7 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 8"})
    elif int(s[10:14], 2) == 8 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 9"})
    elif int(s[10:14], 2) == 9 :
        registre.update({"TarifEnCoursF":"Energie ventilée sur Index 10"})
    else :
        registre.update({"TarifEnCoursF":"Tarif inconnu : " + s[10:14]})

    if int(s[14:16], 2) == 0 :
        registre.update({"TarifEnCoursD":"Energie ventilée sur Index 1"})
    elif int(s[14:16], 2) == 1 :
        registre.update({"TarifEnCoursD":"Energie ventilée sur Index 2"})
    elif int(s[14:16], 2) == 2 :
        registre.update({"TarifEnCoursD":"Energie ventilée sur Index 3"})
    elif int(s[14:16], 2) == 3 :
        registre.update({"TarifEnCoursD":"Energie ventilée sur Index 4"})
    else :
        registre.update({"TarifEnCoursD":"Tarif inconnu : " + s[14:16]})

    if s[16] == "0" :
        registre.update({"HorlogeDegradee":"Horloge correcte"})
    else :
        registre.update({"HorlogeDegradee":"Horloge en mode dégradée"})

    if s[17] == "0" :
        registre.update({"ModeTIC":"Historique"})
    else :
        registre.update({"ModeTIC":"Standard"})

    if s[19:21] == "00" :
        registre.update({"SortieCommEuridis":"Désactivée"})
    elif s[19:21] == "01" :
        registre.update({"SortieCommEuridis":"Activée sans sécurité"})
    elif s[19:21] == "11" :
        registre.update({"SortieCommEuridis":"Activée avec sécurité"})
    else :
        registre.update({"SortieCommEuridis":"Statut inconnu : " + s[14:16]})

    if s[21:23] == "00" :
        registre.update({"StatutCPL":"New/Unlock"})
    elif s[21:23] == "01" :
        registre.update({"StatutCPL":"New/Lock"})
    elif s[21:23] == "10" :
        registre.update({"StatutCPL":"Registered"})
    else :
        registre.update({"StatutCPL":"Statut inconnu : " + s[14:16]})

    if s[23] == "0" :
        registre.update({"SynchroCPL":"Non synchronisé"})
    else :
        registre.update({"SynchroCPL":"Synchronisé"})

    if int(s[24:26], 2) == 0 :
        registre.update({"CouleurTempoJour":"Pas d'annonce"})
    elif int(s[24:26], 2) == 1 :
        registre.update({"CouleurTempoJour":"Bleu"})
    elif int(s[24:26], 2) == 2 :
        registre.update({"CouleurTempoJour":"Blanc"})
    elif int(s[24:26], 2) == 3 :
        registre.update({"CouleurTempoJour":"Rouge"})
    else :
        registre.update({"CouleurTempoJour":"Statut inconnu : " + s[24:26]})

    if int(s[26:28], 2) == 0 :
        registre.update({"CouleurTempoDemain":"Pas d'annonce"})
    elif int(s[26:28], 2) == 1 :
        registre.update({"CouleurTempoDemain":"Bleu"})
    elif int(s[26:28], 2) == 2 :
        registre.update({"CouleurTempoDemain":"Blanc"})
    elif int(s[26:28], 2) == 3 :
        registre.update({"CouleurTempoDemain":"Rouge"})
    else :
        registre.update({"CouleurTempoDemain":"Statut inconnu : " + s[26:28]})

    if int(s[28:30], 2) == 0 :
        registre.update({"PreavisPointesMobiles":"Pas de préavis en cours"})
    elif int(s[28:30], 2) == 1 :
        registre.update({"PreavisPointesMobiles":"Préavis PM1 en cours"})
    elif int(s[28:30], 2) == 2 :
        registre.update({"PreavisPointesMobiles":"Préavis PM2 en cours"})
    elif int(s[28:30], 2) == 3 :
        registre.update({"PreavisPointesMobiles":"Préavis PM3 en cours"})
    else :
        registre.update({"PreavisPointesMobiles":"Statut inconnu : " + s[28:30]})

    if int(s[30:33], 2) == 0 :
        registre.update({"PointeMobile":"Pas de pointe mobile"})
    elif int(s[30:33], 2) == 1 :
        registre.update({"PointeMobile":"PM1 en cours"})
    elif int(s[30:33], 2) == 2 :
        registre.update({"PointeMobile":"PM2 en cours"})
    elif int(s[30:33], 2) == 3 :
        registre.update({"PointeMobile":"PM3 en cours"})
    else :
        registre.update({"PointeMobile":"Statut inconnu : " + s[30:33]})

    return registre




#===============================================================================
#=== Analyse du dictionnaire contenant la trame reçue                        ===
#===============================================================================
# Le but de cela est d'avoir un dictionnaire qui soit agnostique du mode de la TIC

def analyseTrame(trameDict):
    consoTotale = 0
    analysedDict = {}

    #Analyse du Registre (mode standard only)
    if "STGE" in trameDict :
        registreDict = analyseRegistre(trameDict["STGE"])
        analysedDict.update({"ContactSec":registreDict["ContactSec"]})
        analysedDict.update({"OrganeDeCoupure":registreDict["OrganeDeCoupure"]})
        analysedDict.update({"CacheBorneDistributeur":registreDict["CacheBorneDistributeur"]})
        analysedDict.update({"SurtensionPhase":registreDict["SurtensionPhase"]})
        analysedDict.update({"DepassementPuissanceRef":registreDict["DepassementPuissanceRef"]})
        analysedDict.update({"Fonctionnement":registreDict["Fonctionnement"]})
        analysedDict.update({"SensEnergieActive":registreDict["SensEnergieActive"]})
        analysedDict.update({"TarifEnCoursF":registreDict["TarifEnCoursF"]})
        analysedDict.update({"TarifEnCoursD":registreDict["TarifEnCoursD"]})
        analysedDict.update({"HorlogeDegradee":registreDict["HorlogeDegradee"]})
        analysedDict.update({"SortieCommEuridis":registreDict["SortieCommEuridis"]})
        analysedDict.update({"StatutCPL":registreDict["StatutCPL"]})
        analysedDict.update({"SynchroCPL":registreDict["SynchroCPL"]})
        analysedDict.update({"CouleurTempoJour":registreDict["CouleurTempoJour"]})
        analysedDict.update({"CouleurTempoDemain":registreDict["CouleurTempoDemain"]})
        analysedDict.update({"PreavisPointesMobiles":registreDict["PreavisPointesMobiles"]})
        analysedDict.update({"PointeMobile":registreDict["PointeMobile"]})
        analysedDict.update({"ModeTIC":registreDict["ModeTIC"]})
    elif "TICMODE" in trameDict :
        if trameDict["TICMODE"] == "STD" :
            analysedDict.update({"ModeTIC":"Historique"})
        else :
            analysedDict.update({"ModeTIC":"Standard"})

    #Message de service "état de la DB" provenant du listener
    if "DBSTATE" in trameDict :
        if trameDict["DBSTATE"] :
            analysedDict.update({"etatDB":"En ligne"})
        else :
            analysedDict.update({"etatDB":"Hors ligne"})

    #Adresse du compteur
    if "ADCO" in trameDict :
        analysedDict.update({"AdresseCompteur":trameDict["ADCO"]})
        cptType, cptName = detCptType(trameDict["ADCO"])
        analysedDict.update({"TypeCompteur":cptType})
        analysedDict.update({"NomCompteur":cptName})
    elif "ADSC" in trameDict :
        analysedDict.update({"AdresseCompteur":trameDict["ADSC"]})
        cptType, cptName = detCptType(trameDict["ADSC"])
        analysedDict.update({"TypeCompteur":cptType})
        analysedDict.update({"NomCompteur":cptName})
    else :
        cptType = ""
        cptName = ""

    #Avertissement de Dépassement de Puissance Souscrite
    if "ADIR" in trameDict :
        analysedDict.update({"DepassementPuissance":trameDict["ADIR"]})

    #Avertissement de Dépassement d'intensité de réglage phase 1
    if "ADIR1" in trameDict :
        analysedDict.update({"DepassementPuissancePhase1":trameDict["ADIR1"]})

    #Avertissement de Dépassement d'intensité de réglage phase 2
    if "ADIR2" in trameDict :
        analysedDict.update({"DepassementPuissancePhase2":trameDict["ADIR2"]})

    #Avertissement de Dépassement d'intensité de réglage phase 3
    if "ADIR3" in trameDict :
        analysedDict.update({"DepassementPuissancePhase3":trameDict["ADIR3"]})

    #Couleur du lendemain (abonnement TEMPO)
    if "DEMAIN" in trameDict :
        analysedDict.update({"CouleurDemain":trameDict["DEMAIN"]})
    elif "STGE" in trameDict :
        analysedDict.update({"CouleurDemain":registreDict["CouleurTempoDemain"]})


    #Options tarifaires mode historique ("BASE" / "EJP." / "HC.." / "TEMP") et indexes associés
    if "OPTARIF" in trameDict :
        if trameDict["OPTARIF"] == "BASE" :
            analysedDict.update({"TarifSouscrit":"Tarif de base"})
            if "BASE" in trameDict :
                analysedDict.update({"IndexBase":int(trameDict["BASE"])})
                analysedDict.update({"IndexTotal":int(trameDict["BASE"])})
        elif trameDict["OPTARIF"] == "HC.." :
            analysedDict.update({"TarifSouscrit":"Heures Creuses"})
            consoTotale = 0
            if "HCHC" in trameDict :
                analysedDict.update({"IndexHC":int(trameDict["HCHC"])})
                consoTotale = consoTotale + int(trameDict["HCHC"])
            if "HCHP" in trameDict :
                analysedDict.update({"IndexHP":trameDict["HCHP"]})
                consoTotale = consoTotale + int(trameDict["HCHP"])
            analysedDict.update({"IndexTotal":consoTotale})
        elif trameDict["OPTARIF"] == "EJP." :
            analysedDict.update({"TarifSouscrit":"EJP"})
            consoTotale = 0
            if "EJPHN" in trameDict :
                analysedDict.update({"IndexEJPNormale":trameDict["EJPHN"]})
                consoTotale = consoTotale + int(trameDict["EJPHN"])
            if "EJPHPM" in trameDict :
                analysedDict.update({"IndexEJPPointe":int(trameDict["EJPHPM"])})
                consoTotale = consoTotale + int(trameDict["EJPHPM"])
            analysedDict.update({"IndexTotal":consoTotale})
        elif trameDict["OPTARIF"] == "TEMPO" :
            analysedDict.update({"TarifSouscrit":"Tempo"})
            consoTotale = 0
            if "BBRHCJB" in trameDict :
                analysedDict.update({"IndexHCJB":int(trameDict["BBRHCJB"])})
                consoTotale = consoTotale + int(trameDict["BBRHCJB"])
            if "BBRHCJW" in trameDict :
                analysedDict.update({"IndexHCJW":int(trameDict["BBRHCJW"])})
                consoTotale = consoTotale + int(trameDict["BBRHCJW"])
            if "BBRHCJR" in trameDict :
                analysedDict.update({"IndexHCJR":int(trameDict["BBRHCJR"])})
                consoTotale = consoTotale + int(trameDict["BBRHCJR"])
            if "BBRHPJB" in trameDict :
                analysedDict.update({"IndexHCPB":int(trameDict["BBRHPJB"])})
                consoTotale = consoTotale + int(trameDict["BBRHPJB"])
            if "BBRHPJW" in trameDict :
                analysedDict.update({"IndexHPJW":int(trameDict["BBRHPJW"])})
                consoTotale = consoTotale + int(trameDict["BBRHPJW"])
            if "BBRHPJR" in trameDict :
                analysedDict.update({"IndexHPJR":int(trameDict["BBRHCPR"])})
                consoTotale = consoTotale + int(trameDict["BBRHPJR"])
            analysedDict.update({"IndexTotal":consoTotale})

    #Options tarifaires mode standard ("BASE" / "?" / "H PLEINE/CREUSE" / "?" / "PRODUCTEUR") et indexes associés
    elif "NGTF" in trameDict :
        if trameDict["NGTF"].strip() == "BASE" :
            analysedDict.update({"TarifSouscrit":"Tarif de base"})
            analysedDict.update({"PeriodeTarifaireEnCours":"TH"})   #Toutes Heures (option BASE)
            if  "EAST" in trameDict :
                analysedDict.update({"IndexBase":int(trameDict["EAST"])})
                analysedDict.update({"IndexTotal":int(trameDict["EAST"])})

        elif trameDict["NGTF"].strip() == "H PLEINE/CREUSE" :
            analysedDict.update({"TarifSouscrit":"Heures Creuses"})
            consoTotale = 0
            if "EASF01" in trameDict :
                analysedDict.update({"IndexHC":int(trameDict["EASF01"])})
                consoTotale = consoTotale + int(trameDict["EASF01"])
            if "EASF02" in trameDict :
                analysedDict.update({"IndexHP":int(trameDict["EASF02"])})
                consoTotale = consoTotale + int(trameDict["EASF02"])
            if  "EAST" in trameDict :
                analysedDict.update({"IndexTotal":int(trameDict["EAST"])})
            if "NTARF" in trameDict :
                if trameDict["NTARF"] == "01" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HC"})
                elif trameDict["NTARF"] == "02" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HP"})
                else :
                    analysedDict.update({"PeriodeTarifaireEnCours":trameDict["NTARF"]})

        elif trameDict["NGTF"].strip() == "HC et Week-End" :
            analysedDict.update({"TarifSouscrit":"Heures Creuses et Week-end"})
            consoTotale = 0
            if "EASF01" in trameDict :
                analysedDict.update({"IndexHC":int(trameDict["EASF01"])})
                consoTotale = consoTotale + int(trameDict["EASF01"])
            if "EASF02" in trameDict :
                analysedDict.update({"IndexHP":int(trameDict["EASF02"])})
                consoTotale = consoTotale + int(trameDict["EASF02"])
            if "EASF03" in trameDict :
                analysedDict.update({"IndexWE":int(trameDict["EASF03"])})
                consoTotale = consoTotale + int(trameDict["EASF03"])
            if  "EAST" in trameDict :
                analysedDict.update({"IndexTotal":int(trameDict["EAST"])})
            if "NTARF" in trameDict :
                if trameDict["NTARF"] == "01" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HC"})
                elif trameDict["NTARF"] == "02" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HP"})
                else :
                    analysedDict.update({"PeriodeTarifaireEnCours":trameDict["NTARF"]})

        elif trameDict["NGTF"].strip() == "EJP" :
            analysedDict.update({"TarifSouscrit":"EJP"})
            consoTotale = 0
            if "EASF01" in trameDict :
                analysedDict.update({"IndexEJPNormale":int(trameDict["EASF01"])})
                consoTotale = consoTotale + int(trameDict["EASF01"])
            if "EASF02" in trameDict :
                analysedDict.update({"IndexEJPPointe":int(trameDict["EASF02"])})
                consoTotale = consoTotale + int(trameDict["EASF02"])
            if  "EAST" in trameDict :
                analysedDict.update({"IndexTotal":int(trameDict["EAST"])})
            if "NTARF" in trameDict :
                if trameDict["NTARF"] == "01" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HN"})
                elif trameDict["NTARF"] == "02" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"PM"})
                else :
                    analysedDict.update({"PeriodeTarifaireEnCours":trameDict["NTARF"]})

        elif trameDict["NGTF"].strip() == "TEMPO" :
            analysedDict.update({"TarifSouscrit":"Tempo"})
            consoTotale = 0
            if "EASF01" in trameDict :
                analysedDict.update({"IndexHCJB":int(trameDict["EASF01"])})
                consoTotale = consoTotale + int(trameDict["EASF01"])
            if "EASF03" in trameDict :
                analysedDict.update({"IndexHCJW":int(trameDict["EASF03"])})
                consoTotale = consoTotale + int(trameDict["EASF03"])
            if "EASF05" in trameDict :
                analysedDict.update({"IndexHCJR":int(trameDict["EASF05"])})
                consoTotale = consoTotale + int(trameDict["EASF05"])
            if "EASF02" in trameDict :
                analysedDict.update({"IndexHCPB":int(trameDict["EASF02"])})
                consoTotale = consoTotale + int(trameDict["EASF02"])
            if "EASF04" in trameDict :
                analysedDict.update({"IndexHPJW":int(trameDict["EASF04"])})
                consoTotale = consoTotale + int(trameDict["EASF04"])
            if "EASF06" in trameDict :
                analysedDict.update({"IndexHPJR":int(trameDict["EASF06"])})
                consoTotale = consoTotale + int(trameDict["EASF06"])
            analysedDict.update({"IndexTotal":int(trameDict["EAST"])})
            if "NTARF" in trameDict :
                if trameDict["NTARF"] == "01" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HCJB"})
                elif trameDict["NTARF"] == "02" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HPJB"})
                elif trameDict["NTARF"] == "03" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HCJW"})
                elif trameDict["NTARF"] == "04" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HPJW"})
                elif trameDict["NTARF"] == "05" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HCJR"})
                elif trameDict["NTARF"] == "06" :
                    analysedDict.update({"PeriodeTarifaireEnCours":"HCJR"})
                else :
                    analysedDict.update({"PeriodeTarifaireEnCours":trameDict["NTARF"]})

        else :
            analysedDict.update({"TarifSouscrit":trameDict["NGTF"].strip()})

        if "EASF07" in trameDict :
            analysedDict.update({"Index07":int(trameDict["EASF07"])})

        if "EASF08" in trameDict :
            analysedDict.update({"Index08":int(trameDict["EASF08"])})

        if "EASF09" in trameDict :
            analysedDict.update({"Index09":int(trameDict["EASF09"])})

        if "EASF10" in trameDict :
            analysedDict.update({"Index10":int(trameDict["EASF10"])})

    if "PTARF" in trameDict :
        analysedDict.update({"PTARF":trameDict["PTARF"]})


    #Horaire Heures Pleines Heures Creuses
    if "HHPHC" in trameDict :
        analysedDict.update({"HorairesHC":trameDict["HHPHC"]})
    elif "PJOURF+1" in trameDict :
        listPJOUR = trameDict["PJOURF+1"].split()
        if listPJOUR[0] == "NONUTILE" :
            analysedDict.update({"HorairesHC":""})
        else :
            if (listPJOUR[1] != "NONUTILE") and (listPJOUR[2] != "NONUTILE") :
                plageHoraire1 = listPJOUR[1][0:2] + ":" + listPJOUR[1][2:4] + " - " + listPJOUR[2][0:2] + ":" + listPJOUR[2][2:4]
            else :
                plageHoraire1 = ""
            if (listPJOUR[3] != "NONUTILE") and (listPJOUR[4] != "NONUTILE") :
                plageHoraire2 = "  /  " + listPJOUR[3][0:2] + ":" + listPJOUR[3][2:4] + " - " + listPJOUR[4][0:2] + ":" + listPJOUR[4][2:4]
            else :
                plageHoraire2 = ""
            if (listPJOUR[5] != "NONUTILE") and (listPJOUR[6] != "NONUTILE") :
                plageHoraire3 = "  /  " + listPJOUR[5][0:2] + ":" + listPJOUR[5][2:4] + " - " + listPJOUR[6][0:2] + ":" + listPJOUR[6][2:4]
            else :
                plageHoraire3 = ""
            if (listPJOUR[7] != "NONUTILE") and (listPJOUR[8] != "NONUTILE") :
                plageHoraire4 = "  /  " + listPJOUR[7][0:2] + ":" + listPJOUR[7][2:4] + " - " + listPJOUR[8][0:2] + ":" + listPJOUR[8][2:4]
            else :
                plageHoraire4 = ""
            if (listPJOUR[9] != "NONUTILE") and (listPJOUR[10] != "NONUTILE") :
                plageHoraire5 = "  /  " + listPJOUR[9][0:2] + ":" + listPJOUR[9][2:4] + " - " + listPJOUR[10][0:2] + ":" + listPJOUR[10][2:4]
            else :
                plageHoraire5 = ""
            analysedDict.update({"HorairesHC":plageHoraire1 + plageHoraire2 + plageHoraire3 + plageHoraire4 + plageHoraire5})


    #Intensité Instantanée
    if "IINST" in trameDict :
        analysedDict.update({"IntensiteInstantanee":int(trameDict["INST"])})
    elif "IRMS1" in trameDict and cptType == "MONO" :
        analysedDict.update({"IntensiteInstantanee":int(trameDict["IRMS1"])})

    #Intensité Instantanée Phase 1
    if "IINST1" in trameDict :
        analysedDict.update({"IntensiteInstantaneePhase1":int(trameDict["INST1"])})
    elif "IRMS1" in trameDict and cptType == "TRI" :
        analysedDict.update({"IntensiteInstantaneePhase1":int(trameDict["IRMS1"])})

    #Intensité Instantanée Phase 2
    if "IINST2" in trameDict :
        analysedDict.update({"IntensiteInstantaneePhase2":int(trameDict["INST2"])})
    elif "IRMS2" in trameDict :
        analysedDict.update({"IntensiteInstantaneePhase2":int(trameDict["IRMS2"])})

    #Intensité Instantanée Phase 3
    if "IINST3" in trameDict :
        analysedDict.update({"IntensiteInstantaneePhase3":int(trameDict["INST3"])})
    elif "IRMS3" in trameDict :
        analysedDict.update({"IntensiteInstantaneePhase3":int(trameDict["IRMS3"])})

    #Intensité maximale appelée
    if "IMAX" in trameDict :
        analysedDict.update({"IntensiteMax":int(trameDict["IMAX"])})
    elif "SMAXSN" in trameDict and "URMS1" in trameDict :
        analysedDict.update({"IntensiteMax":int(trameDict["SMAXSN"]) / int(trameDict["URMS1"])})

    #Intensité maximale appelée Phase 1
    if "IMAX1" in trameDict :
        analysedDict.update({"IntensiteMaxPhase1":int(trameDict["IMAX1"])})
    elif "SMAXSN1" in trameDict and "URMS1" in trameDict :
        analysedDict.update({"IntensiteMaxPhase1":int(trameDict["SMAXSN1"]) / int(trameDict["URMS1"])})

    #Intensité maximale appelée Phase 2
    if "IMAX2" in trameDict :
        analysedDict.update({"IntensiteMaxPhase2":int(trameDict["IMAX2"])})
    elif "SMAXSN2" in trameDict and "URMS2" in trameDict :
        analysedDict.update({"IntensiteMaxPhase2":int(trameDict["SMAXSN2"]) / int(trameDict["URMS2"])})

    #Intensité maximale appelée Phase 3
    if "IMAX3" in trameDict :
        analysedDict.update({"IntensiteMaxPhase3":int(trameDict["IMAX3"])})
    elif "SMAXSN3" in trameDict and "URMS3" in trameDict :
        analysedDict.update({"IntensiteMaxPhase3":int(trameDict["SMAXSN3"]) / int(trameDict["URMS3"])})

    #Mot d'état du compteur
    if "MOTDETAT" in trameDict :
        analysedDict.update({"MotEtat":trameDict["MOTDETAT"]})

    #Option tarifaire choisie
    if "ISOUSC" in trameDict :
        analysedDict.update({"IntensiteSouscrite":int(trameDict["ISOUSC"]) / 5})
    elif "PREF" in trameDict :
        analysedDict.update({"IntensiteSouscrite":int(trameDict["PREF"])})

    #Période Tarifaire en cours
    if "PTEC" in trameDict :
        if trameDict["PTEC"] == "TH.." :
            analysedDict.update({"PeriodeTarifaireEnCours":"TH"})   #Toutes Heures (option BASE)
        elif trameDict["PTEC"] == "HC.." :
            analysedDict.update({"PeriodeTarifaireEnCours":"HC"})   #Heures Creuses
        elif trameDict["PTEC"] == "HP.." :
            analysedDict.update({"PeriodeTarifaireEnCours":"HP"})   #Heures Pleines
        elif trameDict["PTEC"] == "HN.." :
            analysedDict.update({"PeriodeTarifaireEnCours":"HN"})   #Heures Normales (EJP)
        elif trameDict["PTEC"] == "PM.." :
            analysedDict.update({"PeriodeTarifaireEnCours":"PM"})   #Heures de Pointe Mobile (EJP)
        elif trameDict["PTEC"] == "HCJB" :
            analysedDict.update({"CouleurTempoJour":registreDict["CouleurTempoJour"]})
            analysedDict.update({"PeriodeTarifaireEnCours":trameDict["PTEC"]})
        elif trameDict["PTEC"] == "HCJW" :
            analysedDict.update({"CouleurTempoJour":registreDict["CouleurTempoJour"]})
            analysedDict.update({"PeriodeTarifaireEnCours":trameDict["PTEC"]})
        elif trameDict["PTEC"] == "HCJR" :
            analysedDict.update({"CouleurTempoJour":registreDict["CouleurTempoJour"]})
            analysedDict.update({"PeriodeTarifaireEnCours":trameDict["PTEC"]})
        elif trameDict["PTEC"] == "HPJB" :
            analysedDict.update({"CouleurTempoJour":registreDict["CouleurTempoJour"]})
            analysedDict.update({"PeriodeTarifaireEnCours":trameDict["PTEC"]})
        elif trameDict["PTEC"] == "HPJW" :
            analysedDict.update({"CouleurTempoJour":registreDict["CouleurTempoJour"]})
            analysedDict.update({"PeriodeTarifaireEnCours":trameDict["PTEC"]})
        elif trameDict["PTEC"] == "HPJR" :
            analysedDict.update({"CouleurTempoJour":registreDict["CouleurTempoJour"]})
            analysedDict.update({"PeriodeTarifaireEnCours":trameDict["PTEC"]})


    if "NJOURF" in trameDict :
        analysedDict.update({"NumeroJourCalendrierFournisseur":trameDict["NJOURF"]})

    if "NJOURF+1" in trameDict :
        analysedDict.update({"NumeroProchainJourCalendrierFournisseur":trameDict["NJOURF+1"]})

    if "PJOURF+1" in trameDict :
        analysedDict.update({"ProfilProchainJourCalendrierFournisseur":trameDict["PJOURF+1"]})

    #Préavis Début EJP (30 min)
    if "PEJP" in trameDict :
        analysedDict.update({"ProfilProchainJourPointe":trameDict["PEJP"]})
    elif "PPOINTE" in trameDict :
        analysedDict.update({"ProfilProchainJourPointe":trameDict["PPOINTE"]})


    #Présence des potentiels
    if "PPOT" in trameDict :
        analysedDict.update({"PresenceDesPotentiels":trameDict["PPOT"]})

    #Puissance apparente
    if "PAPP" in trameDict :
        analysedDict.update({"PuissanceApparente":int(trameDict["PAPP"])})
    elif "SINSTS" in trameDict :
        analysedDict.update({"PuissanceApparente":int(trameDict["SINSTS"])})

    if "SINSTS1" in trameDict :
        analysedDict.update({"PuissanceApparentePhase1":int(trameDict["SINSTS1"])})

    if "SINSTS2" in trameDict :
        analysedDict.update({"PuissanceApparentePhase2":int(trameDict["SINSTS2"])})

    if "SINSTS3" in trameDict :
        analysedDict.update({"PuissanceApparentePhase3":int(trameDict["SINSTS3"])})

    #Puissance maximale atteinte
    if "PMAX" in trameDict :
        analysedDict.update({"PuissanceMaxAtteinte":int(trameDict["PMAX"])})
    elif "SMAXSN" in trameDict :
        analysedDict.update({"PuissanceMaxAtteinte":int(trameDict["SMAXSN"])})

    if "SMAXSN1" in trameDict :
        analysedDict.update({"PuissanceMaxAtteintePhase1":int(trameDict["SMAXSN1"])})

    if "SMAXSN2" in trameDict :
        analysedDict.update({"PuissanceMaxAtteintePhase2":int(trameDict["SMAXSN2"])})

    if "SMAXSN3" in trameDict :
        analysedDict.update({"PuissanceMaxAtteintePhase3":int(trameDict["SMAXSN3"])})

    #Date et heure courante (Linky)
    if "DATE" in trameDict :
        analysedDict.update({"DateHeureLinky":trameDict["DATE"][0] + " - " + trameDict["DATE"][5:7] + "/" + trameDict["DATE"][3:5] + "/20" + trameDict["DATE"][1:3] + " - " + trameDict["DATE"][7:9] + ":" + trameDict["DATE"][9:11] + ":" + trameDict["DATE"][11:]})

    #Puissance app max. soutirée n-1
    if "SMAXSN-1" in trameDict :
        analysedDict.update({"PuissanceApparenteMaxN-1":int(trameDict["SMAXSN-1"])})

    if "SMAXSN1-1" in trameDict :
        analysedDict.update({"PuissanceApparenteMaxN-1Phase1":int(trameDict["SMAXSN1-1"])})

    if "SMAXSN2-1" in trameDict :
        analysedDict.update({"PuissanceApparenteMaxN-1Phase2":int(trameDict["SMAXSN2-1"])})

    if "SMAXSN3-1" in trameDict :
        analysedDict.update({"PuissanceApparenteMaxN-1Phase3":int(trameDict["SMAXSN3-1"])})

    #Puissance app. de coupure
    if "PCOUP" in trameDict :
        analysedDict.update({"PuissanceCoupure":int(trameDict["PCOUP"])})

    #Message court
    if "MSG1" in trameDict :
        analysedDict.update({"MessageCourt":trameDict["MSG1"]})

    #Message Ultra court
    if "MSG2" in trameDict :
        analysedDict.update({"MessageUltraCourt":trameDict["MSG2"]})

    #Tensions efficaces
    if "URMS1" in trameDict :
        analysedDict.update({"TensionEfficacePhase1":int(trameDict["URMS1"])})

    if "URMS2" in trameDict :
        analysedDict.update({"TensionEfficacePhase2":int(trameDict["URMS2"])})

    if "URMS3" in trameDict :
        analysedDict.update({"TensionEfficacePhase3":int(trameDict["URMS3"])})

    #Tensions moyennes
    if "UMOY1" in trameDict :
        analysedDict.update({"TensionMoyennePhase1":int(trameDict["UMOY1"])})

    if "UMOY2" in trameDict :
        analysedDict.update({"TensionMoyennePhase2":int(trameDict["UMOY2"])})

    if "UMOY3" in trameDict :
        analysedDict.update({"TensionMoyennePhase3":int(trameDict["UMOY3"])})

    #Version de la TIC
    if "VTIC" in trameDict :
        analysedDict.update({"VersionTIC":trameDict["VTIC"]})

    #Point n de la courbe de charge active soutirée
    if "CCASN" in trameDict :
        analysedDict.update({"PointNCourbeChargeActiveSoutiree":int(trameDict["CCASN"])})

    #Point n-1 de la courbe de charge active soutirée
    if "CCASN-1" in trameDict :
        analysedDict.update({"PointN-1CourbeChargeActiveSoutiree":int(trameDict["CCASN-1"])})

    #Debute et fins de Pointe mobile
    if "DPM1" in trameDict :
        analysedDict.update({"DebutPointeMobile1":trameDict["DPM1"]})

    if "DPM2" in trameDict :
        analysedDict.update({"DebutPointeMobile2":trameDict["DPM2"]})

    if "DPM3" in trameDict :
        analysedDict.update({"DebutPointeMobile3":trameDict["DPM3"]})

    if "FPM1" in trameDict :
        analysedDict.update({"FinPointeMobile1":trameDict["FPM1"]})

    if "FPM2" in trameDict :
        analysedDict.update({"FinPointeMobile2":trameDict["FPM2"]})

    if "FPM3" in trameDict :
        analysedDict.update({"FinPointeMobile3":trameDict["FPM3"]})

    #Energie active soutirée Distributeur
    if "EASD01" in trameDict :
        analysedDict.update({"EnergieActiveSoutireeDistributeurIndex1":int(trameDict["EASD01"])})

    if "EASD02" in trameDict :
        analysedDict.update({"EnergieActiveSoutireeDistributeurIndex2":int(trameDict["EASD02"])})

    if "EASD03" in trameDict :
        analysedDict.update({"EnergieActiveSoutireeDistributeurIndex3":int(trameDict["EASD03"])})

    if "EASD04" in trameDict :
        analysedDict.update({"EnergieActiveSoutireeDistributeurIndex4":int(trameDict["EASD04"])})

    if "PRM" in trameDict :
        analysedDict.update({"PRM":trameDict["PRM"]})

    if "RELAIS" in trameDict :
        relaisValue = analyseRelais(trameDict["RELAIS"])
        analysedDict.update({"Relais":relaisValue})

    return analysedDict
