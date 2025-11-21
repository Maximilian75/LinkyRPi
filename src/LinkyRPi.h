#ifndef LINKYRPI_H
#define LINKYRPI_H

#include <stdint.h>

// Structure pour les données brutes de la TIC
typedef struct {
    char code[50];
    char value[50];
} Measure;

// Structure pour les données traduites et complétées pour les consommateurs et le dispatcheur
typedef struct {
    char tic_code[20];
    char friendly_name[50];
    unsigned int publish_frequency;
    char data_format[10];
    char mqtt_topic[100];
    char device_class[20];
    char unit_of_measurement[10];
    char icon[30];
} MeasureDetail;

// Déclaration des variables globales (extern)
extern Measure entities[];
extern MeasureDetail detailed_entities[];
extern int entity_count;
extern uint8_t ui_enabled;
extern uint8_t db_enabled;
extern uint8_t file_enabled;
extern uint8_t mqtt_enabled;


// Fonctions utilisées par le listener
void trim(char *str);
void detCptType(const char *cptAddress, char *cptType, char *cptName);
void analyseRegistre(const char *registreValue, Measure *measures, int *count);
void detOptionTarif(const char *opTarif, char *nomTarif);
void periodeEnCours(const char *tarifSouscrit, const char *codeTarifEnCours, char *periodeTarifaire);
void treatPJOURFPlus1(const char *value, Measure *measures, int *count);
void treatmesure(const char *line, Measure *measures, int *count);
int send_frame_to_queue(mqd_t mq, Measure *measures, int measure_count);

// Fonctions utilisées par le dispatcheur
void translate_and_filter_trame(const char *trame_json, MeasureDetail *detailed_entities, int entity_count, bool mqtt_enabled);
json_t *build_output_json(const char *trame_json, MeasureDetail *detailed_entities, int entity_count);

#endif
