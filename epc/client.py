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
