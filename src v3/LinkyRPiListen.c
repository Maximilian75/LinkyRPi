#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <string.h>
#include <mqueue.h>
#include <errno.h>
#include <time.h>
#include <stdarg.h>
#include <pthread.h>
#include <sys/inotify.h>
#include <limits.h>
#include <sys/stat.h>  // Pour mkdir()
#include <syslog.h>

// Constantes
#define CONFIG_FILE "/home/linkyrpi/LinkyRPi/LinkyRPi3.conf"
#define MAX_MSG_SIZE 512
#define MAX_PAIRS 20
#define LOG_BUFFER_SIZE 512
#define EVENT_SIZE (sizeof(struct inotify_event))
#define BUF_LEN (1024 * (EVENT_SIZE + NAME_MAX + 1))

// Niveaux de log
typedef enum { INFO, WARNING, ERROR, DEBUG } LogLevel;

// Structure pour la configuration
typedef struct {
    LogLevel log_level;
    char log_file[256];
    char serial_port[64];
    int serial_timeout;
    char queue_listen_name[64];
    int queue_max_messages;
} Config;

// Structure pour les paires clé/valeur
typedef struct {
    char key[32];
    char value[64];
} KeyValuePair;

// Variables globales
Config global_config;
volatile int config_reloaded = 0;
pthread_mutex_t log_mutex = PTHREAD_MUTEX_INITIALIZER;

// Prototypes
void load_config();
int detect_baudrate(int fd, int timeout);
void log_message(LogLevel level, const char *format, ...);
void send_to_queue(mqd_t mq, KeyValuePair *pairs, int pair_count);
void *monitor_config(void *arg);


int main() {
    // 1. Chargement de la config
    load_config();

    // 2. Ouverture du port série
    int fd = open(global_config.serial_port, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1) {
        fprintf(stderr, "[ERROR] Impossible d'ouvrir %s: %s\n",
                global_config.serial_port, strerror(errno));
        return 1;
    }
    fprintf(stderr, "[DEBUG] Port série ouvert (fd=%d)\n", fd);

    // 3. Création de la queue
    mqd_t mq = mq_open(global_config.queue_listen_name, O_WRONLY | O_CREAT, 0644, NULL);
    if (mq == (mqd_t)-1) {
        fprintf(stderr, "[ERROR] mq_open échoué: %s\n", strerror(errno));
        return 1;
    }
    fprintf(stderr, "[DEBUG] Queue créée (fd=%d)\n", (int)mq);

    // 4. Boucle principale (sans thread pour l'instant)
    char buffer[MAX_MSG_SIZE];
    int in_trame = 0;
    KeyValuePair pairs[MAX_PAIRS];
    int pair_count = 0;

    while (1) {
        int n = read(fd, buffer, MAX_MSG_SIZE);
        if (n > 0) {
            buffer[n] = '\0';
            fprintf(stderr, "[DEBUG] Données lues: %s\n", buffer);
        }
    }

    close(fd);
    mq_close(mq);
    return 0;
}




/*
int main2() {
    // 1. Chargement initial de la config
    global_config.queue_listen_name[0] = '\0';
    load_config();

    // 2. Ouverture du port série
    int fd = open(global_config.serial_port, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1) {
        log_message(ERROR, "Impossible d'ouvrir %s : %s", global_config.serial_port, strerror(errno));
        exit(EXIT_FAILURE);
    }
    log_message(INFO, "Port série %s ouvert avec succès (fd=%d)", global_config.serial_port, fd);

    // 3. Détection du baud rate
    int baudrate = detect_baudrate(fd, global_config.serial_timeout);
    if (baudrate == -1) {
        log_message(ERROR, "Impossible de détecter le baud rate");
        exit(EXIT_FAILURE);
    }
    log_message(INFO, "Baud rate détecté : %d", baudrate);

    // 4. Configuration finale du port série
    struct termios options;
    tcgetattr(fd, &options);
    cfsetispeed(&options, baudrate);
    cfsetospeed(&options, baudrate);
    options.c_cflag = CS7 | CLOCAL | CREAD;
    tcsetattr(fd, TCSANOW, &options);

    // 5. Ouverture de la queue POSIX
    log_message(INFO, "Tentative d'ouverture de la queue %s...", global_config.queue_listen_name);
    mqd_t mq = mq_open(global_config.queue_listen_name, O_WRONLY | O_CREAT, 0644, NULL);
    if (mq == (mqd_t)-1) {
        log_message(ERROR, "mq_open échoué pour %s : %s",
                    global_config.queue_listen_name, strerror(errno));
        exit(EXIT_FAILURE);
    }
    log_message(INFO, "Queue %s créée/ouverte avec succès (fd=%d)", global_config.queue_listen_name, (int)mq);


    // 6. Lancement du thread de surveillance de la config
    pthread_t config_thread;
    pthread_create(&config_thread, NULL, monitor_config, NULL);

    // 7. Boucle de lecture des trames
    char buffer[MAX_MSG_SIZE];
    KeyValuePair pairs[MAX_PAIRS];
    int pair_count = 0;
    int in_trame = 0;

    while (1) {
        if (config_reloaded) {
            mq_close(mq);
            mq = mq_open(global_config.queue_listen_name, O_WRONLY | O_CREAT, 0644, NULL);
            config_reloaded = 0;
        }

        int n = read(fd, buffer, MAX_MSG_SIZE);
        if (n > 0) {
            buffer[n] = '\0';
            log_message(DEBUG, "Données brutes lues (%d octets) : %s", n, buffer);

            if (strchr(buffer, '\x02') != NULL) {
                in_trame = 1;
                pair_count = 0;
                log_message(DEBUG, "Début de trame détecté");
                continue;
            }

            if (strchr(buffer, '\x03') != NULL && in_trame) {
                if (pair_count > 0) {
                    send_to_queue(mq, pairs, pair_count);
                    log_message(DEBUG, "Fin de trame détectée, %d paires envoyées", pair_count);
                }
                in_trame = 0;
                continue;
            }

            if (in_trame) {
                char *line = strdup(buffer);
                char *token = strtok(line, "\t ");
                if (token != NULL) {
                    strcpy(pairs[pair_count].key, token);
                    token = strtok(NULL, "\t ");
                    if (token != NULL) {
                        strcpy(pairs[pair_count].value, token);
                        log_message(DEBUG, "Paire ajoutée : %s=%s", pairs[pair_count].key, pairs[pair_count].value);
                        pair_count++;
                    }
                }
                free(line);
            }
        }
    }

    close(fd);
    mq_close(mq);
    return 0;
}
*/

// Chargement de la configuration
void load_config() {
    // Initialisation complète avec valeurs par défaut
    global_config.log_level = INFO;
    snprintf(global_config.log_file, sizeof(global_config.log_file), "/var/log/LinkyRPi/LinkyRPiListen.log");
    snprintf(global_config.serial_port, sizeof(global_config.serial_port), "/dev/ttyAMA0");
    global_config.serial_timeout = 2;
    snprintf(global_config.queue_listen_name, sizeof(global_config.queue_listen_name), "/linky_queue_listen");
    global_config.queue_max_messages = 10;

    FILE *f = fopen(CONFIG_FILE, "r");
    if (!f) {
        log_message(WARNING, "Impossible d'ouvrir %s. Utilisation des valeurs par défaut.", CONFIG_FILE);
        return;
    }

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (line[0] == '[' || line[0] == '\n') continue;
        char *key = strtok(line, "=");
        char *value = strtok(NULL, "=\n");
        if (!key || !value) continue;

        // Supprime les espaces en début/fin de chaîne
        while (*key == ' ') key++;
        while (*value == ' ') value++;

        if (strcmp(key, "level") == 0) {
            if (strcmp(value, "DEBUG") == 0) global_config.log_level = DEBUG;
            else if (strcmp(value, "INFO") == 0) global_config.log_level = INFO;
            else if (strcmp(value, "WARNING") == 0) global_config.log_level = WARNING;
            else if (strcmp(value, "ERROR") == 0) global_config.log_level = ERROR;
        } else if (strcmp(key, "file") == 0) {
            snprintf(global_config.log_file, sizeof(global_config.log_file), "%s", value);
        } else if (strcmp(key, "port") == 0) {
            snprintf(global_config.serial_port, sizeof(global_config.serial_port), "%s", value);
        } else if (strcmp(key, "timeout") == 0) {
            global_config.serial_timeout = atoi(value);
        } else if (strcmp(key, "queue_listen_name") == 0) {
            snprintf(global_config.queue_listen_name, sizeof(global_config.queue_listen_name), "%s", value);
        } else if (strcmp(key, "max_messages") == 0) {
            global_config.queue_max_messages = atoi(value);
        }
    }
    fclose(f);

    // Log de debug structuré
    log_message(INFO, "Config chargée : queue=%s, port=%s, level=%d",
                global_config.queue_listen_name, global_config.serial_port, global_config.log_level);
}


// Détection du baud rate
int detect_baudrate(int fd, int timeout) {
    int baudrates[] = {B1200, B9600};
    char *expected_keys[] = {"ADCO", "ADSC"};
    struct termios options;
    tcgetattr(fd, &options);

    for (int i = 0; i < 2; i++) {
        cfsetispeed(&options, baudrates[i]);
        cfsetospeed(&options, baudrates[i]);
        tcsetattr(fd, TCSANOW, &options);

        time_t start = time(NULL);
        char buffer[MAX_MSG_SIZE];
        int found = 0;

        while (time(NULL) - start < timeout) {
            int n = read(fd, buffer, MAX_MSG_SIZE);
            if (n > 0) {
                buffer[n] = '\0';
                if (strstr(buffer, expected_keys[i]) != NULL) {
                    found = 1;
                    break;
                }
            }
        }

        if (found) return baudrates[i];
    }

    return -1;
}

// Surveillance du fichier de config (inotify)
void *monitor_config(void *arg) {
    int fd = inotify_init();
    int wd = inotify_add_watch(fd, CONFIG_FILE, IN_MODIFY);
    char buffer[BUF_LEN];

    while (1) {
        int length = read(fd, buffer, BUF_LEN);
        if (length < 0) continue;

        for (char *ptr = buffer; ptr < buffer + length; ) {
            struct inotify_event *event = (struct inotify_event *)ptr;
            if (event->mask & IN_MODIFY) {
                log_message(INFO, "Fichier de config modifié, rechargement...");
                load_config();
                config_reloaded = 1;
            }
            ptr += EVENT_SIZE + event->len;
        }
    }
    return NULL;
}

// Envoi vers la queue POSIX
void send_to_queue(mqd_t mq, KeyValuePair *pairs, int pair_count) {
    char message[MAX_MSG_SIZE] = {0};
    for (int i = 0; i < pair_count; i++) {
        strcat(message, pairs[i].key);
        strcat(message, "=");
        strcat(message, pairs[i].value);
        if (i < pair_count - 1) strcat(message, "|");
    }
    log_message(DEBUG, "Envoi vers la queue : %s", message);
    if (mq_send(mq, message, strlen(message) + 1, 0) == -1) {
        log_message(ERROR, "Erreur lors de l'envoi vers la queue : %s", strerror(errno));
    }
}

// Génère les logs
void log_message(LogLevel level, const char *format, ...) {
    if (level > global_config.log_level) return;

    pthread_mutex_lock(&log_mutex);
    char log_buffer[LOG_BUFFER_SIZE];
    va_list args;
    va_start(args, format);
    vsnprintf(log_buffer, LOG_BUFFER_SIZE, format, args);
    va_end(args);

    const char *level_str;
    switch (level) {
        case INFO:    level_str = "INFO"; break;
        case WARNING: level_str = "WARNING"; break;
        case ERROR:   level_str = "ERROR"; break;
        case DEBUG:   level_str = "DEBUG"; break;
        default:      level_str = "INFO";
    }

    time_t now = time(NULL);
    struct tm *tm = localtime(&now);
    char timestamp[20];
    strftime(timestamp, 20, "%Y-%m-%dT%H:%M:%S", tm);

    FILE *log_file = fopen(global_config.log_file, "a");
    if (log_file) {
        fprintf(log_file, "[%s] [%s] %s\n", timestamp, level_str, log_buffer);
        fflush(log_file);
        fclose(log_file);
    } else {
        fprintf(stderr, "Erreur: Impossible d'ouvrir %s: %s\n", global_config.log_file, strerror(errno));
    }
    pthread_mutex_unlock(&log_mutex);
}
