#include <stdio.h>
#include "socket.h"

#define BUF_SIZE  (1024*8)

int main()
{
    char buf[BUF_SIZE];
    int sock = server_socket(6600);
    while(1) {
        int client = server_accept(sock);
        socket_recv(client, buf, BUF_SIZE);
        printf("RECV:%s\n", buf);
        close_socket(client);
    }
}
