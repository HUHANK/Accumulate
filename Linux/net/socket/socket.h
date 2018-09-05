#ifndef SOCKET_H
#define SOCKET_H

#define ERRMSG strerror(errno)

/*创建服务socket*/
int server_socket(int port);

/*设置非阻塞*/
int setnonblock(int fd);

/*接收客户端的socket*/
int server_accept(int sock);

/*接收消息*/
int socket_recv(int sock, char* buf, const int buf_len);

/*发送消息*/
int socket_send(int sock, const char* buf, const int buf_len);

/*关闭*/
int close_socket(int fd);





























































#endif // SOCKET_H
