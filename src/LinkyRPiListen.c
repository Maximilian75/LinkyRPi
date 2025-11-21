#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <fcntl.h>      // open()
#include <unistd.h>     // read(), close()
#include <errno.h>      // errno
#include <string.h>     // strerror()
#include <syslog.h>     // syslog()
#include <mqueue.h>     // mq_open()
#include <termios.h>    // Configuration du port série
#include <stdbool.h>
#include <yaml.h>
#include <jansson.h>
#include "LinkyRPi.h"   // Fonctions spécifiques à LinkyRPi

// Variables globales (à ajuster/déplacer plus tard)
#define SERIAL_PORT "/dev/ttyAMA0"
#define QUEUE_NAME "/linkyrpi_listen"
#define QUEUE_MAX_MSG 10
#define QUEUE_MSG_SIZE 8192

int fd_serial = -1;    // Descripteur du port série
mqd_t mq = (mqd_t)-1;



int main() {
    openlog("LinkyRPiListen", LOG_PID, LOG_USER);
    printf("Début du programme\n");

    // 1. Ouverture du port série
    printf("Ici on va ouvrir le port série %s\n", SERIAL_PORT);
    //fd_serial = open(SERIAL_PORT, O_RDWR | O_NOCTTY | O_NDELAY);
    fd_serial = open(SERIAL_PORT, O_RDWR | O_NOCTTY);
    if (fd_serial == -1) {
        printf("Impossible d'ouvrir %s: %s\n", SERIAL_PORT, strerror(errno));
        return 1;
    }
    printf("Port série ouvert (fd=%d)\n", fd_serial);

    // 2. Configuration du port série (termios)
    printf("Tentative de configuration en 9600 bauds...\n");
    struct termios serial_settings;
    if (tcgetattr(fd_serial, &serial_settings) < 0) {
        printf("tcgetattr échoué : %s\n", strerror(errno));
        return 1;
    }
    cfsetispeed(&serial_settings, B9600);
    cfsetospeed(&serial_settings, B9600);
    serial_settings.c_cflag &= ~PARENB;
    serial_settings.c_cflag |= PARENB | PARODD; // Parité paire
    serial_settings.c_cflag &= ~CSTOPB;         // 1 bit de stop
    serial_settings.c_cflag &= ~CSIZE;
    serial_settings.c_cflag |= CS7;             // 7 bits
    serial_settings.c_cflag |= (CLOCAL | CREAD);
    serial_settings.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    serial_settings.c_oflag &= ~OPOST;
    serial_settings.c_cc[VMIN] = 0;
    serial_settings.c_cc[VTIME] = 10; // Timeout 1s

    if (tcsetattr(fd_serial, TCSANOW, &serial_settings) < 0) {
        printf("tcsetattr (9600) échoué : %s\n", strerror(errno));
        return 1;
    }

    // Test de lecture en 9600 bauds
    fd_set read_fds;
    FD_ZERO(&read_fds);
    FD_SET(fd_serial, &read_fds);
    struct timeval timeout = {2, 0}; // Timeout 2s
    int ready = select(fd_serial + 1, &read_fds, NULL, NULL, &timeout);
    if (ready <= 0) {
        printf("Aucune donnée en 9600 bauds, bascule en 1200 bauds\n");
        cfsetispeed(&serial_settings, B1200);
        cfsetospeed(&serial_settings, B1200);
        if (tcsetattr(fd_serial, TCSANOW, &serial_settings) < 0) {
            printf("tcsetattr (1200) échoué : %s\n", strerror(errno));
            return 1;
        }
        printf("Mode TIC historique (1200 bauds) activé\n");
    } else {
        printf("Mode TIC standard (9600 bauds) activé\n");
    }

    // 3. Ouverture de la file POSIX
    printf("Ici on va ouvrir/creer la file POSIX %s\n", QUEUE_NAME);
    mq_unlink(QUEUE_NAME);
    struct mq_attr attr = {
        .mq_maxmsg = QUEUE_MAX_MSG,
        .mq_msgsize = QUEUE_MSG_SIZE
    };
    mq = mq_open(QUEUE_NAME, O_WRONLY | O_CREAT | O_NONBLOCK, 0644, &attr);

    struct mq_attr attr_check;
    if (mq_getattr(mq, &attr_check) == -1) {
        perror("mq_getattr échoué");
    } else {
        printf("Attributs de la queue :\n");
        printf("  - Taille max des messages : %ld\n", attr_check.mq_msgsize);
        printf("  - Nombre max de messages : %ld\n", attr_check.mq_maxmsg);
    }


    if (mq == (mqd_t)-1) {
        printf("mq_open échoué: %s\n", strerror(errno));
        close(fd_serial);
        return 1;
    }
    printf("Queue POSIX ouverte (mqd=%d)\n", (int)mq);

    // 4. Boucle principale : lecture des trames
    printf("Ici on va lire les trames en boucle et les envoyer à la file POSIX\n");
    char frame[2048] = {0};
    size_t frame_pos = 0;
    int in_frame = 0;
    char c;

    while (1) {
        ssize_t n = read(fd_serial, &c, 1); // Lire 1 octet à la fois
        if (n == 1) {

            // On attend de tomber sur le début de trame
            if (!in_frame && c == '\x02') {
                //printf("Début de trame détecté\n");
                in_frame = 1;
                frame_pos = 0;
                frame[frame_pos++] = c; // On garde le 0x02
            } else if (in_frame) {
                frame[frame_pos++] = c;

                // On lit jusqu'à la fin de la trame
                if (c == '\x03') {
                    frame[frame_pos] = '\0';

                    // Copie de frame pour strtok
                    char frame_copy[2048];
                    strncpy(frame_copy, frame, sizeof(frame_copy) - 1);

                    // Découpage de la trame en lignes
                    Measure measures[200];
                    int measure_count = 0;
                    char *saveptr1;
                    char *line = strtok_r(frame_copy, "\n", &saveptr1);

                    while (line != NULL) {
                        if (strlen(line) > 1) {
                            //printf("---------------------------------\n");
                            //printf("Line : %s\n", line);
                            treatmesure(line, measures, &measure_count);

                            // Traitement spécifique pour ADSC/ADCO
                            if (measure_count > 0 &&
                                (strcmp(measures[measure_count - 1].code, "ADSC") == 0 ||
                                 strcmp(measures[measure_count - 1].code, "ADCO") == 0)) {

                                char cptType[8] = {0};
                                char cptName[128] = {0};
                                detCptType(measures[measure_count - 1].value, cptType, cptName);

                                strncpy(measures[measure_count].code, "X_CT", sizeof(measures[measure_count].code) - 1);
                                strncpy(measures[measure_count].value, cptType, sizeof(measures[measure_count].value) - 1);
                                measure_count++;

                                strncpy(measures[measure_count].code, "X_CN", sizeof(measures[measure_count].code) - 1);
                                strncpy(measures[measure_count].value, cptName, sizeof(measures[measure_count].value) - 1);
                                measure_count++;
                                 }
                        }

                        line = strtok_r(NULL, "\n", &saveptr1);
                    }


                    // Traitement des tarifs
                    char tarifSouscrit[64] = {0};
                    char codeTarifEnCours[64] = {0};
                    char nomTarif[64] = {0};
                    char periodeTarifaire[64] = {0};

                    for (int i = 0; i < measure_count; i++) {
                        if (strcmp(measures[i].code, "NGTF") == 0 || strcmp(measures[i].code, "OPTARIF") == 0) {
                            strncpy(tarifSouscrit, measures[i].value, sizeof(tarifSouscrit) - 1);
                            detOptionTarif(tarifSouscrit, nomTarif);
                            strncpy(measures[measure_count].code, "X_TA", sizeof(measures[measure_count].code) - 1);
                            strncpy(measures[measure_count].value, nomTarif, sizeof(measures[measure_count].value) - 1);
                            measure_count++;
                        }
                        if (strcmp(measures[i].code, "PTEC") == 0 || strcmp(measures[i].code, "NTARF") == 0) {
                            strncpy(codeTarifEnCours, measures[i].value, sizeof(codeTarifEnCours) - 1);
                            periodeEnCours(nomTarif, codeTarifEnCours, periodeTarifaire);
                            strncpy(measures[measure_count].code, "X_PT", sizeof(measures[measure_count].code) - 1);
                            strncpy(measures[measure_count].value, periodeTarifaire, sizeof(measures[measure_count].value) - 1);
                            measure_count++;
                        }
                    }

/*
                    // Affichage des paires nettoyées
                    for (int i = 0; i < measure_count; i++) {
                        printf("%s : %s\n", measures[i].code, measures[i].value);
                    }
*/

                    // Push dans la queue POSIX
                    if (send_frame_to_queue(mq, measures, measure_count) <= 0) {
                        // On continue sans bloquer
                    }

                    in_frame = 0;
                    tcflush(fd_serial, TCIFLUSH);
                }

            }
        } else if (n < 0) {
            printf("Erreur de lecture : %s\n", strerror(errno));
        }
        usleep(10000);
    }

    // Nettoyage (normalement jamais atteint)
    printf("Ici on ferme tout proprement (port série, file POSIX, logs)\n");
    if (fd_serial != -1) close(fd_serial);
    if (mq != (mqd_t)-1) mq_close(mq);
    closelog();
    return 0;
}
