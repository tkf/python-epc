import threading

from .py3compat import Queue
from .utils import ThreadedIterator
from .core import BlockingCallback
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

    def _recv(self):
        self._recv_iter = ThreadedIterator(EPCHandler._recv(self))
        return self._recv_iter


class EPCClient(EPCCore):

    """
    EPC client class to call remote functions and serve Python functions.
    """

    thread_daemon = True

    def __init__(self, socket_or_address=None, debugger=None):
        if socket_or_address is not None:
            self.connect(socket_or_address)
        EPCCore.__init__(self, debugger)

    def connect(self, socket_or_address):
        """
        Connect to server and start serving registered functions.

        :type socket_or_address: tuple or socket object
        :arg  socket_or_address: A ``(host, port)`` pair to be passed
                                 to `socket.create_connection`, or
                                 a socket object.

        """
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
        self.handler_thread.daemon = self.thread_daemon
        self.handler_thread.start()
        self.handler.wait_until_ready()

    def close(self):
        """Close connection."""
        self.handler._recv_iter.stop()

    def _ignore(*_):
        """"Do nothing method for `EPCHandler`."""
    add_client = _ignore
    remove_client = _ignore

    @staticmethod
    def _blocking_request(call, timeout, *args):
        bc = BlockingCallback()
        call(*args, **bc.cbs)
        return bc.result(timeout=timeout)

    def call_sync(self, name, args, timeout=None):
        """
        Blocking version of :meth:`call`.

        :type    name: str
        :arg     name: Remote function name to call.
        :type    args: list
        :arg     args: Arguments passed to the remote function.
        :type timeout: int or None
        :arg  timeout: Timeout in second.  None means no timeout.

        If the called remote function raise an exception, this method
        raise an exception.  If you give `timeout`, this method may
        raise an `Empty` exception.

        """
        return self._blocking_request(self.call, timeout, name, args)

    def methods_sync(self, timeout=None):
        """
        Blocking version of :meth:`methods`.  See also :meth:`call_sync`.
        """
        return self._blocking_request(self.methods, timeout)
