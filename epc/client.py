import itertools

from sexpdata import Symbol

from .core import itermessage, encode_message, unpack_message
from .utils import ThreadedIterator


class SocketReader(object):

    def __init__(self, sock, recvsize=4096):
        self._sock = sock
        self._recvsize = recvsize
        self._buffer = bytearray()

    def read(self, size):
        while len(self._buffer) < size:
            got = self._sock.recv(self._recvsize)
            if not got:
                return ''
            self._buffer.extend(got)
        value = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return bytes(value)


class EPCClient(object):

    def __init__(self, socket_or_address=None):
        counter = itertools.count(1)
        self.get_uid = lambda: next(counter)
        if socket_or_address is not None:
            self.connect(socket_or_address)

    def connect(self, socket_or_address):
        if isinstance(socket_or_address, tuple):
            import socket
            self.socket = socket.create_connection(socket_or_address)
        else:
            self.socket = socket_or_address
        self.reader = SocketReader(self.socket)
        self._messages = ThreadedIterator(itermessage(self.reader.read))

    def register_function(self, function, name=None):
        raise NotImplementedError

    def call(self, method, args):
        return self._request('call', Symbol(method), args)

    def methods(self):
        return self._request('methods')

    def _request(self, name, *args):
        uid = self.get_uid()
        self.socket.sendall(encode_message(name, uid, *args))
        (name, ruid, rest) = unpack_message(next(self._messages))
        pyname = name.replace('-', '_')
        assert uid == ruid  # FIXME: support non-serial execution!
        return getattr(self, '_handle_{0}'.format(pyname))(uid, *rest)

    def _handle_return(self, uid, reply):
        return reply

    def _handle_return_error(self, uid, reply):
        raise ValueError(reply)

    def _handle_epc_error(self, uid, reply):
        raise ValueError(reply)
