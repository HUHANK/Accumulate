#include "socket.h"
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>

#define ERRMSG strerror(errno)

/*创建socket*/
int socket_create() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        printf("Create Socket Failed! error message:%s\n", ERRMSG);
    }
    return sock;
}

/*关闭*/
int close_socket(int fd) {
    if (fd < 0) {
        printf("function close_socket param not correct!\n");
        return fd;
    }
    close(fd);
    return 0;
}

/*设置非阻塞*/
int setnonblock(int fd) {
    int res = fcntl(fd, F_SETFL, fcntl(fd, F_GETFD, 0)|O_NONBLOCK);
    if (res < 0) {
        printf("Set NonBlock Error! error message: %s\n", ERRMSG);
    }
    return res;
}

/*socket关闭之后并不会立即收回，而是要经历一个TIME_WAIT的阶段。此时对这个端口进行重新绑定就会出错。要想立即绑定端口，需要先设置 SO_REUSEADDR*/
int socket_reuseaddr(int fd) {
    int on = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) == -1) {
        printf("setsockopt reuseaddr failed! error message:%s\n", ERRMSG);
        close_socket(fd);
        return -1;
    }
    return 0;
}

/*服务绑定--监听端口号*/
int socket_bind(int sock, int port) {
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port   = htons(port);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    /*bind*/
    int res = bind(sock, (struct sockaddr*)&addr, sizeof(addr));
    if (res == -1) {
        printf("socket bind failed! error message:%s\n", ERRMSG);
        close_socket(sock);
        return res;
    }

    res = listen(sock, 124);
    if (res == -1) {
        printf("socket listen failed! error message:%s\n", ERRMSG);
        close_socket(sock);
        return res;
    }
    return 0;
}

/*创建服务socket*/
int server_socket(int port) {
    if (port < 0) {
        printf("function server_socket param not correct!\n");
        return -1;
    }
    int sock = socket_create();
    if (sock < 0) return -1;

    int res = socket_reuseaddr(sock);
    if (res < 0) return -1;

    res = socket_bind(sock, port);
    if (res < 0) return -1;

    return sock;
}

/*连接到服务器*/
int connect_server(const char* ipaddr, int port) {
    if (port<0 || ipaddr==NULL) {
        printf("function connect_server param not correct!\n");
        return -1;
    }
    int sock = socket_create();
    if (sock < 0) return -1;

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port   = htons(port);
    addr.sin_addr.s_addr=inet_addr(ipaddr);

    int res = connect(sock, (struct sockaddr*)&addr, sizeof(addr));
    if (res == -1) {
        printf("socket connect failed! error message: %s\n", ERRMSG);
        return -1;
    }
    return sock;
}

/*将sockaddr_in转化成IP地址*/
int sockaddr_tos(const struct sockaddr_in *addr, char* ipaddr) {
    if ( !addr || !ipaddr ) return -1;
    unsigned char * p = (unsigned char*)&(addr->sin_addr.s_addr);
    sprintf(ipaddr, "%u.%u.%u.%u", p[0], p[1], p[2], p[3]);
    return 0;
}

/*接收客户端的socket*/
int server_accept(int sock) {
    if (sock < 0) {
        printf("function server_accept param not correct!\n");
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    socklen_t len = sizeof(addr);
    int client_sock = accept(sock, (struct sockaddr*)&addr, &len);
    if (client_sock < 0) {
        printf("accept client failed! error message: %s\n", ERRMSG);
        return -1;
    }
    else {
        char ipaddr[20] = {0};
        sockaddr_tos(&addr, ipaddr);
        printf("accept from %s\n", ipaddr);
    }
    return client_sock;
}

/*接收消息*/
int socket_recv(int sock, char* buf, const int buf_len) {
    if ( sock<0 || buf == NULL || buf_len <= 0 ) {
        printf("function socket_recv param not correct!\n");
        return -1;
    }
    int rc = 0;
    rc = recv(sock, buf, buf_len, 0);
    if (rc == 0) {
        printf("client is close!\n");
        return rc;
    } else if (rc < 0) {
        /*
         * recv错误信息：Connection reset by peer
         * 错误原因：服务端给客户端发送数据，但是客户端没有接收，直接关闭，那么就会报错
         * 如果客户端接受了数据，再关闭，也不会报错，rc==0.
         */
        printf("socket recv failed! error message: %s\n", ERRMSG);
        return rc;
    }
    return rc;
}

/*发送消息*/
int socket_send(int sock, const char* buf, const int buf_len) {
    if ( sock<0 || buf == NULL || buf_len <= 0 ) {
        printf("function socket_send param not correct!\n");
        return -1;
    }
    int rc = 0;
    rc = send(sock, buf, buf_len, 0);
    if (rc < 0) {
        printf("socket send failed! error message: %s\n", ERRMSG);
        return rc;
    }
    return rc;
}



























