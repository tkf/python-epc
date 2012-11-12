import io

from sexpdata import Symbol

from ..client import EPCClient
from ..core import encode_message, unpack_message
from .utils import BaseTestCase


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


class TestClient(BaseTestCase):

    def setUp(self):
        self.fsock = FakeSocket()
        self.client = EPCClient(self.fsock)

    def set_next_reply(self, *args):
        self.fsock.append(encode_message(*args))

    def sent_message(self, i=0):
        (name, uid, rest) = unpack_message(self.fsock.sent_message[0][6:])
        if name == 'call':
            rest[0] = rest[0].value()
        return [name, uid] + rest

    def check_return(self, desired_return, name, *args):
        uid = 1
        self.set_next_reply('return', uid, desired_return)
        got = getattr(self.client, name)(*args)
        self.assertEqual(got, desired_return)
        sent = self.sent_message()
        self.assertEqual(sent, [name, uid] + list(args))

    def test_call_return(self):
        self.check_return('some value', 'call', 'dummy', [1, 2, 3])

    def test_methods_return(self):
        self.check_return([[Symbol('dummy'), [], "document"]], 'methods')
