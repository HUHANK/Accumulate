
import struct
from io import BytesIO, StringIO

class Message(object):
    """"""
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

    def get_boolean(self):
        b = self.get_byte()
        return struct.unpack("?", b)
