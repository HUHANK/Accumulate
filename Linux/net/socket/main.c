#include <stdio.h>
#include "socket.h"
#include "ae_poll.h"

#define BUF_SIZE  (1024*8)

int main()
{
    int i = 0;
    char buf[BUF_SIZE];
    int listens = server_socket(6600);
    int epfd = aeCreate();
    aeAddEvent(epfd, listens, EPOLLIN | EPOLLERR | EPOLLHUP);

    struct epoll_event events[1024];
    struct epoll_event ev ;
    while(1) {
        int evc = aePoll(epfd, events, 1024);
        printf("COUNT: %d\n", evc);
        for (i=0; i<evc; i++) {
            ev = events[i];
            if (ev.data.fd == listens) {
                int client = server_accept(listens);
                if (client < 0) continue;
                setnonblock(client);
                aeAddEvent(epfd, client, EPOLLIN | EPOLLERR | EPOLLHUP);
                continue;
            }
            if (ev.data.fd & EPOLLIN) {
                int c = socket_recv(ev.data.fd, buf, BUF_SIZE);
                if (c <= 0) {
                    aeDelEvent(epfd, ev.data.fd, 0);
                    continue;
                }
                printf("#-------------------------------------------------#\n");
                printf("RECV: %s\n", buf);
                //close_socket(ev.data.fd);
                aeModEvent(epfd, ev.data.fd, EPOLLOUT);
                continue;
            }
            else if (ev.data.fd & EPOLLOUT) {
                socket_send(ev.data.fd, "ABCDEFGHIJKLMN", strlen("ABCDEFGHIJKLMN")+1);
                aeModEvent(epfd, ev.data.fd, EPOLLOUT);
                continue;
            }
            else if (ev.data.fd & EPOLLERR) {
                printf("EPOLLERR\n");
                close_socket(ev.data.fd);
                aeDelEvent(epfd, ev.data.fd, 0);
            }
            else if (ev.data.fd & EPOLLHUP) {
                printf("EPOLLHUP\n");
                close_socket(ev.data.fd);
                aeDelEvent(epfd, ev.data.fd, 0);
            }
        }
    }
    close(epfd);
    close_socket(listens);
    return 0;
}
