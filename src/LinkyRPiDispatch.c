#include <stdio.h>
#include <stdlib.h>
#include <mqueue.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <stdbool.h>
#include <yaml.h>
#include <jansson.h>
#include "LinkyRPi.h"   // Fonctions spécifiques à LinkyRPi

#define MQ_LISTEN_NAME "/linkyrpi_listen"
#define MQ_MQTT_NAME   "/linkyrpi_mqtt"
//#define MQ_MQTT_NAME   "/LinkyRPiQMQTT"
#define MQ_DB_NAME     "/linkyrpi_db"
#define MQ_UI_NAME     "/linkyrpi_ui"
#define MQ_FILE_NAME   "/linkyrpi_file"

#define QUEUE_MSG_SIZE 8192
#define QUEUE_MAX_MSG 10

mqd_t mq_mqtt = (mqd_t)-1;
mqd_t mq_db = (mqd_t)-1;
mqd_t mq_ui = (mqd_t)-1;
mqd_t mq_file = (mqd_t)-1;


int main(int argc, char *argv[]) {
    printf("1/ Chargement de la configuration générale...\n");
    FILE *config_file = fopen("/home/linkyrpi/LinkyRPi/LinkyRPi3.conf", "r");
    if (config_file == NULL) {
        perror("Impossible d'ouvrir le fichier de configuration");
        return 1;
    }

    char line[256];
    while (fgets(line, sizeof(line), config_file)) {
        if (strstr(line, "UI=") != NULL) {
            ui_enabled = (strstr(line, "True") != NULL);
        } else if (strstr(line, "DB=") != NULL) {
            db_enabled = (strstr(line, "True") != NULL);
        } else if (strstr(line, "File=") != NULL) {
            file_enabled = (strstr(line, "True") != NULL);
        } else if (strstr(line, "MQTT=") != NULL) {
            mqtt_enabled = (strstr(line, "True") != NULL);
        }
    }
    fclose(config_file);

    // Affiche les flags récupérés
    printf("Configuration chargée : UI=%d, DB=%d, File=%d, MQTT=%d\n",
           ui_enabled, db_enabled, file_enabled, mqtt_enabled);

    printf("2/ Chargement du fichier de traduction YAML...\n");

    FILE *yaml_file = fopen("/home/linkyrpi/LinkyRPi/LinkyRPiTranslate.yaml", "r");
    if (!yaml_file) {
        perror("Impossible d'ouvrir le fichier YAML");
        return 1;
    }

    yaml_parser_t parser;
    yaml_event_t event;

    if (!yaml_parser_initialize(&parser)) {
        fprintf(stderr, "Erreur : impossible d'initialiser le parser YAML\n");
        fclose(yaml_file);
        return 1;
    }

    yaml_parser_set_input_file(&parser, yaml_file);

    int in_entities = 0;
    MeasureDetail current_entity = {0};
    int max_iterations = 2000; // Limite pour éviter les boucles infinies
    int iterations = 0;

    do {
        if (!yaml_parser_parse(&parser, &event)) {
            fprintf(stderr, "Erreur de parsing YAML : %s (itération %d)\n", parser.problem, iterations);
            break;
        }

        iterations++;
        if (iterations > max_iterations) {
            fprintf(stderr, "Avertissement : trop d'itérations, arrêt du parsing\n");
            break;
        }

        // Traite l'événement
        if (event.type == YAML_STREAM_END_EVENT) {
            printf("Fin du stream YAML détectée, sortie de la boucle\n");
            yaml_event_delete(&event);
            break;  // Sortie immédiate
        }

        // Logs et traitement des événements
        //printf("Événement YAML : %d (itération %d)\n", event.type, iterations);

        switch (event.type) {
            case YAML_MAPPING_START_EVENT:
                if (in_entities) {
                    memset(&current_entity, 0, sizeof(current_entity));
                }
                break;
            case YAML_SCALAR_EVENT:
                if (in_entities && event.data.scalar.value) {
                    char *key = (char *)event.data.scalar.value;
                    // Parse la valeur associée
                    if (!yaml_parser_parse(&parser, &event)) {
                        fprintf(stderr, "Erreur de parsing YAML (valeur manquante)\n");
                        yaml_event_delete(&event);
                        break;
                    }
                    if (event.type == YAML_SCALAR_EVENT && event.data.scalar.value) {
                        char *value = (char *)event.data.scalar.value;
                        // Ne traite que si on est dans une entité ET que tic_code est déjà rempli
                        if (strlen(current_entity.tic_code) > 0) {
                            if (strcmp(key, "friendly_name") == 0) {
                                strncpy(current_entity.friendly_name, value, sizeof(current_entity.friendly_name) - 1);
                            } else if (strcmp(key, "publish_frequency") == 0) {
                                current_entity.publish_frequency = atoi(value);
                            } else if (strcmp(key, "data_format") == 0) {
                                strncpy(current_entity.data_format, value, sizeof(current_entity.data_format) - 1);
                            }

                        } else if (strcmp(key, "tic_code") == 0) {
                            strncpy(current_entity.tic_code, value, sizeof(current_entity.tic_code) - 1);
                        }
                    }
                } else if (event.data.scalar.value && strcmp((char *)event.data.scalar.value, "entities") == 0) {
                    in_entities = 1;
                }
                break;

            case YAML_MAPPING_END_EVENT:
                if (in_entities && strlen(current_entity.tic_code) > 0 && entity_count < 200) {
                    detailed_entities[entity_count] = current_entity;
                    entity_count++;
                }
                break;
            default:
                break;
        }

        yaml_event_delete(&event);
    } while (!parser.error && iterations <= max_iterations);


    if (parser.error) {
        fprintf(stderr, "Erreur YAML : %s\n", parser.problem);
    }

    yaml_parser_delete(&parser);
    fclose(yaml_file);

    printf("Fichier YAML chargé : %d entités trouvées.\n", entity_count);


    printf("3/ Ouverture de la queue POSIX en entrée...\n");
    struct mq_attr attr = {
        .mq_maxmsg = 10,
        .mq_msgsize = QUEUE_MSG_SIZE
    };
    mqd_t mq = mq_open(MQ_LISTEN_NAME, O_RDONLY | O_NONBLOCK, 0644, &attr);
    if (mq == (mqd_t)-1) {
        perror("mq_open échoué");
        return 1;
    }
    printf("Queue '%s' ouverte en lecture.\n", MQ_LISTEN_NAME);

    printf("4/ Initialisation des queues POSIX de sortie (MQTT, DB, UI, File)...\n");
    if (mqtt_enabled) {
        mq_mqtt = mq_open(MQ_MQTT_NAME, O_WRONLY | O_CREAT, 0644, &attr);
        if (mq_mqtt == (mqd_t)-1) {
            perror("mq_open échoué pour MQTT");
            return 1;
        }
        printf("Queue MQTT '%s' ouverte en écriture.\n", MQ_MQTT_NAME);
    }

    if (db_enabled) {
        mq_db = mq_open(MQ_DB_NAME, O_WRONLY | O_CREAT, 0644, &attr);
        if (mq_db == (mqd_t)-1) {
            perror("mq_open échoué pour DB");
            return 1;
        }
        printf("Queue DB '%s' ouverte en écriture.\n", MQ_DB_NAME);
    }

    if (ui_enabled) {
        mq_ui = mq_open(MQ_UI_NAME, O_WRONLY | O_CREAT, 0644, &attr);
        if (mq_ui == (mqd_t)-1) {
            perror("mq_open échoué pour UI");
            return 1;
        }
        printf("Queue UI '%s' ouverte en écriture.\n", MQ_UI_NAME);
    }

    if (file_enabled) {
        mq_file = mq_open(MQ_FILE_NAME, O_WRONLY | O_CREAT, 0644, &attr);
        if (mq_file == (mqd_t)-1) {
            perror("mq_open échoué pour File");
            return 1;
        }
        printf("Queue File '%s' ouverte en écriture.\n", MQ_FILE_NAME);
    }



    printf("5/ Boucle principale de traitement...\n");
    char buffer[QUEUE_MSG_SIZE];
    unsigned int prio;
    int running = 1;
    while (running) {
        ssize_t bytes_read = mq_receive(mq, buffer, QUEUE_MSG_SIZE, &prio);
        if (bytes_read >= 0) {
            buffer[bytes_read] = '\0';
            printf("  a/ Lecture de la trame reçue...\n");
            translate_and_filter_trame(buffer, detailed_entities, entity_count, mqtt_enabled);

            printf("  c/ Filtrage des données selon publish_frequency...\n");
            json_t *output_json = build_output_json(buffer, detailed_entities, entity_count);
            if (output_json) {
                char *output_str = json_dumps(output_json, JSON_INDENT(0));
                //printf("JSON à envoyer :\n%s\n", output_str);

                // TODO : Ajouter les envois vers DB, UI, File si activés
                if (ui_enabled) {
                    // MQ_UI_NAME
                    printf(">> Envoi UI...\n");
                }
                if (db_enabled) {
                    // MQ_DB_NAME
                    printf(">> Envoi DB...\n");
                }
                if (file_enabled) {
                    // MQ_FILE_NAME
                    printf(">> Envoi File...\n");
                }
                if (mqtt_enabled && mq_mqtt != (mqd_t)-1) {
                    if (mq_send(mq_mqtt, output_str, strlen(output_str), 0) == -1) {
                        perror("mq_send échoué pour MQTT");
                        // Ne pas bloquer le programme, continuer le traitement
                    } else {
                        printf("Données envoyées à la queue MQTT.\n");
                    }
                }




                free(output_str);
                json_decref(output_json);
            }

        } else {
            if (errno == EAGAIN) {
                usleep(10000); // Attend 10ms avant de réessayer
            } else {
                perror("mq_receive échoué");
                running = 0; // Sort de la boucle en cas d'erreur fatale
            }
        }
    }

    printf("6/ Fermeture des queues et nettoyage...\n");
    mq_close(mq);
    // TODO : fermeture des queues de sortie et libération des ressources

    return 0;
}
