
#This file is part of LinkyRPi.
#LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
#(c)Copyright Mikaël Masci 2022


#===============================================================================
#=== Constitution des syllabus (dictionnaires de traduction)                 ===
#===============================================================================
def generateSyllabus() :
    syllabus = {}
    dataFormat = {}

    # Correspondances entre les clés de la TIC HISTORIQUE et le dictionnaire traduit
    syllabus.update({"ADCO":"AdresseCompteur"})
    syllabus.update({"OPTARIF":"TarifSouscrit"})
    syllabus.update({"ISOUSC":"IntensiteSouscrite"})
    syllabus.update({"BASE":"Index00"})
    syllabus.update({"HCHC":"Index01"})
    syllabus.update({"HCHP":"Index02"})
    syllabus.update({"EJPHN":"Index01"})
    syllabus.update({"EJPHPM":"Index02"})
    syllabus.update({"BBRHCJB":"Index01"})
    syllabus.update({"BBRHCJW":"Index03"})
    syllabus.update({"BBRHCJR":"Index05"})
    syllabus.update({"BBRHPJB":"Index02"})
    syllabus.update({"BBRHPJW":"Index04"})
    syllabus.update({"BBRHPJR":"Index06"})
    syllabus.update({"PEJP":"ProfilProchainJourPointe"})
    syllabus.update({"PTEC":"CodeTarifEnCours"})
    syllabus.update({"DEMAIN":"CouleurTEMPODemain"})
    syllabus.update({"IINST":"IntensiteInstantaneePhase1"})
    syllabus.update({"IINST1":"IntensiteInstantaneePhase1"})
    syllabus.update({"IINST2":"IntensiteInstantaneePhase2"})
    syllabus.update({"IINST3":"IntensiteInstantaneePhase3"})
    syllabus.update({"ADPS":"DepassementPuissance"})
    syllabus.update({"IMAX":"IntensiteMax"})
    syllabus.update({"IMAX1":"IntensiteMaxPhase1"})
    syllabus.update({"IMAX2":"IntensiteMaxPhase2"})
    syllabus.update({"IMAX3":"IntensiteMaxPhase3"})
    syllabus.update({"PMAX":"PuissanceMaxAtteinte"})
    syllabus.update({"PAPP":"PuissanceApparente"})
    syllabus.update({"HHPHC":"HorairesHC"})
    syllabus.update({"MOTDETAT":"MotEtat"})
    syllabus.update({"PPOT":"PresenceDesPotentiels"})
    syllabus.update({"ADIR1":"DepassementPuissancePhase1"})
    syllabus.update({"ADIR2":"DepassementPuissancePhase2"})
    syllabus.update({"ADIR3":"DepassementPuissancePhase3"})

    # Correspondances entre les clés de la TIC STANDARD et le dictionnaire traduit
    syllabus.update({"ADSC":"AdresseCompteur"})
    syllabus.update({"VTIC":"VersionTIC"})
    syllabus.update({"DATE":"DateHeureLinky"})
    syllabus.update({"NGTF":"TarifSouscrit"})
    #syllabus.update({"LTARF":"PeriodeTarifaireEnCours"})
    syllabus.update({"EAST":"Index00"})
    syllabus.update({"EASF01":"Index01"})
    syllabus.update({"EASF02":"Index02"})
    syllabus.update({"EASF03":"Index03"})
    syllabus.update({"EASF04":"Index04"})
    syllabus.update({"EASF05":"Index05"})
    syllabus.update({"EASF06":"Index06"})
    syllabus.update({"EASF07":"Index07"})
    syllabus.update({"EASF08":"Index08"})
    syllabus.update({"EASF09":"Index09"})
    syllabus.update({"EASF10":"Index10"})
    syllabus.update({"EASD01":"EnergieActiveSoutireeDistributeurIndex1"})
    syllabus.update({"EASD02":"EnergieActiveSoutireeDistributeurIndex2"})
    syllabus.update({"EASD03":"EnergieActiveSoutireeDistributeurIndex3"})
    syllabus.update({"EASD04":"EnergieActiveSoutireeDistributeurIndex4"})
    syllabus.update({"EAIT":"EnergieActiveInjectéeTotale"})
    syllabus.update({"ERQ1":"EnergieRéactiveQ1Totale"})
    syllabus.update({"ERQ2":"EnergieRéactiveQ2Totale"})
    syllabus.update({"ERQ3":"EnergieRéactiveQ3Totale"})
    syllabus.update({"ERQ4":"EnergieRéactiveQ4Totale"})
    syllabus.update({"IRMS1":"IntensiteInstantaneePhase1"})
    syllabus.update({"IRMS2":"IntensiteInstantaneePhase2"})
    syllabus.update({"IRMS3":"IntensiteInstantaneePhase3"})
    syllabus.update({"URMS1":"TensionEfficacePhase1"})
    syllabus.update({"URMS2":"TensionEfficacePhase2"})
    syllabus.update({"URMS3":"TensionEfficacePhase3"})
    syllabus.update({"PREF":"IntensiteSouscrite"})
    syllabus.update({"PCOUP":"PuissanceCoupure"})
    syllabus.update({"SINSTS":"PuissanceApparente"})
    syllabus.update({"SINSTS1":"PuissanceApparentePhase1"})
    syllabus.update({"SINSTS2":"PuissanceApparentePhase2"})
    syllabus.update({"SINSTS3":"PuissanceApparentePhase3"})
    syllabus.update({"SMAXSN":"PuissanceMaxAtteinte"})
    syllabus.update({"SMAXSN1":"PuissanceMaxAtteintePhase1"})
    syllabus.update({"SMAXSN2":"PuissanceMaxAtteintePhase2"})
    syllabus.update({"SMAXSN3":"PuissanceMaxAtteintePhase3"})
    syllabus.update({"SMAXSN-1":"PuissanceApparenteMaxN-1"})
    syllabus.update({"SMAXSN1-1":"PuissanceApparenteMaxN-1Phase1"})
    syllabus.update({"SMAXSN2-1":"PuissanceApparenteMaxN-1Phase2"})
    syllabus.update({"SMAXSN3-1":"PuissanceApparenteMaxN-1Phase3"})
    syllabus.update({"SINSTI":"PuissanceApparenteInstantanéeInjectée"})
    syllabus.update({"SMAXIN":"PuissanceApparenteMaxInjectée"})
    syllabus.update({"SMAXIN-1":"PuissanceApparenteMaxInjectéeN-1"})
    syllabus.update({"CCASN":"PointNCourbeChargeActiveSoutiree"})
    syllabus.update({"CCASN-1":"PointN-1CourbeChargeActiveSoutiree"})
    syllabus.update({"CCAIN":"PointNCourbeChargeActiveInjectée"})
    syllabus.update({"CCAIN-1":"PointN-1CourbeChargeActiveInjectée"})
    syllabus.update({"UMOY1":"TensionMoyennePhase1"})
    syllabus.update({"UMOY2":"TensionMoyennePhase2"})
    syllabus.update({"UMOY3":"TensionMoyennePhase3"})
    syllabus.update({"DPM1":"DebutPointeMobile1"})
    syllabus.update({"FPM1":"FinPointeMobile1"})
    syllabus.update({"DPM2":"DebutPointeMobile2"})
    syllabus.update({"FPM2":"FinPointeMobile2"})
    syllabus.update({"DPM3":"DebutPointeMobile3"})
    syllabus.update({"FPM3":"FinPointeMobile3"})
    syllabus.update({"MSG1":"MessageCourt"})
    syllabus.update({"MSG2":"MessageUltraCourt"})
    syllabus.update({"PRM":"PRM"})
    syllabus.update({"NTARF":"CodeTarifEnCours"})
    syllabus.update({"NJOURF":"NumeroJourCalendrierFournisseur"})
    syllabus.update({"NJOURF+1":"NumeroProchainJourCalendrierFournisseur"})
    syllabus.update({"PJOURF+1":"ProfilProchainJourCalendrierFournisseur"})
    syllabus.update({"PPOINTE":"ProfilProchainJourPointe"})
    syllabus.update({"TICMODE":"ModeTIC"})

    #On crée un dictionnaire indiquand, pour chaque clé du dictionnaire traduit, si la donnée est numérique ou alpha
    dataFormat.update({"AdresseCompteur":"char"})
    dataFormat.update({"CacheBorneDistributeur":"char"})
    dataFormat.update({"ContactSec":"char"})
    dataFormat.update({"CouleurDemain":"char"})
    dataFormat.update({"CouleurTEMPODemain":"char"})
    dataFormat.update({"CouleurTEMPOJour":"char"})
    dataFormat.update({"DateHeureLinky":"char"})
    dataFormat.update({"DebutPointeMobile1":"char"})
    dataFormat.update({"DebutPointeMobile2":"char"})
    dataFormat.update({"DebutPointeMobile3":"char"})
    dataFormat.update({"DepassementPuissance":"int"})
    dataFormat.update({"DepassementPuissancePhase1":"int"})
    dataFormat.update({"DepassementPuissancePhase2":"int"})
    dataFormat.update({"DepassementPuissancePhase3":"int"})
    dataFormat.update({"DepassementPuissanceRef":"char"})
    dataFormat.update({"EnergieActiveInjectéeTotale":"int"})
    dataFormat.update({"EnergieRéactiveQ1Totale":"int"})
    dataFormat.update({"EnergieRéactiveQ2Totale":"int"})
    dataFormat.update({"EnergieRéactiveQ3Totale":"int"})
    dataFormat.update({"EnergieRéactiveQ4Totale":"int"})
    dataFormat.update({"FinPointeMobile1":"char"})
    dataFormat.update({"FinPointeMobile2":"char"})
    dataFormat.update({"FinPointeMobile3":"char"})
    dataFormat.update({"Fonctionnement":"char"})
    dataFormat.update({"HorairesHC":"char"})
    dataFormat.update({"HorlogeDegradee":"char"})
    dataFormat.update({"Index00":"int"})
    dataFormat.update({"Index01":"int"})
    dataFormat.update({"Index02":"int"})
    dataFormat.update({"Index03":"int"})
    dataFormat.update({"Index04":"int"})
    dataFormat.update({"Index05":"int"})
    dataFormat.update({"Index06":"int"})
    dataFormat.update({"Index07":"int"})
    dataFormat.update({"Index08":"int"})
    dataFormat.update({"Index09":"int"})
    dataFormat.update({"Index10":"int"})
    dataFormat.update({"IndexBase":"int"})
    dataFormat.update({"IndexEJPNormale":"int"})
    dataFormat.update({"IndexEJPPointe":"int"})
    dataFormat.update({"IndexHC":"int"})
    dataFormat.update({"IndexHCJB":"int"})
    dataFormat.update({"IndexHCJR":"int"})
    dataFormat.update({"IndexHCJW":"int"})
    dataFormat.update({"IndexHP":"int"})
    dataFormat.update({"IndexHPJB":"int"})
    dataFormat.update({"IndexHPJR":"int"})
    dataFormat.update({"IndexHPJW":"int"})
    dataFormat.update({"IndexTotal":"int"})
    dataFormat.update({"IntensiteInstantanee":"int"})
    dataFormat.update({"IntensiteInstantaneePhase1":"int"})
    dataFormat.update({"IntensiteInstantaneePhase2":"int"})
    dataFormat.update({"IntensiteInstantaneePhase3":"int"})
    dataFormat.update({"IntensiteMax":"int"})
    dataFormat.update({"IntensiteMaxPhase1":"int"})
    dataFormat.update({"IntensiteMaxPhase2":"int"})
    dataFormat.update({"IntensiteMaxPhase3":"int"})
    dataFormat.update({"IntensiteSouscrite":"int"})
    dataFormat.update({"MessageCourt":"char"})
    dataFormat.update({"MessageUltraCourt":"char"})
    dataFormat.update({"ModeTIC":"char"})
    dataFormat.update({"MotEtat":"char"})
    dataFormat.update({"NumeroJourCalendrierFournisseur":"char"})
    dataFormat.update({"NumeroProchainJourCalendrierFournisseur":"char"})
    dataFormat.update({"NumeroTarifEnCours":"char"})
    dataFormat.update({"OrganeDeCoupure":"char"})
    dataFormat.update({"PeriodeTarifaireEnCours":"char"})
    dataFormat.update({"PointeMobile":"char"})
    dataFormat.update({"PointN-1CourbeChargeActiveInjectée":"int"})
    dataFormat.update({"PointN-1CourbeChargeActiveSoutiree":"int"})
    dataFormat.update({"PointNCourbeChargeActiveInjectée":"int"})
    dataFormat.update({"PointNCourbeChargeActiveSoutiree":"int"})
    dataFormat.update({"PreavisPointesMobiles":"char"})
    dataFormat.update({"PresenceDesPotentiels":"char"})
    dataFormat.update({"PRM":"char"})
    dataFormat.update({"ProfilProchainJourCalendrierFournisseur":"char"})
    dataFormat.update({"ProfilProchainJourPointe":"char"})
    dataFormat.update({"PuissanceApparente":"int"})
    dataFormat.update({"PuissanceApparenteInstantanéeInjectée":"int"})
    dataFormat.update({"PuissanceApparenteMaxInjectée":"int"})
    dataFormat.update({"PuissanceApparenteMaxInjectéeN-1":"int"})
    dataFormat.update({"PuissanceApparenteMaxN-1":"int"})
    dataFormat.update({"PuissanceApparenteMaxN-1Phase1":"int"})
    dataFormat.update({"PuissanceApparenteMaxN-1Phase2":"int"})
    dataFormat.update({"PuissanceApparenteMaxN-1Phase3":"int"})
    dataFormat.update({"PuissanceApparentePhase1":"int"})
    dataFormat.update({"PuissanceApparentePhase2":"int"})
    dataFormat.update({"PuissanceApparentePhase3":"int"})
    dataFormat.update({"PuissanceCoupure":"int"})
    dataFormat.update({"PuissanceMaxAtteinte":"int"})
    dataFormat.update({"PuissanceMaxAtteintePhase1":"int"})
    dataFormat.update({"PuissanceMaxAtteintePhase2":"int"})
    dataFormat.update({"PuissanceMaxAtteintePhase3":"int"})
    dataFormat.update({"RegistreModeTIC":"char"})
    dataFormat.update({"Relais":"char"})
    dataFormat.update({"SensEnergieActive":"char"})
    dataFormat.update({"SortieCommEuridis":"char"})
    dataFormat.update({"StatutCPL":"char"})
    dataFormat.update({"SurtensionPhase":"char"})
    dataFormat.update({"SynchroCPL":"char"})
    dataFormat.update({"TarifEnCoursD":"char"})
    dataFormat.update({"TarifEnCoursF":"char"})
    dataFormat.update({"TarifSouscrit":"char"})
    dataFormat.update({"TensionEfficacePhase1":"int"})
    dataFormat.update({"TensionEfficacePhase2":"int"})
    dataFormat.update({"TensionEfficacePhase3":"int"})
    dataFormat.update({"TensionMoyennePhase1":"int"})
    dataFormat.update({"TensionMoyennePhase2":"int"})
    dataFormat.update({"TensionMoyennePhase3":"int"})
    dataFormat.update({"VersionTIC":"char"})
    dataFormat.update({"EnergieActiveSoutireeDistributeurIndex1":"int"})
    dataFormat.update({"EnergieActiveSoutireeDistributeurIndex2":"int"})
    dataFormat.update({"EnergieActiveSoutireeDistributeurIndex3":"int"})
    dataFormat.update({"EnergieActiveSoutireeDistributeurIndex4":"int"})
    dataFormat.update({"CodeTarifEnCours":"char"})


    return syllabus, dataFormat



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
        registre.update({"CouleurTEMPOJour":"Pas d'annonce"})
    elif int(s[24:26], 2) == 1 :
        registre.update({"CouleurTEMPOJour":"Bleu"})
    elif int(s[24:26], 2) == 2 :
        registre.update({"CouleurTEMPOJour":"Blanc"})
    elif int(s[24:26], 2) == 3 :
        registre.update({"CouleurTEMPOJour":"Rouge"})
    else :
        registre.update({"CouleurTEMPOJour":"Statut inconnu : " + s[24:26]})

    if int(s[26:28], 2) == 0 :
        registre.update({"CouleurTEMPODemain":"Pas d'annonce"})
    elif int(s[26:28], 2) == 1 :
        registre.update({"CouleurTEMPODemain":"Bleu"})
    elif int(s[26:28], 2) == 2 :
        registre.update({"CouleurTEMPODemain":"Blanc"})
    elif int(s[26:28], 2) == 3 :
        registre.update({"CouleurTEMPODemain":"Rouge"})
    else :
        registre.update({"CouleurTEMPODemain":"Statut inconnu : " + s[26:28]})

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
#=== Ventilation des index en fonction de l'option tarifaire                 ===
#===============================================================================
def ventilIndex(analysedDict) :

    if analysedDict["TarifSouscrit"] == "Tarif de base" :
        analysedDict.update({"IndexBase":analysedDict["Index00"]})
        analysedDict.update({"IndexTotal":analysedDict["Index00"]})

    elif analysedDict["TarifSouscrit"] == "Heures Creuses" :
        analysedDict.update({"IndexHC":analysedDict["Index01"]})
        analysedDict.update({"IndexHP":analysedDict["Index02"]})
        if "Index00" in analysedDict :
            analysedDict.update({"IndexTotal":analysedDict["Index00"]})
        else :
            analysedDict.update({"IndexTotal":analysedDict["Index01"] + analysedDict["Index02"]})

    elif analysedDict["TarifSouscrit"] == "HC et Week-End" :
        analysedDict.update({"IndexHC":analysedDict["Index01"]})
        analysedDict.update({"IndexHP":analysedDict["Index02"]})
        analysedDict.update({"IndexWE":analysedDict["Index03"]})
        if "Index00" in analysedDict :
            analysedDict.update({"IndexTotal":analysedDict["Index00"]})
        else :
            analysedDict.update({"IndexTotal":analysedDict["Index01"] + analysedDict["Index02"] + analysedDict["Index03"]})

    elif analysedDict["TarifSouscrit"] == "EJP" :
        analysedDict.update({"IndexEJPNormale":analysedDict["Index01"]})
        analysedDict.update({"IndexEJPPointe":analysedDict["Index02"]})
        if "Index00" in analysedDict :
            analysedDict.update({"IndexTotal":analysedDict["Index00"]})
        else :
            analysedDict.update({"IndexTotal":analysedDict["Index01"] + analysedDict["Index02"]})

    elif analysedDict["TarifSouscrit"] == "TEMPO" :
        analysedDict.update({"IndexHCJB":analysedDict["Index01"]})
        analysedDict.update({"IndexHPJB":analysedDict["Index02"]})
        analysedDict.update({"IndexHCJW":analysedDict["Index03"]})
        analysedDict.update({"IndexHPJW":analysedDict["Index04"]})
        analysedDict.update({"IndexHCJR":analysedDict["Index05"]})
        analysedDict.update({"IndexHPJR":analysedDict["Index06"]})
        if "Index00" in analysedDict :
            analysedDict.update({"IndexTotal":analysedDict["Index00"]})
        else :
            analysedDict.update({"IndexTotal":analysedDict["Index01"] + analysedDict["Index02"] + analysedDict["Index03"] + analysedDict["Index04"] + analysedDict["Index05"] + analysedDict["Index06"]})

    return analysedDict



#===============================================================================
#=== Détermination de la periode en cours                                    ===
#===============================================================================
def periodeEnCours(analysedDict) :

    if analysedDict["TarifSouscrit"] == "Heures Creuses" :
        if analysedDict["CodeTarifEnCours"] in (["HC..", "01"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HC"})
        elif analysedDict["CodeTarifEnCours"] in (["HP..", "02"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HP"})

    if analysedDict["TarifSouscrit"] == "HC et Week-End" :
        if analysedDict["CodeTarifEnCours"] == "01" :
            analysedDict.update({"PeriodeTarifaireEnCours":"HC"})
        elif analysedDict["CodeTarifEnCours"] == "02":
            analysedDict.update({"PeriodeTarifaireEnCours":"HP"})
        elif analysedDict["CodeTarifEnCours"] == "03":
            analysedDict.update({"PeriodeTarifaireEnCours":"WE"})

    if analysedDict["TarifSouscrit"] == "EJP" :
        if analysedDict["CodeTarifEnCours"] in (["HN..", "01"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HN"})
        elif analysedDict["CodeTarifEnCours"] in (["PM..", "02"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"PM"})

    if analysedDict["TarifSouscrit"] == "TEMPO" :
        if analysedDict["CodeTarifEnCours"] in (["HCJB", "01"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HCJB"})
        elif analysedDict["CodeTarifEnCours"] in (["HPJB", "02"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HPJB"})
        elif analysedDict["CodeTarifEnCours"] in (["HCJW", "03"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HCJW"})
        elif analysedDict["CodeTarifEnCours"] in (["HPJW", "04"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HPJW"})
        elif analysedDict["CodeTarifEnCours"] in (["HCJR", "05"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HCJR"})
        elif analysedDict["CodeTarifEnCours"] in (["HCJR", "06"]) :
            analysedDict.update({"PeriodeTarifaireEnCours":"HCJR"})

    return analysedDict


#===============================================================================
#=== Traduction des options tarifaires                                       ===
#===============================================================================
def detOptionTarif(opTarif) :
    optionTarif = opTarif.strip()
    if optionTarif == "BASE" :
        nomTarif = "Tarif de base"
    elif optionTarif == "HC.." :
        nomTarif = "Heures Creuses"
    elif optionTarif == "H PLEINE/CREUSE" :
        nomTarif = "Heures Creuses"
    elif optionTarif == "Heures Creuses et Week-end" :
        nomTarif = "Heures Creuses et Week-end"
    elif optionTarif[:3] == "EJP" :
        nomTarif = "EJP"
    elif optionTarif == "TEMPO" :
        nomTarif = "TEMPO"
    else :
        nomTarif = "".join(["Tarif inconnu : ", optionTarif])

    return nomTarif


#===============================================================================
#=== Analyse du dictionnaire contenant la trame reçue                        ===
#===============================================================================
# Le but de cela est d'avoir un dictionnaire qui soit agnostique du mode de la TIC

def analyseTrame(syllabus, dataFormat, trameDict):
    consoTotale = 0
    analysedDict = {}

    for key in trameDict :
        if key in syllabus :
            if dataFormat[syllabus[key]] == "char" :
                analysedDict.update({syllabus[key]:trameDict[key]})
            else :
                analysedDict.update({syllabus[key]:int(trameDict[key])})
#        else :
#            print("Clé inconnue du syllabus : " + key)

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
        analysedDict.update({"CouleurTEMPOJour":registreDict["CouleurTEMPOJour"]})
        analysedDict.update({"CouleurTEMPODemain":registreDict["CouleurTEMPODemain"]})
        analysedDict.update({"PreavisPointesMobiles":registreDict["PreavisPointesMobiles"]})
        analysedDict.update({"PointeMobile":registreDict["PointeMobile"]})
        analysedDict.update({"RegistreModeTIC":registreDict["ModeTIC"]})

        analysedDict.update({"CouleurTEMPOJour":registreDict["CouleurTEMPOJour"]})
        analysedDict.update({"CouleurDemain":registreDict["CouleurTEMPODemain"]})


    #Nom et type de compteur
    if "ADCO" in trameDict :
        cptType, cptName = detCptType(trameDict["ADCO"])
        analysedDict.update({"TypeCompteur":cptType})
        analysedDict.update({"NomCompteur":cptName})

    if "ADSC" in trameDict :
        cptType, cptName = detCptType(trameDict["ADSC"])
        analysedDict.update({"TypeCompteur":cptType})
        analysedDict.update({"NomCompteur":cptName})


    #Options tarifaires
    optionTarif = ""
    if "OPTARIF" in trameDict :
        optionTarif = trameDict["OPTARIF"]
    elif "NGTF" in trameDict :
        optionTarif = trameDict["NGTF"]
    nomTarif = detOptionTarif(optionTarif)
    analysedDict.update({"TarifSouscrit":nomTarif})

    #Ventilation des index en fonction de l'option tarifaire
    analysedDict = ventilIndex(analysedDict)

    #Détermination de la periode tarifaire en cours
    analysedDict = periodeEnCours(analysedDict)

    #Horaire Heures Pleines Heures Creuses
    if "PJOURF+1" in trameDict :
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


    #Option tarifaire choisie
    if "ISOUSC" in trameDict :
        analysedDict.update({"IntensiteSouscrite":int(trameDict["ISOUSC"]) / 5})

    #Date et heure courante (Linky)
    if "DATE" in trameDict :
        analysedDict.update({"DateHeureLinky":trameDict["DATE"][0] + " - " + trameDict["DATE"][5:7] + "/" + trameDict["DATE"][3:5] + "/20" + trameDict["DATE"][1:3] + " - " + trameDict["DATE"][7:9] + ":" + trameDict["DATE"][9:11] + ":" + trameDict["DATE"][11:]})

    if "RELAIS" in trameDict :
        relaisValue = analyseRelais(trameDict["RELAIS"])
        analysedDict.update({"Relais":relaisValue})

    return analysedDict
