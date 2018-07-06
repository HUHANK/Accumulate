
import os
import errno
import socket
from message import Message


class Packetizer(object):

    SERVER_SSH_VERSION = None
    CLIENT_SSH_VERSION = "SSH-2.0-HYL_Release_0.01"
    # These tuples of algorithm identifiers are in preference order; do not
    # reorder without reason!
    _preferred_ciphers = (
        'aes128-ctr',
        'aes192-ctr',
        'aes256-ctr',
        'aes128-cbc',
        'aes192-cbc',
        'aes256-cbc',
        'blowfish-cbc',
        '3des-cbc',
    )
    _preferred_macs = (
        'hmac-sha2-256',
        'hmac-sha2-512',
        'hmac-sha1',
        'hmac-md5',
        'hmac-sha1-96',
        'hmac-md5-96',
    )
    _preferred_keys = (
        'ssh-ed25519',
        'ecdsa-sha2-nistp256',
        'ecdsa-sha2-nistp384',
        'ecdsa-sha2-nistp521',
        'ssh-rsa',
        'ssh-dss',
    )
    _preferred_kex = (
        'ecdh-sha2-nistp256',
        'ecdh-sha2-nistp384',
        'ecdh-sha2-nistp521',
        'diffie-hellman-group-exchange-sha256',
        'diffie-hellman-group-exchange-sha1',
        'diffie-hellman-group14-sha1',
        'diffie-hellman-group1-sha1',
    )
    _preferred_gsskex = (
        'gss-gex-sha1-toWM5Slw5Ew8Mqkay+al2g==',
        'gss-group14-sha1-toWM5Slw5Ew8Mqkay+al2g==',
        'gss-group1-sha1-toWM5Slw5Ew8Mqkay+al2g==',
    )
    _preferred_compression = ('none',)


    def __init__(self, socket):
        self.__socket = socket

    def wriate_all(self, out):
        while len(out) > 0:
            retry_write = False
            try:
                n = self.__socket.send(out)
            except socket.timeout:
                retry_write = True
            except socket.error as e:
                arg = e.args[0]
                if arg == errno.EAGAIN:
                    retry_write = True
                elif arg == errno.EINTR:
                    retry_write = True
                else:
                    n = -1
            except Exception:
                n = -1
            if retry_write:
                n = 0
            if n < 0:
                raise EOFError()
            if n == len(out):
                break
            out = out[n:]

        return

    def read_all(self, n):
        """"""
        out = bytes()
        while n > 0:
            got_timeout = False
            try:
                x = self.__socket.recv(n)
                if len(x) == 0:
                    raise EOFError()
                out += x
                n -= len(x)
            except socket.timeout:
                got_timeout = True
            except socket.error as e:
                arg = e.args[0]
                if arg == errno.EAGAIN:
                    got_timeout = True
                elif arg == errno.EINTR:
                    #syscall interrupted; try again
                    pass
                else:
                    raise
        return out

    def read_max(self, n=8192):
        out = bytes()
        try:
            return self.__socket.recv(n)
        except Exception:
            raise
        return out

    def _build_packet(self, payload):
        bsize = 8
        padding = 3 + bsize - ((len(payload) + 8) % bsize)
        packet = Message()
        packet.add_int32(len(payload)+padding+1)
        packet.add_char(padding)
        packet.add_bytes(payload)
        packet.add_bytes(os.urandom(padding))
        return packet.asbytes()

    def negotiate_version(self):
        self.wriate_all(self.CLIENT_SSH_VERSION + "\r\n")
        self.SERVER_SSH_VERSION = self.read_max()
        print self.SERVER_SSH_VERSION

    def kex_init(self):

        m = Message()
        m.add_char(20)
        m.add_bytes(os.urandom(16))
        m.add_list(self._preferred_kex)
        m.add_list(self._preferred_keys)
        m.add_list(self._preferred_ciphers)
        m.add_list(self._preferred_ciphers)
        m.add_list(self._preferred_macs)
        m.add_list(self._preferred_macs)
        m.add_list(self._preferred_compression)
        m.add_list(self._preferred_compression)
        m.add_string(bytes())
        m.add_string(bytes())
        m.add_boolean(False)
        m.add_int32(0)

        packet = self._build_packet(m.asbytes())
        self.wriate_all(packet)

        m = Message(self.read_max())
        print m.get_int32()
        print m.get_char()
        print m.get_char()
        print m.get_bytes(16)
        print m.get_string()
        print m.get_string()

        print m.get_string()
        print m.get_string()

        print m.get_string()
        print m.get_string()

        print m.get_string()
        print m.get_string()

        print m.get_string()
        print m.get_string()

        print m.get_char()
        print m.get_int32()











client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("10.10.14.36", 22))

packet = Packetizer(client)

packet.negotiate_version()
packet.kex_init()

