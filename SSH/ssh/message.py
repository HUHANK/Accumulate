
import struct
from io import BytesIO, StringIO

def u(s, encoding='utf8'):
    if isinstance(s, bytes):
        return s.decode(encoding)
    elif isinstance(s, str):
        return s
    else:
        raise TypeError("Expected unicode or bytes, got {!r}".format(s))

class Message(object):
    """"""
    big_int = long(0xff000000)

    def __init__(self, content=None):
        if content is not None:
            self.packet = BytesIO(content)
        else:
            self.packet = BytesIO()

    def asbytes(self):
        """
        Return the byte stream content of this Message, as bytes.
        """
        return self.packet.getvalue()

    def rewind(self):
        self.packet.seek(0)

    def get_remainder(self):
        position = self.packet.tell()
        remainder = self.packet.read()
        self.packet.seek(position)
        return remainder

    def get_so_far(self):
        position = self.packet.tell()
        self.rewind()
        return self.packet.read(position)

    def get_bytes(self, n):
        b = self.packet.read(n)
        return b

    def get_byte(self):
        return self.get_bytes(1)

    def get_char(self):
        return struct.unpack('B', self.get_byte())[0]

    def get_boolean(self):
        b = self.get_byte()
        return struct.unpack("?", b)

    def get_int32(self):
        """Fetch a 32-bit unsigned integer"""
        return struct.unpack("!I", self.get_bytes(4))[0]

    def get_int64(self):
        """Fetch a 64-bit unsigned integer(long)"""
        return struct.unpack("!Q", self.get_bytes(8))[0]

    def get_string(self):
        return self.get_bytes(self.get_int32())

    def get_text(self):
        return u(self.get_string())

    def get_binary(self):
        return self.get_string()

    def get_list(self, divide=","):
        return self.get_text().split(divide)

    def add_bytes(self, b):
        self.packet.write(b)
        return self

    def add_boolean(self, b):
        assert isinstance(b, bool)
        return self.add_bytes(struct.pack('?', b))

    def add_char(self, c):
        return self.add_bytes(struct.pack('B', c))

    def add_int32(self, n):
        assert isinstance(n, int)
        return self.add_bytes(struct.pack('!I', n))

    def add_int64(self, n):
        assert isinstance(n, long )
        return self.add_bytes(struct.pack('!Q', n))

    def add_string(self, s):
        ss = None
        if isinstance(s, str):
            ss = s.encode("utf-8")
        else:
            ss = s
        self.add_int32(len(ss))
        return self.add_bytes(ss)

    def add_list(self, li):
        return self.add_string(','.join(li))


