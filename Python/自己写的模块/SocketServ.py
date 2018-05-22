# -*- coding:utf-8 -*-

import threading
import Queue
import socket
import sys
import traceback

QUEUE_SIZE = 5


class TcpSocketServer(object):
    """TCP/IP Socket Server"""
    def __init__(self, port):
        self.__tcp_fd = None
        self.__address = ('127.0.0.1', port)
        self.LISTEN = 30
        super(TcpSocketServer, self).__init__()

    def start(self):
        try:
            self.__tcp_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
            self.__tcp_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__tcp_fd.bind(self.__address)
            self.__tcp_fd.listen(self.LISTEN)
        except socket.error as msg:
            print msg
            sys.exit(1)

        while True:
            conn, addr = self.__tcp_fd.accept()
            self.tcp_request_process(conn, addr)

    def tcp_request_process(self, conn, addr):
        pass


class HTTPRequestHandle(object):
    """ """
    def __init__(self, conn):
        super(HTTPRequestHandle, self).__init__()
        self.conn = conn
        self.timeout = 2

    def setup(self):
        if self.timeout is not None:
            self.conn.settimeout(self.timeout)
        self.rfile = self.conn.makefile('rb', -1)
        self.wfile = self.conn.makefile('wb', 0)

    def finish(self):
        if not self.wfile.closed:
            try:
                self.wfile.flush()
            except socket.error:
                # A final socket error may have occurred here, such as
                # the local error ECONNABORTED.
                pass
        self.wfile.close()
        self.rfile.close()
        self.conn.close()

    def handle(self):
        try:
            self.setup()

            #1
            line = self.rfile.readline()
            line = line.rstrip("\r\n")
            words = line.split()
            if len(words) == 3:
                self.command, self.path, self.version = words

            if len(words) != 3 or self.version[:5] != 'HTTP/':
                print "Bad request version (%r)" % self.version
                return False

            #2
            self.headers = {}
            while True:
                line = self.rfile.readline()
                line = line.rstrip("\r\n")

                if not line:
                    break
                words = line.split(":", 1)
                if len(words) == 2:
                    k, v = words
                    self.headers[k.strip()] = v.strip()

            #3get Data
            ln = int(self.headers['Content-Length'])
            self.data = self.rfile.read(ln)

            mname = "do_" + self.command
            if not hasattr(self, mname):
                print "Unsupported method (%r)" % mname
            else:
                method = getattr(self, mname)
                method()
            self.wfile.flush()
        except socket.timeout, e:
            print "Request timed out: %r" % (e)
        finally:
            self.finish()

class HTTPServer(TcpSocketServer):
    def __init__(self, port=8800, pron=1):
        super(HTTPServer, self).__init__(port)
        self.conns = Queue.Queue(QUEUE_SIZE)
        self.PROCESS_NUM = pron
        self.processes = []
        for i in range(self.PROCESS_NUM):
            t = threading.Thread(target=HTTPServer.mult_process_func, args=(self,))
            t.start()
            self.processes.append(t)

    def mult_process_func(self):
        while True:
            conn = self.conns.get()
            http = HTTPRequestHandle(conn)
            http.handle()

    def tcp_request_process(self, conn, addr):
        print addr
        self.conns.put(conn, timeout=1)





#测试
if __name__ == '__main__':
    http = HTTPServer(pron=10)
    http.start()











































