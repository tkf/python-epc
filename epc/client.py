import threading
import itertools

from .server import EPCHandler


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

        # This is what BaseServer.finish_request does:
        address = None  # it is not used, so leave it empty
        self.handler = EPCHandler(self.socket, address, self)

        self.call = self.handler.call
        self.methods = self.handler.methods

        self.handler_thread = threading.Thread(target=self.handler.handle)
        self.handler_thread.start()

    def _ignore(*_):
        """"Do nothing method for `EPCHandler`."""
    add_client = _ignore
    remove_client = _ignore
