import threading
import itertools

from .py3compat import Queue
from .server import EPCHandler, EPCCore


class EPCClientHandler(EPCHandler):

    # In BaseRequestHandler, everything happen in `.__init__()`.
    # Let's defer it to `.start()`.

    def __init__(self, *args):
        self._args = args
        self._ready = Queue.Queue()

    def start(self):
        EPCHandler.__init__(self, *self._args)

    def setup(self):
        EPCHandler.setup(self)
        self._ready.put(True)

    def wait_until_ready(self):
        self._ready.get()


class EPCClient(EPCCore):

    def __init__(self, socket_or_address=None, debugger=None):
        counter = itertools.count(1)
        self.get_uid = lambda: next(counter)
        if socket_or_address is not None:
            self.connect(socket_or_address)
        self.set_debugger(debugger)

    def connect(self, socket_or_address):
        if isinstance(socket_or_address, tuple):
            import socket
            self.socket = socket.create_connection(socket_or_address)
        else:
            self.socket = socket_or_address

        # This is what BaseServer.finish_request does:
        address = None  # it is not used, so leave it empty
        self.handler = EPCClientHandler(self.socket, address, self)

        self.call = self.handler.call
        self.methods = self.handler.methods

        self.handler_thread = threading.Thread(target=self.handler.start)
        self.handler_thread.start()
        self.handler.wait_until_ready()

    def _ignore(*_):
        """"Do nothing method for `EPCHandler`."""
    add_client = _ignore
    remove_client = _ignore

    @staticmethod
    def _blocking_request(call, timeout, *args):
        q = Queue.Queue()
        call(*args,
             callback=lambda x: q.put(('return', x)),
             errback=lambda x: q.put(('error', x)))
        (rtype, reply) = q.get(timeout=timeout)
        if rtype == 'return':
            return reply
        else:
            raise reply

    def call_block(self, name, args, timeout=None):
        return self._blocking_request(self.call, timeout, name, args)

    def methods_block(self, timeout=None):
        return self._blocking_request(self.methods, timeout)
