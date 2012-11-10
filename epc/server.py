import sys
import logging

from sexpdata import loads, dumps, Symbol, String

from .py3compat import SocketServer, utf8
from .utils import autolog


_logger = logging.getLogger('epc.server')


def setuplogfile(logger=_logger, filename='python-epc.log'):
    ch = logging.FileHandler(filename=filename, mode='w')
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)


def encode_string(string):
    data = string.encode('utf-8')
    datalen = '{0:06x}'.format(len(data) + 1).encode()
    return _JOIN_BYTES([datalen, data, _NEWLINE_BYTE])
_JOIN_BYTES = ''.encode().join
_NEWLINE_BYTE = '\n'.encode()


def encode_object(obj, **kwds):
    return encode_string(dumps(obj, **kwds))


class EPCHandler(SocketServer.StreamRequestHandler):

    # These attribute are defined in `SocketServer.BaseRequestHandler`
    # self.server  : an instance of `EPCServer`
    # self.request :
    # self.client_address

    # These attribute are defined in `SocketServer.StreamRequestHandler`
    # self.connection : = self.request
    # self.rfile      : stream from client
    # self.wfile      : stream to client

    logger = _logger

    def _recv(self):
        while True:
            self.logger.debug('receiving...')
            head = self.rfile.read(6)
            if not head:
                return
            length = int(head, 16)
            data = self.rfile.read(length)
            if len(data) < length:
                raise ValueError('need {0}-length data; got {1}'
                                 .format(length, len(data)))
            self.logger.debug(
                'received: length = %r; data = %r', length, data)
            yield data

    @autolog('debug')
    def _send(self, obj):
        string = encode_object(obj)
        self.wfile.write(string)

    @autolog('debug')
    def handle(self):
        for sexp in self._recv():
            self._handle(sexp)

    @autolog('debug')
    def _handle(self, sexp):
        uid = undefined = []  # default: nil
        try:
            data = loads(sexp.decode('utf-8'))
            (name, uid, args) = (data[0].value(), data[1], data[2:])
            self._send(getattr(self, '_handle_{0}'.format(name))(uid, *args))
        except Exception as err:
            if self.server.debugger:
                traceback = sys.exc_info()[2]
                self.server.debugger.post_mortem(traceback)
            name = 'epc-error' if uid is undefined else 'return-error'
            self._send([Symbol(name), uid, String(repr(err))])

    @autolog('debug')
    def _handle_call(self, uid, meth, args):
        # See: `epc:handler-called-method`
        name = meth.value()
        if name in self.server.funcs:
            func = self.server.funcs[name]
            return [Symbol('return'), uid, func(*args)]
        else:
            return [Symbol('epc-error'), uid,
                    "EPC-ERROR: No such method : {0}".format(name)]

    def _handle_return(self, uid, meth, args):
        # There should be a dict that maps uid to a callback.  This
        # callback is set when calling the method of client from
        # server (here).  This callback is called here with the args.
        pass

    def _handle_methods(self, uid):
        return [Symbol('return'), uid, [
            (Symbol(name), [], String(func.__doc__ or ""))
            # FIXNE: implement arg-specs
            for (name, func)
            in self.server.funcs.items()]]

    # @autolog('debug')
    # def setup(self):
    #     SocketServer.StreamRequestHandler.setup(self)

    # @autolog('debug')
    # def finish(self):
    #     SocketServer.StreamRequestHandler.finish(self)


class EPCDispacher:        # SocketServer.TCPServer is old style class

    logger = _logger

    def __init__(self):
        self.funcs = {}
        self.instance = None

    def register_instance(self, instance, allow_dotted_names=False):
        self.instance = instance
        self.allow_dotted_names = allow_dotted_names
        raise NotImplementedError

    def register_function(self, function, name=None):
        """
        Register function to be called from EPC client.

        :type  function: callable
        :arg   function: Function to publish.
        :type      name: str
        :arg       name: Name by which function is published.

        """
        if name is None:
            name = function.__name__
        self.funcs[name] = function


class EPCCaller:           # SocketServer.TCPServer is old style class

    logger = _logger

    def __init__(self):
        self.callbacks = {}

        def uid():
            i = 0
            while True:
                yield i
                i += 1
        self.uid = uid().next

    def call(self, name, args, callback):
        uid = self.uid()
        self._send_object([Symbol('call'), uid, name] + args)
        self.callbacks[uid] = callback

    def methods(self, name, callback):
        uid = self.uid()
        self._send_object([Symbol('methods'), uid])
        self.callbacks[uid] = callback

    def _send_object(self, obj):
        encode_object(obj)
        # How to send this string??

    # Probably this should go into "client" class?
    # Are server methods allowed to call client's methods?
    # If not, having this class and `return` handler makes no sense.


class EPCServer(SocketServer.TCPServer, EPCDispacher):

    """
    A server class to publish Python functions via EPC protocol.

    >>> server = EPCServer(('localhost', 0))
    >>> def echo(*a):
    ...     return a
    >>> server.register_function(echo)
    >>> server.print_port()                                #doctest: +SKIP
    >>> server.serve_forever()                             #doctest: +SKIP

    See :class:`SocketServer.TCPServer` and :class:`SocketServer.BaseServer`
    to see other methods that can be used.

    """

    logger = _logger

    def __init__(self, server_address,
                 RequestHandlerClass=EPCHandler,
                 bind_and_activate=True,
                 debugger=None):
        # `BaseServer` (super class of `SocketServer`) will set
        # `RequestHandlerClass` to the attribute `self.RequestHandlerClass`.
        # This class is initialize in `BaseServer.finish_request` by
        # `self.RequestHandlerClass(request, client_address, self)`.
        SocketServer.TCPServer.__init__(
            self, server_address, RequestHandlerClass, bind_and_activate)
        EPCDispacher.__init__(self)
        self.logger.debug('-' * 75)
        self.logger.debug(
            "EPCServer is initialized: server_address = %r",
            self.server_address)
        self.set_debugger(debugger)

    def set_debugger(self, debugger):
        """
        Set debugger to run when an error occurs in published method.

        You can also set debugger by passing `debugger` argument to
        the class constructor.

        :type debugger: {'pdb', 'ipdb', None}
        :arg  debugger: type of debugger.

        """
        if debugger == 'pdb':
            import pdb
            self.debugger = pdb
        elif debugger == 'ipdb':
            import ipdb
            self.debugger = ipdb
        else:
            self.debugger = debugger

    @autolog('debug')
    def handle_error(self, request, client_address):
        self.logger.error('handle_error: trying to get traceback.format_exc')
        try:
            import traceback
            self.logger.error('handle_error: \n%s', traceback.format_exc())
        except:
            self.logger.error('handle_error: OOPS')

    def print_port(self, stream=sys.stdout):
        """
        Print port this EPC server runs on.

        As Emacs client reads port number from STDOUT, you need to
        call this just before calling :meth:`serve_forever`.

        :type stream: text stream
        :arg  stream: A stream object to write port on.
                      Default is :data:`sys.stdout`.

        """
        stream.write(str(self.server_address[1]))
        stream.write("\n")
        stream.flush()

# see also: SimpleXMLRPCServer.SimpleXMLRPCDispatcher


def echo_server(address='localhost', port=0):
    server = EPCServer((address, port))
    server.logger.setLevel(logging.DEBUG)
    setuplogfile()

    def echo(*a):
        """Return argument unchanged."""
        return a
    server.register_function(echo)
    return server


if __name__ == '__main__':
    server = echo_server()
    server.print_port()  # needed for Emacs client

    server.serve_forever()
    server.logger.info('exit')
