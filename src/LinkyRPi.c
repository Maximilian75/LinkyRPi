//
// Librairie de fonctions pour LinkyRPi
//
#include <stdio.h>   // Pour printf, snprintf, atoi
#include <stdlib.h>  // Pour atoi
#include <errno.h>   // Pour errno
#include <ctype.h>
#include <fcntl.h>      // open()
#include <unistd.h>     // read(), close()
#include <errno.h>      // errno
#include <string.h>     // strerror()
#include <syslog.h>     // syslog()
#include <mqueue.h>     // mq_open()
#include <stdbool.h>
#include <yaml.h>
#include <jansson.h>
#include "LinkyRPi.h"   // Fonctions spécifiques à LinkyRPi

// Variables globales
#define SERIAL_PORT "/dev/ttyAMA0"
#define QUEUE_NAME "/linkyrpi_listen"
#define QUEUE_MAX_MSG 10
#define QUEUE_MSG_SIZE 8192

//-------------------------------------------------------------------------------------------------------------------//
// Supprime les espaces, tabulations et retours chariot en début et fin de chaîne
//-------------------------------------------------------------------------------------------------------------------//
void trim(char *str) {
    char *end;

    // Trim début
    while (isspace((unsigned char)*str)) str++;

    if (*str == 0) return; // Chaîne vide

    // Trim fin
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;

    // Nouveau terminateur
    *(end + 1) = '\0';
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction d'extraction du modèle et type de compteur
//-------------------------------------------------------------------------------------------------------------------//
void detCptType(const char *cptAddress, char *cptType, char *cptName) {
    if (strncmp(&cptAddress[4], "61", 2) == 0) {
        snprintf(cptName, 128, "61 - Compteur monophasé 60 A généralisation Linky G3 \\n Arrivée puissance haute - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "MONO", 5);
    } else if (strncmp(&cptAddress[4], "62", 2) == 0) {
        snprintf(cptName, 128, "62 - Compteur monophasé 90 A généralisation Linky G1 \\n Arrivée puissance basse - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "MONO", 5);
    } else if (strncmp(&cptAddress[4], "63", 2) == 0) {
        snprintf(cptName, 128, "63 - Compteur triphasé 60 A généralisation Linky G1 \\n Arrivée puissance basse - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "TRI", 4);
    } else if (strncmp(&cptAddress[4], "64", 2) == 0) {
        snprintf(cptName, 128, "64 - Compteur monophasé 60 A généralisation Linky G3 \\n Arrivée puissance basse - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "MONO", 5);
    } else if (strncmp(&cptAddress[4], "70", 2) == 0) {
        snprintf(cptName, 128, "70 - Compteur monophasé Linky 60 A \\n Mise au point G3 - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "MONO", 5);
    } else if (strncmp(&cptAddress[4], "71", 2) == 0) {
        snprintf(cptName, 128, "71 - Compteur triphasé Linky 60 A \\n Mise au point G3 - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "TRI", 4);
    } else if (strncmp(&cptAddress[4], "75", 2) == 0) {
        snprintf(cptName, 128, "75 - Compteur monophasé 90 A généralisation Linky G3 \\n Arrivée puissance basse - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "MONO", 5);
    } else if (strncmp(&cptAddress[4], "76", 2) == 0) {
        snprintf(cptName, 128, "76 - Compteur triphasé 60 A généralisation Linky G3 \\n Arrivée puissance basse - Millesime 20%s", &cptAddress[2]);
        strncpy(cptType, "TRI", 4);
    } else {
        snprintf(cptName, 128, "%.*s - Modèle de compteur non référencé \\n Enedis-NOI-CPT_54E - Millesime 20%s", 2, &cptAddress[4], &cptAddress[2]);
        strncpy(cptType, "", 1);
    }
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction de décodage du REGISTRE
//-------------------------------------------------------------------------------------------------------------------//
void analyseRegistre(const char *registreValue, Measure *measures, int *count) {
    // Conversion de la valeur hexadécimale en binaire (32 bits)
    unsigned int registre_int = (unsigned int)strtol(registreValue, NULL, 16);
    char s[33] = {0};
    for (int bit = 31; bit >= 0; bit--) {
        s[31 - bit] = (registre_int & (1 << bit)) ? '1' : '0';
    }
    s[32] = '\0';

    // ContactSec (X_CS)
    strncpy(measures[*count].code, "X_CS", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[0] == '0') ? "Fermé" : "Ouvert", sizeof(measures[*count].value) - 1);
    (*count)++;

    // OrganeDeCoupure (X_OC)
    strncpy(measures[*count].code, "X_OC", sizeof(measures[*count].code) - 1);
    char oc_value[64];
    int oc = (s[1] - '0') * 4 + (s[2] - '0') * 2 + (s[3] - '0');
    if (oc == 0) strncpy(oc_value, "Fermé", sizeof(oc_value) - 1);
    else if (oc == 1) strncpy(oc_value, "Ouvert sur surpuissance", sizeof(oc_value) - 1);
    else if (oc == 2) strncpy(oc_value, "Ouvert sur surtension", sizeof(oc_value) - 1);
    else if (oc == 3) strncpy(oc_value, "Ouvert sur délestage", sizeof(oc_value) - 1);
    else if (oc == 4) strncpy(oc_value, "Ouvert sur ordre CPL ou Euridis", sizeof(oc_value) - 1);
    else if (oc == 5) strncpy(oc_value, "Ouvert sur une surchauffe avec une valeur du courant supérieure au courant de commutation maximal", sizeof(oc_value) - 1);
    else if (oc == 6) strncpy(oc_value, "Ouvert sur une surchauffe avec une valeur de courant inférieure au courant de commutation maximal", sizeof(oc_value) - 1);
    else snprintf(oc_value, sizeof(oc_value), "Statut inconnu : %.*s", 3, &s[1]);
    strncpy(measures[*count].value, oc_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // CacheBorneDistributeur (X_BD)
    strncpy(measures[*count].code, "X_BD", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[4] == '0') ? "Fermé" : "Ouvert", sizeof(measures[*count].value) - 1);
    (*count)++;

    // SurtensionPhase (X_SP)
    strncpy(measures[*count].code, "X_SP", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[6] == '0') ? "Non" : "Oui", sizeof(measures[*count].value) - 1);
    (*count)++;

    // DepassementPuissanceRef (X_DP)
    strncpy(measures[*count].code, "X_DP", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[7] == '0') ? "Non" : "Oui", sizeof(measures[*count].value) - 1);
    (*count)++;

    // Fonctionnement (X_FO)
    strncpy(measures[*count].code, "X_FO", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[8] == '0') ? "Consommateur" : "Producteur", sizeof(measures[*count].value) - 1);
    (*count)++;

    // SensEnergieActive (X_SE)
    strncpy(measures[*count].code, "X_SE", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[9] == '0') ? "Positive" : "Négative", sizeof(measures[*count].value) - 1);
    (*count)++;

    // TarifEnCoursF (X_TF)
    strncpy(measures[*count].code, "X_TF", sizeof(measures[*count].code) - 1);
    char tf_value[64];
    int tf = (s[10] - '0') * 8 + (s[11] - '0') * 4 + (s[12] - '0') * 2 + (s[13] - '0');
    if (tf >= 1 && tf <= 10) snprintf(tf_value, sizeof(tf_value), "Energie ventilée sur Index %d", tf);
    else snprintf(tf_value, sizeof(tf_value), "Tarif inconnu : %.*s", 4, &s[10]);
    strncpy(measures[*count].value, tf_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // TarifEnCoursD (X_TD)
    strncpy(measures[*count].code, "X_TD", sizeof(measures[*count].code) - 1);
    char td_value[64];
    int td = (s[14] - '0') * 2 + (s[15] - '0');
    if (td >= 1 && td <= 4) snprintf(td_value, sizeof(td_value), "Energie ventilée sur Index %d", td);
    else snprintf(td_value, sizeof(td_value), "Tarif inconnu : %.*s", 2, &s[14]);
    strncpy(measures[*count].value, td_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // HorlogeDegradee (X_HD)
    strncpy(measures[*count].code, "X_HD", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[16] == '0') ? "Horloge correcte" : "Horloge en mode dégradée", sizeof(measures[*count].value) - 1);
    (*count)++;

    // ModeTIC (X_MT)
    strncpy(measures[*count].code, "X_MT", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[17] == '0') ? "Historique" : "Standard", sizeof(measures[*count].value) - 1);
    (*count)++;

    // SortieCommEuridis (X_CE)
    strncpy(measures[*count].code, "X_CE", sizeof(measures[*count].code) - 1);
    char ce_value[64];
    if (s[19] == '0' && s[20] == '0') strncpy(ce_value, "Désactivée", sizeof(ce_value) - 1);
    else if (s[19] == '0' && s[20] == '1') strncpy(ce_value, "Activée sans sécurité", sizeof(ce_value) - 1);
    else if (s[19] == '1' && s[20] == '1') strncpy(ce_value, "Activée avec sécurité", sizeof(ce_value) - 1);
    else snprintf(ce_value, sizeof(ce_value), "Statut inconnu : %.*s", 2, &s[19]);
    strncpy(measures[*count].value, ce_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // StatutCPL (X_CP)
    strncpy(measures[*count].code, "X_CP", sizeof(measures[*count].code) - 1);
    char cp_value[64];
    if (s[21] == '0' && s[22] == '0') strncpy(cp_value, "New/Unlock", sizeof(cp_value) - 1);
    else if (s[21] == '0' && s[22] == '1') strncpy(cp_value, "New/Lock", sizeof(cp_value) - 1);
    else if (s[21] == '1' && s[22] == '0') strncpy(cp_value, "Registered", sizeof(cp_value) - 1);
    else snprintf(cp_value, sizeof(cp_value), "Statut inconnu : %.*s", 2, &s[21]);
    strncpy(measures[*count].value, cp_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // SynchroCPL (X_SC)
    strncpy(measures[*count].code, "X_SC", sizeof(measures[*count].code) - 1);
    strncpy(measures[*count].value, (s[23] == '0') ? "Non synchronisé" : "Synchronisé", sizeof(measures[*count].value) - 1);
    (*count)++;

    // CouleurTEMPOJour (X_CT)
    strncpy(measures[*count].code, "X_CT", sizeof(measures[*count].code) - 1);
    char ct_value[64];
    int ct = (s[24] - '0') * 2 + (s[25] - '0');
    if (ct == 0) strncpy(ct_value, "Pas d'annonce", sizeof(ct_value) - 1);
    else if (ct == 1) strncpy(ct_value, "Bleu", sizeof(ct_value) - 1);
    else if (ct == 2) strncpy(ct_value, "Blanc", sizeof(ct_value) - 1);
    else if (ct == 3) strncpy(ct_value, "Rouge", sizeof(ct_value) - 1);
    else snprintf(ct_value, sizeof(ct_value), "Statut inconnu : %.*s", 2, &s[24]);
    strncpy(measures[*count].value, ct_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // CouleurTEMPODemain (X_CD)
    strncpy(measures[*count].code, "X_CD", sizeof(measures[*count].code) - 1);
    char cd_value[64];
    int cd = (s[26] - '0') * 2 + (s[27] - '0');
    if (cd == 0) strncpy(cd_value, "Pas d'annonce", sizeof(cd_value) - 1);
    else if (cd == 1) strncpy(cd_value, "Bleu", sizeof(cd_value) - 1);
    else if (cd == 2) strncpy(cd_value, "Blanc", sizeof(cd_value) - 1);
    else if (cd == 3) strncpy(cd_value, "Rouge", sizeof(cd_value) - 1);
    else snprintf(cd_value, sizeof(cd_value), "Statut inconnu : %.*s", 2, &s[26]);
    strncpy(measures[*count].value, cd_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // PreavisPointesMobiles (X_PP)
    strncpy(measures[*count].code, "X_PP", sizeof(measures[*count].code) - 1);
    char pp_value[64];
    int pp = (s[28] - '0') * 2 + (s[29] - '0');
    if (pp == 0) strncpy(pp_value, "Pas de préavis en cours", sizeof(pp_value) - 1);
    else if (pp == 1) strncpy(pp_value, "Préavis PM1 en cours", sizeof(pp_value) - 1);
    else if (pp == 2) strncpy(pp_value, "Préavis PM2 en cours", sizeof(pp_value) - 1);
    else if (pp == 3) strncpy(pp_value, "Préavis PM3 en cours", sizeof(pp_value) - 1);
    else snprintf(pp_value, sizeof(pp_value), "Statut inconnu : %.*s", 2, &s[28]);
    strncpy(measures[*count].value, pp_value, sizeof(measures[*count].value) - 1);
    (*count)++;

    // PointeMobile (X_PM)
    strncpy(measures[*count].code, "X_PM", sizeof(measures[*count].code) - 1);
    char pm_value[64];
    int pm = (s[30] - '0') * 4 + (s[31] - '0') * 2 + (s[32] - '0');
    if (pm == 0) strncpy(pm_value, "Pas de pointe mobile", sizeof(pm_value) - 1);
    else if (pm == 1) strncpy(pm_value, "PM1 en cours", sizeof(pm_value) - 1);
    else if (pm == 2) strncpy(pm_value, "PM2 en cours", sizeof(pm_value) - 1);
    else if (pm == 3) strncpy(pm_value, "PM3 en cours", sizeof(pm_value) - 1);
    else snprintf(pm_value, sizeof(pm_value), "Statut inconnu : %.*s", 3, &s[30]);
    strncpy(measures[*count].value, pm_value, sizeof(measures[*count].value) - 1);
    (*count)++;
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction de détermination de l'option tarifaire
//-------------------------------------------------------------------------------------------------------------------//
void detOptionTarif(const char *opTarif, char *nomTarif) {
    char cleanTarif[64];
    strncpy(cleanTarif, opTarif, sizeof(cleanTarif) - 1);
    cleanTarif[sizeof(cleanTarif) - 1] = '\0';
    trim(cleanTarif);

    if (strcmp(cleanTarif, "BASE") == 0) {
        strncpy(nomTarif, "Tarif de base", 64);
    } else if (strcmp(cleanTarif, "HC..") == 0 || strcmp(cleanTarif, "H PLEINE/CREUSE") == 0) {
        strncpy(nomTarif, "Heures Creuses", 64);
    } else if (strncmp(cleanTarif, "Heures Creuses et Week-end", 24) == 0) {
        strncpy(nomTarif, "Heures Creuses et Week-end", 64);
    } else if (strncmp(cleanTarif, "EJP", 3) == 0) {
        strncpy(nomTarif, "EJP", 64);
    } else if (strcmp(cleanTarif, "TEMPO") == 0) {
        strncpy(nomTarif, "TEMPO", 64);
    } else {
        snprintf(nomTarif, 64, "Tarif inconnu : %s", cleanTarif);
    }
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction de détermination du tarif en cours
//-------------------------------------------------------------------------------------------------------------------//
void periodeEnCours(const char *tarifSouscrit, const char *codeTarifEnCours, char *periodeTarifaire) {
    if (strcmp(tarifSouscrit, "Heures Creuses") == 0) {
        if (strcmp(codeTarifEnCours, "HC..") == 0 || strcmp(codeTarifEnCours, "01") == 0) {
            strncpy(periodeTarifaire, "HC", 64);
        } else if (strcmp(codeTarifEnCours, "HP..") == 0 || strcmp(codeTarifEnCours, "02") == 0) {
            strncpy(periodeTarifaire, "HP", 64);
        }
    } else if (strcmp(tarifSouscrit, "HC et Week-End") == 0) {
        if (strcmp(codeTarifEnCours, "01") == 0) {
            strncpy(periodeTarifaire, "HC", 64);
        } else if (strcmp(codeTarifEnCours, "02") == 0) {
            strncpy(periodeTarifaire, "HP", 64);
        } else if (strcmp(codeTarifEnCours, "03") == 0) {
            strncpy(periodeTarifaire, "WE", 64);
        }
    } else if (strncmp(tarifSouscrit, "EJP", 3) == 0) {
        if (strcmp(codeTarifEnCours, "HN..") == 0 || strcmp(codeTarifEnCours, "01") == 0) {
            strncpy(periodeTarifaire, "HN", 64);
        } else if (strcmp(codeTarifEnCours, "PM..") == 0 || strcmp(codeTarifEnCours, "02") == 0) {
            strncpy(periodeTarifaire, "PM", 64);
        }
    } else if (strcmp(tarifSouscrit, "TEMPO") == 0) {
        if (strcmp(codeTarifEnCours, "HCJB") == 0 || strcmp(codeTarifEnCours, "01") == 0) {
            strncpy(periodeTarifaire, "HCJB", 64);
        } else if (strcmp(codeTarifEnCours, "HPJB") == 0 || strcmp(codeTarifEnCours, "02") == 0) {
            strncpy(periodeTarifaire, "HPJB", 64);
        } else if (strcmp(codeTarifEnCours, "HCJW") == 0 || strcmp(codeTarifEnCours, "03") == 0) {
            strncpy(periodeTarifaire, "HCJW", 64);
        } else if (strcmp(codeTarifEnCours, "HPJW") == 0 || strcmp(codeTarifEnCours, "04") == 0) {
            strncpy(periodeTarifaire, "HPJW", 64);
        } else if (strcmp(codeTarifEnCours, "HCJR") == 0 || strcmp(codeTarifEnCours, "05") == 0) {
            strncpy(periodeTarifaire, "HCJR", 64);
        } else if (strcmp(codeTarifEnCours, "HPJR") == 0 || strcmp(codeTarifEnCours, "06") == 0) {
            strncpy(periodeTarifaire, "HPJR", 64);
        }
    }
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction d'extraction des plages horaires pleine/creuse
//-------------------------------------------------------------------------------------------------------------------//
void treatPJOURFPlus1(const char *value, Measure *measures, int *count) {
    char *tokens[11]; // Tableau pour stocker les tokens
    char *token;
    char value_copy[200];
    strncpy(value_copy, value, sizeof(value_copy) - 1);

    // Découpage de la valeur par espaces
    token = strtok(value_copy, " ");
    int i = 0;
    while (token != NULL && i < 11) {
        tokens[i] = token;
        token = strtok(NULL, " ");
        i++;
    }

    // Vérification de la présence de "NONUTILE"
    if (i > 0 && strcmp(tokens[0], "NONUTILE") == 0) {
        strncpy(measures[*count].code, "X_H1", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, "", sizeof(measures[*count].value) - 1);
        (*count)++;
        return;
    }

    // Traitement des plages horaires
    char plageHoraire[64];

    // Plage horaire 1
    if (i > 2 && strcmp(tokens[1], "NONUTILE") != 0 && strcmp(tokens[2], "NONUTILE") != 0) {
        snprintf(plageHoraire, sizeof(plageHoraire), "%.*s:%.*s - %.*s:%.*s",
                 2, tokens[1], 2, tokens[1] + 2,
                 2, tokens[2], 2, tokens[2] + 2);
        strncpy(measures[*count].code, "X_H1", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, plageHoraire, sizeof(measures[*count].value) - 1);
        (*count)++;
    } else {
        strncpy(measures[*count].code, "X_H1", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, "", sizeof(measures[*count].value) - 1);
        (*count)++;
    }

    // Plage horaire 2
    if (i > 4 && strcmp(tokens[3], "NONUTILE") != 0 && strcmp(tokens[4], "NONUTILE") != 0) {
        snprintf(plageHoraire, sizeof(plageHoraire), "%.*s:%.*s - %.*s:%.*s",
                 2, tokens[3], 2, tokens[3] + 2,
                 2, tokens[4], 2, tokens[4] + 2);
        strncpy(measures[*count].code, "X_H2", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, plageHoraire, sizeof(measures[*count].value) - 1);
        (*count)++;
    } else {
        strncpy(measures[*count].code, "X_H2", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, "", sizeof(measures[*count].value) - 1);
        (*count)++;
    }

    // Plage horaire 3
    if (i > 6 && strcmp(tokens[5], "NONUTILE") != 0 && strcmp(tokens[6], "NONUTILE") != 0) {
        snprintf(plageHoraire, sizeof(plageHoraire), "%.*s:%.*s - %.*s:%.*s",
                 2, tokens[5], 2, tokens[5] + 2,
                 2, tokens[6], 2, tokens[6] + 2);
        strncpy(measures[*count].code, "X_H3", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, plageHoraire, sizeof(measures[*count].value) - 1);
        (*count)++;
    } else {
        strncpy(measures[*count].code, "X_H3", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, "", sizeof(measures[*count].value) - 1);
        (*count)++;
    }

    // Plage horaire 4
    if (i > 8 && strcmp(tokens[7], "NONUTILE") != 0 && strcmp(tokens[8], "NONUTILE") != 0) {
        snprintf(plageHoraire, sizeof(plageHoraire), "%.*s:%.*s - %.*s:%.*s",
                 2, tokens[7], 2, tokens[7] + 2,
                 2, tokens[8], 2, tokens[8] + 2);
        strncpy(measures[*count].code, "X_H4", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, plageHoraire, sizeof(measures[*count].value) - 1);
        (*count)++;
    } else {
        strncpy(measures[*count].code, "X_H4", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, "", sizeof(measures[*count].value) - 1);
        (*count)++;
    }

    // Plage horaire 5
    if (i > 10 && strcmp(tokens[9], "NONUTILE") != 0 && strcmp(tokens[10], "NONUTILE") != 0) {
        snprintf(plageHoraire, sizeof(plageHoraire), "%.*s:%.*s - %.*s:%.*s",
                 2, tokens[9], 2, tokens[9] + 2,
                 2, tokens[10], 2, tokens[10] + 2);
        strncpy(measures[*count].code, "X_H5", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, plageHoraire, sizeof(measures[*count].value) - 1);
        (*count)++;
    } else {
        strncpy(measures[*count].code, "X_H5", sizeof(measures[*count].code) - 1);
        strncpy(measures[*count].value, "", sizeof(measures[*count].value) - 1);
        (*count)++;
    }
}



//-------------------------------------------------------------------------------------------------------------------//
// Fonction de nettoyage des données venant de la TIC
//-------------------------------------------------------------------------------------------------------------------//
void treatmesure(const char *line, Measure *measures, int *count) {
    char code[16] = {0};
    char value1[200] = {0};
    char value2[200] = {0};
    char checksum[4] = {0};
    char binary_value[9] = {0};

    // Copie locale de la ligne
    char line_copy[1024];
    strncpy(line_copy, line, sizeof(line_copy) - 1);
    //printf("--TreatMeasure--\n");
    //printf("%s\n", line_copy);


    // Découpage par tabulations
    char *saveptr2;
    char *token = strtok_r(line_copy, "\t", &saveptr2);
    if (token == NULL) {
        printf(">> Problème de décodage ligne 1 : %s\n", line);
        return;
    }
    strncpy(code, token, sizeof(code) - 1);
    //printf(">> Code : %s\n", code);

    token = strtok_r(NULL, "\t", &saveptr2);
    if (token == NULL) {
        printf(">> Problème de décodage ligne 2 : %s\n", line);
        return;
    }
    strncpy(value1, token, sizeof(value1) - 1);
    //printf(">> Value1 : %s\n", value1);

    token = strtok_r(NULL, "\t", &saveptr2);
    if (token != NULL) {
        strncpy(value2, token, sizeof(value2) - 1);
    } else {
        value2[0] = '\0';
    }
    //printf(">> Value2 : %s\n", value2);

    token = strtok_r(NULL, "\t", &saveptr2);
    if (token != NULL) {
        strncpy(checksum, token, sizeof(checksum) - 1);
    } else {
        checksum[0] = '\0';
    }
    //printf(">> Check : %s\n", checksum);

    // Traitement spécifique pour RELAIS
    if (strcmp(code, "RELAIS") == 0) {
        int ascii_value = atoi(value1);
        for (int bit = 7; bit >= 0; bit--) {
            binary_value[7 - bit] = (ascii_value & (1 << bit)) ? '1' : '0';
        }
        binary_value[8] = '\0';
        strncpy(measures[*count].value, binary_value, sizeof(measures[*count].value) - 1);
    }
    // Traitement spécifique pour REGISTRE
    else if (strcmp(code, "STGE") == 0) {
        analyseRegistre(value1, measures, count);
    }
    // Traitement spécifique pour PCOUP
    else if (strcmp(code, "PCOUP") == 0) {
        int pcout_val = atoi(value1);
        snprintf(measures[*count].value, sizeof(measures[*count].value), "%d", pcout_val * 1000);
    }
    // Traitement des plages horaires
    else if (strcmp(code, "PJOURF+1") == 0) {
        treatPJOURFPlus1(value1, measures, count);
    }


    // Cas particuliers avec timestamp
    else {
        const char *special_codes[] = {
            "SMAXSN", "SMAXSN-1", "CCASN", "CCASN-1", "UMOY1", "UMOY2", "UMOY3",
            "DPM1", "FPM1", "DPM2", "FPM2", "DPM3", "FPM3", NULL
        };
        int is_special = 0;
        for (int i = 0; special_codes[i] != NULL; i++) {
            if (strcmp(code, special_codes[i]) == 0) {
                is_special = 1;
                break;
            }
        }
        if (is_special) {
            strncpy(measures[*count].value, value2, sizeof(measures[*count].value) - 1);
        } else {
            strncpy(measures[*count].value, value1, sizeof(measures[*count].value) - 1);
        }
    }

    strncpy(measures[*count].code, code, sizeof(measures[*count].code) - 1);
    (*count)++;
    //printf("Fin treatmesure\n\n");
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction de push dans la queue POSIX LISTENER --> DISPATCHER
//-------------------------------------------------------------------------------------------------------------------//
int send_frame_to_queue(mqd_t mq, Measure *measures, int measure_count) {
    char message[QUEUE_MSG_SIZE];
    char *ptr = message;
    int remaining = sizeof(message);

    ptr += snprintf(ptr, remaining, "{\"trame\":[");
    remaining = sizeof(message) - (ptr - message);

    for (int i = 0; i < measure_count; i++) {
        int written = snprintf(ptr, remaining, "{\"code\":\"%s\",\"value\":\"%s\"}", measures[i].code, measures[i].value);
        ptr += written;
        remaining -= written;
        if (i < measure_count - 1) {
            *ptr++ = ',';
            remaining--;
        }
    }

    snprintf(ptr, remaining, "]}");

    //printf("Longueur du message : %zu octets (max autorisé : %d)\n", strlen(message), QUEUE_MSG_SIZE);
    if (mq_send(mq, message, strlen(message), 0) == -1) {
        if (errno == EAGAIN) {
            printf("Queue pleine, trame abandonnée\n");
            return 0;
        } else {
            printf("mq_send échoué : %s (errno: %d)\n", strerror(errno), errno);
            return -1;
        }
    }
    return 1;
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction de traduction de la trame 'brute' venue du listener, en trame agnostique et parlante
//-------------------------------------------------------------------------------------------------------------------//
Measure entities[200];
MeasureDetail detailed_entities[200];

int entity_count = 0;
uint8_t ui_enabled = 0;
uint8_t db_enabled = 0;
uint8_t file_enabled = 0;
uint8_t mqtt_enabled = 0;

void translate_and_filter_trame(const char *trame_json, MeasureDetail *detailed_entities, int entity_count, bool mqtt_enabled) {
    json_t *root;
    json_error_t error;

    root = json_loads(trame_json, 0, &error);
    if (!root) {
        fprintf(stderr, "Erreur de parsing JSON : %s\n", error.text);
        return;
    }

    json_t *trame_array = json_object_get(root, "trame");
    if (!json_is_array(trame_array)) {
        fprintf(stderr, "Erreur : 'trame' n'est pas un tableau JSON\n");
        json_decref(root);
        return;
    }

    size_t index;
    json_t *value;

    json_array_foreach(trame_array, index, value) {
        json_t *code_json = json_object_get(value, "code");
        json_t *value_json = json_object_get(value, "value");

        if (!json_is_string(code_json) || !json_is_string(value_json)) {
            printf("Ignoré : entrée invalide\n");
            continue;
        }

        const char *code = json_string_value(code_json);
        const char *val = json_string_value(value_json);

        bool found = false;
        for (int i = 0; i < entity_count; i++) {
            if (strcmp(detailed_entities[i].tic_code, code) == 0) {
                found = true;
                break;
            }
        }

        if (!found) {
            printf("Non traduit : code '%s' (valeur = '%s')\n", code, val);
        }
    }

    json_decref(root);
}


//-------------------------------------------------------------------------------------------------------------------//
// Fonction de construction du JSON pour envoi DISPATCHER --> Consommateurs (UI, DB, MQTT)
//-------------------------------------------------------------------------------------------------------------------//
json_t *build_output_json(const char *trame_json, MeasureDetail *detailed_entities, int entity_count) {
    json_t *root = json_loads(trame_json, 0, NULL);
    if (!root) return NULL;

    json_t *trame_array = json_object_get(root, "trame");
    if (!json_is_array(trame_array)) {
        json_decref(root);
        return NULL;
    }

    json_t *output = json_object();

    size_t index;
    json_t *value;
    json_array_foreach(trame_array, index, value) {
        json_t *code_json = json_object_get(value, "code");
        json_t *value_json = json_object_get(value, "value");

        if (!json_is_string(code_json) || !json_is_string(value_json))
            continue;

        const char *code = json_string_value(code_json);
        const char *val = json_string_value(value_json);

        for (int i = 0; i < entity_count; i++) {
            if (strcmp(detailed_entities[i].tic_code, code) == 0) {
                json_object_set_new(output, detailed_entities[i].friendly_name, json_string(val));
                break;
            }
        }
    }

    json_decref(root);
    return output;
}

