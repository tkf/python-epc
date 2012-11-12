import unittest
import io

from ..client import EPCClient
from ..core import encode_message, decode_message


class FakeSocket(object):

    def __init__(self):
        self._buffer = io.BytesIO()
        self.sent_message = []

    def append(self, byte):
        pos = self._buffer.tell()
        self._buffer.write(byte)
        self._buffer.seek(pos)

    def recv(self, bufsize):
        return self._buffer.read(bufsize)

    def sendall(self, string):
        self.sent_message.append(string)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.fsock = FakeSocket()
        self.client = EPCClient(self.fsock)

    def set_next_reply(self, *args):
        self.fsock.append(encode_message(*args))

    def sent_message(self, i=0):
        (name, uid, rest) = decode_message(self.fsock.sent_message[0][6:])
        if name == 'call':
            rest[0] = rest[0].value()
        return [name, uid] + rest

    def test_call_return(self):
        uid = 1
        returned = 'some value'
        self.set_next_reply('return', uid, returned)
        got = self.client.call('dummy', [1, 2, 3])
        self.assertEqual(got, returned)
        sent = self.sent_message()
        self.assertEqual(sent, ['call', uid, 'dummy', [1, 2, 3]])
