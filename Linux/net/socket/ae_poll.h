#ifndef AE_POLL_H
#define AE_POLL_H
#include <sys/epoll.h>

int aeCreate();

int aeAddEvent(const int epfd, const int fd, const int mask);

int aeModEvent(const int epfd, const int fd, const int mask);

int aeDelEvent(const int epfd, const int fd, const int mask);

int aePoll(const int epfd, struct epoll_event *events, const int evSize);


#endif // AE_POLL_H
