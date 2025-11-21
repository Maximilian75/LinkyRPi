#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

int main() {
    fprintf(stderr, "[TEST] Ouverture de /dev/ttyAMA0...\n");
    int fd = open("/dev/ttyAMA0", O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1) {
        fprintf(stderr, "[ERROR] open() échoué: %s (errno=%d)\n",
                strerror(errno), errno);
        return 1;
    }
    fprintf(stderr, "[SUCCESS] Port ouvert (fd=%d)\n", fd);
    close(fd);
    return 0;
}
