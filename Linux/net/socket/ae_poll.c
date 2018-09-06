#include "ae_poll.h"
#include <errno.h>

#define ERRMSG strerror(errno)

/*创建一个epoll实例*/
int aeCreate() {
    int epfd = epoll_create(1024);
    if (-1 == epfd) {
        printf("aeCreate failed! error message: %s\n", ERRMSG);
        return -1;
    }
    return epfd;
}


int aeEventOpt(const int epfd, const int fd, const int mask, const int opt) {
    if (epfd < 0 || fd < 0 || mask < 0 || opt < 0) {
        printf("function aeEventOpt param not correct!\n");
        return -1;
    }
    struct epoll_event ev = {0};
    ev.events = mask;
    ev.data.fd = fd;

    int res = epoll_ctl(epfd, opt, fd, &ev);
    if (res == -1) {
        printf("aeEventOpt failed! error message: %s\n", ERRMSG);
        return res;
    }
    return res;
}

/*ADD*/
int aeAddEvent(const int epfd, const int fd, const int mask) {
    return aeEventOpt(epfd, fd, mask, EPOLL_CTL_ADD);
}

/*MODIFY*/
int aeModEvent(const int epfd, const int fd, const int mask) {
    return aeEventOpt(epfd, fd, mask, EPOLL_CTL_MOD);
}

/*DELETE*/
int aeDelEvent(const int epfd, const int fd, const int mask) {
    return aeEventOpt(epfd, fd, mask, EPOLL_CTL_DEL);
}

/*等待所监听文件描述符上有事件发生*/
int aePoll(const int epfd, struct epoll_event *events, const int evSize) {
    int ret = 0;
    ret = epoll_wait(epfd, events, evSize, -1);
    if (ret < 0) {
        printf("epoll wait failed! error message: %s\n", ERRMSG);
        return -1;
    }
    return ret;
}

