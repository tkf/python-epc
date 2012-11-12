import itertools

from .core import itermessage, encode_message, decode_message


class SocketReader(object):

    def __init__(self, sock, recvsize=4096):
        self._sock = sock
        self._recvsize = recvsize
        self._buffer = bytearray()

    def read(self, size):
        while len(self._buffer) < size:
            self._buffer.extend(self._sock.recv(self._recvsize))
        value = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return value


class EPCClient(object):

    def __init__(self, socket_or_address):
        if isinstance(socket_or_address, tuple):
            import socket
            self.socket = socket(socket_or_address)
        else:
            self.socket = socket
        self.reader = SocketReader(self.socket)
        self._messages = itermessage(self.reader.read)
        counter = itertools.count(1)
        self.get_uid = lambda: next(counter)

    def register_function(self, function, name=None):
        raise NotImplementedError

    def call(self, method, *args):
        return self._request('call', method, *args)

    def methods(self):
        return self._request('methods')

    def _request(self, name, *args):
        uid = self.get_uid()
        self.socket.sendall(encode_message(name, uid, *args))
        (name, ruid, rest) = decode_message(next(self._messages))
        assert uid == ruid  # FIXME: support non-serial execution!
        return getattr(self, '_handle_{0}'.format(name))(uid, *rest)

    def _handle_return(self, uid, reply):
        return reply

    def _handle_return_error(self, uid, reply):
        raise ValueError(reply)

    def _handle_epc_error(self, uid, reply):
        raise ValueError(reply)
