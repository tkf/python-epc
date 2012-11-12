import sys
import logging
import itertools

from sexpdata import loads, dumps, Symbol, String

from .py3compat import SocketServer
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


class BaseRemoteError(Exception):
    """
    All exceptions from remote method are derived from this class.
    """


class CallerUnknown(BaseRemoteError):
    """
    Error raised in remote method, but caller of the method is unknown.
    """


class EPCError(BaseRemoteError):
    """
    Error returned by `epc-error` protocol.
    """


class ReturnError(BaseRemoteError):
    """
    Error returned by `return-error` protocol.
    """


class EPCErrorCallerUnknown(CallerUnknown, EPCError):
    """
    Same as :class:`EPCError`, but caller is unknown.
    """


class ReturnErrorCallerUnknown(CallerUnknown, ReturnError):
    """
    Same as :class:`ReturnError`, but caller is unknown.
    """


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

    @autolog('debug')
    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        self.server.add_client(self)

    @autolog('debug')
    def finish(self):
        try:
            SocketServer.StreamRequestHandler.setup(self)
        finally:
            self.server.remove_client(self)

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
            pyname = name.replace('-', '_')
            self._send(getattr(self, '_handle_{0}'.format(pyname))(uid, *args))
        except Exception as err:
            if self.handle_error(err):
                return
            if self.server.debugger:
                traceback = sys.exc_info()[2]
                self.server.debugger.post_mortem(traceback)
            if isinstance(err, BaseRemoteError):  # do not send error back
                return
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

    def _handle_methods(self, uid):
        return [Symbol('return'), uid, [
            (Symbol(name), [], String(func.__doc__ or ""))
            # FIXNE: implement arg-specs
            for (name, func)
            in self.server.funcs.items()]]

    def _handle_return(self, uid, reply):
        self.server.handle_return(uid, reply)

    def _handle_return_error(self, uid, reply):
        self.server.handle_return_error(uid, reply)

    def _handle_epc_error(self, uid, reply):
        self.server.handle_epc_error(uid, reply)

    def handle_error(self, err):
        """
        Handle error which is not handled by errback.

        Return True from this function means that error is properly
        handled, so the error is not sent to client.  Do not confuse
        this with :meth:`SocketServer.BaseServer.handle_error`.  This
        method is for handling error for each client, not for entire
        server.  Default implementation does nothing.  Therefore,
        error occurs in this server is sent to client always.

        """

    def call(self, name, *args, **kwds):
        """
        Call method connected to this handler.

        :type     name: str
        :arg      name: Method name to call.
        :type     args: list
        :arg      args: Arguments for remote method to call.
        :type callback: callable
        :arg  callback: A function to be called with returned value of
                        the remove method.
        :type  errback: callable
        :arg   errback: A function to be called with an error occurred
                        in the remote method.  It is either an instance
                        of :class:`ReturnError` or :class:`EPCError`.

        """
        self.server.call(self, name, *args, **kwds)

    def methods(self, *args, **kwds):
        """
        Request info of callable remote methods.

        Arguments for :meth:`call` except for `name` can be applied to
        this function too.

        """
        self.server.methods(self, *args, **kwds)


class EPCClientManager:

    def __init__(self):
        self.clients = []
        """
        A list of :class:`EPCHandler` object for connected clients.
        """

    def add_client(self, handler):
        self.clients.append(handler)
        self.handle_client_connect(handler)

    def remove_client(self, handler):
        self.clients.remove(handler)
        self.handle_client_disconnect(handler)

    def handle_client_connect(self, handler):
        """
        Handler which is called with a newly connected `client`.

        :type  handler: :class:`EPCHandler`
        :arg   handler: Object for handling request from the client.

        Default implementation does nothing.

        """

    def handle_client_disconnect(self, handler):
        """
        Handler which is called with a disconnected `client`.

        :type  handler: :class:`EPCHandler`
        :arg   handler: Object for handling request from the client.

        Default implementation does nothing.

        """


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

    def __init__(self):
        self.callbacks = {}
        self.errbacks = {}
        counter = itertools.count(1)
        self.get_uid = lambda: next(counter)

    def _set_callbacks(self, uid, callback, errback):
        self.callbacks[uid] = callback
        self.errbacks[uid] = errback

    def _pop_callbacks(self, uid):
        return (self.callbacks.pop(uid), self.errbacks.pop(uid))

    def call(self, handler, name, args=[], callback=None, errback=None):
        uid = self.get_uid()
        handler._send([Symbol('call'), uid, Symbol(name), args])
        self._set_callbacks(uid, callback, errback)

    def methods(self, handler, callback=None, errback=None):
        uid = self.get_uid()
        handler._send([Symbol('methods'), uid])
        self._set_callbacks(uid, callback, errback)

    def handle_return(self, uid, reply):
        if not (isinstance(uid, int) and uid in self.callbacks):
            raise CallerUnknown(reply)
        (callback, _) = self._pop_callbacks(uid)
        if callback is not None:
            callback(reply)

    def _handle_error_reply(self, uid, reply, eclass, notfound):
        if not (isinstance(uid, int) and uid in self.errbacks):
            raise notfound(reply)
        (_, errback) = self._pop_callbacks(uid)
        error = eclass(reply)
        if errback is None:
            raise error
        else:
            errback(error)

    def handle_return_error(self, uid, reply):
        self._handle_error_reply(uid, reply, ReturnError,
                                 ReturnErrorCallerUnknown)

    def handle_epc_error(self, uid, reply):
        self._handle_error_reply(uid, reply, EPCError,
                                 EPCErrorCallerUnknown)


class EPCServer(SocketServer.TCPServer, EPCClientManager,
                EPCDispacher, EPCCaller):

    """
    A server class to publish functions and call functions via EPC protocol.

    To publish Python functions, all you need is
    :meth:`register_function() <EPCDispacher.register_function>`,
    :meth:`print_port` and
    :meth:`serve_forever() <SocketServer.BaseServer.serve_forever>`.

    >>> server = EPCServer(('localhost', 0))
    >>> def echo(*a):
    ...     return a
    >>> server.register_function(echo)
    >>> server.print_port()                                #doctest: +SKIP
    >>> server.serve_forever()                             #doctest: +SKIP

    To call client's method, use :attr:`clients <EPCClientManager.clients>`,
    to get client handler and use its :meth:`EPCHandler.call` and
    :meth:`EPCHandler.methods` methods to communicate with connected client.

    >>> handler = server.clients[0]                        #doctest: +SKIP
    >>> def callback(reply):
    ...     print(reply)
    >>> handler.call('method_name', ['arg-1', 'arg-2', 'arg-3'],
    ...              callback)                             #doctest: +SKIP

    See :class:`SocketServer.TCPServer` and :class:`SocketServer.BaseServer`
    for other usable methods.

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
        EPCClientManager.__init__(self)
        EPCDispacher.__init__(self)
        EPCCaller.__init__(self)
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


class ThreadingEPCServer(SocketServer.ThreadingMixIn, EPCServer):
    """
    Class :class:`EPCServer` mixed with :class:`SocketServer.ThreadingMixIn`.

    Use this class when combining EPCServer with other Python module
    which has event loop, such as GUI modules.  For example, see
    `examples/gtk/server.py`_ for how to use this class with GTK

    .. _examples/gtk/server.py:
       https://github.com/tkf/python-epc/blob/master/examples/gtk/server.py

    """


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
