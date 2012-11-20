import sys
import logging
import itertools
import threading

from sexpdata import Symbol, String

from .py3compat import SocketServer
from .utils import autolog, LockingDict, newthread, callwith
from .core import encode_message, unpack_message, BlockingCallback


def _get_logger():
    """
    Generate a logger with a stream handler.
    """
    logger = logging.getLogger('epc')
    hndlr = logging.StreamHandler()
    hndlr.setLevel(logging.INFO)
    hndlr.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logger.addHandler(hndlr)
    return logger
_logger = _get_logger()


def setuplogfile(logger=_logger, filename='python-epc.log'):
    ch = logging.FileHandler(filename=filename, mode='w')
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)


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


class EPCClosed(Exception):
    """
    Trying to send to a closed socket.
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
        self.callmanager = EPCCallManager()
        self.server.add_client(self)

    @autolog('debug')
    def finish(self):
        try:
            SocketServer.StreamRequestHandler.finish(self)
        finally:
            self.server.remove_client(self)

    def _rfile_read_safely(self, size):
        try:
            return self.rfile.read(size)
        except (AttributeError, ValueError):
            if self.rfile.closed:
                # Calling read on closed socket raises
                # AttributeError in 2.x and ValueError in 3.x.
                # http://bugs.python.org/issue9177
                raise StopIteration
            else:
                raise  # if not, just re-raise it.

    def _recv(self):
        while True:
            self.logger.debug('receiving...')
            head = self._rfile_read_safely(6)
            if not head:
                return
            length = int(head, 16)
            data = self._rfile_read_safely(length)
            if len(data) < length:
                raise ValueError('need {0}-length data; got {1}'
                                 .format(length, len(data)))
            self.logger.debug(
                'received: length = %r; data = %r', length, data)
            yield data

    @autolog('debug')
    def _send(self, *args):
        string = encode_message(*args)
        try:
            self.wfile.write(string)
        except (AttributeError, ValueError):
            # See also: :meth:`_rfile_read_safely`
            raise EPCClosed

    @autolog('debug')
    def handle(self):
        for sexp in self._recv():
            self._handle(sexp)

    @autolog('debug')
    def _handle(self, sexp):
        uid = undefined = []  # default: nil
        try:
            (name, uid, args) = unpack_message(sexp)
            pyname = name.replace('-', '_')
            getattr(self, '_validate_{0}'.format(pyname))(uid, args)
            handler = getattr(self, '_handle_{0}'.format(pyname))
            reply = handler(uid, *args)
            if reply is not None:
                self._send(*reply)
        except Exception as err:
            if self.handle_error(err):
                return
            if self.server.debugger:
                traceback = sys.exc_info()[2]
                self.server.debugger.post_mortem(traceback)
            name = 'epc-error' if uid is undefined else 'return-error'
            self._send(name, uid, repr(err))

    @autolog('debug')
    def _handle_call(self, uid, meth, args):
        # See: `epc:handler-called-method`
        name = meth.value()
        if name in self.server.funcs:
            func = self.server.funcs[name]
            return ['return', uid, func(*args)]
        else:
            return ['epc-error', uid,
                    "EPC-ERROR: No such method : {0}".format(name)]

    def _handle_methods(self, uid):
        return ['return', uid, [
            (Symbol(name), [], String(func.__doc__ or ""))
            # FIXNE: implement arg-specs
            for (name, func)
            in self.server.funcs.items()]]

    def _handle_return(self, uid, reply):
        self.callmanager.handle_return(uid, reply)

    def _handle_return_error(self, uid, reply=None, *_):
        self.callmanager.handle_return_error(uid, reply)

    def _handle_epc_error(self, uid, reply=None, *_):
        self.callmanager.handle_epc_error(uid, reply)

    _epc_error_template = \
        "(%s %d ...): Got %s arguments in the reply: %r"

    def _validate_call(self, uid, args, num_expect=2, name='call'):
        len_args = len(args)
        if len_args == num_expect:
            return
        elif len_args < num_expect:
            message = 'Not enough arguments {0!r}'.format(args)
        else:
            message = 'Too many arguments {0!r}'.format(args)
        self._send("epc-error", uid, message)
        raise EPCError('({0} {1} ...): {2}'.format(name, uid, message))

    def _validate_methods(self, uid, args):
        self._validate_call(uid, args, 0, 'methods')

    def _validate_return(self, uid, args):
        len_args = len(args)
        error = lambda x: self._epc_error_template % ('return', uid, x, args)
        if len_args == 0:
            message = error('not enough')
        elif len_args > 1:
            message = error('too many')
        else:
            return
        self.logger.error(message)
        self._handle_epc_error(uid, message)
        raise EPCError(message)

    def _validate_return_error(self, uid, args):
        self._log_extra_argument_error('return-error', uid, args)

    def _validate_epc_error(self, uid, args):
        self._log_extra_argument_error('epc-error', uid, args)

    def _log_extra_argument_error(self, name, uid, args):
        if len(args) > 1:
            self.logger.error(self._epc_error_template,
                              'return-error', uid, 'too many', args)

    def handle_error(self, err):
        """
        Handle error which is not handled by errback.

        :type  err: Exception
        :arg   err: An error not handled by other mechanisms.
        :rtype: boolean

        Return True from this function means that error is properly
        handled, so the error is not sent to client.  Do not confuse
        this with :meth:`SocketServer.BaseServer.handle_error`.  This
        method is for handling error for each client, not for entire
        server.  Default implementation logs the error and returns
        True if the error is coming from remote [#]_ or returns False
        otherwise. Therefore, only the error occurs in this handler
        class is sent to remote.

        .. [#] More specifically, it returns True if `err` is an
           instance of :class:`BaseRemoteError` or :class:`EPCClosed`.

        """
        self.logger.error(repr(err))
        if isinstance(err, (BaseRemoteError, EPCClosed)):
            # BaseRemoteError: do not send error back
            # EPCClosed: no exception from thread
            return True

    def call(self, name, *args, **kwds):
        """
        Call method connected to this handler.

        :type     name: str
        :arg      name: Method name to call.
        :type     args: list
        :arg      args: Arguments for remote method to call.
        :type callback: callable
        :arg  callback: A function to be called with returned value of
                        the remote method.
        :type  errback: callable
        :arg   errback: A function to be called with an error occurred
                        in the remote method.  It is either an instance
                        of :class:`ReturnError` or :class:`EPCError`.

        """
        self.callmanager.call(self, name, *args, **kwds)

    def methods(self, *args, **kwds):
        """
        Request info of callable remote methods.

        Arguments for :meth:`call` except for `name` can be applied to
        this function too.

        """
        self.callmanager.methods(self, *args, **kwds)

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


class ThreadingEPCHandler(EPCHandler):

    def _handle(self, sexp):
        newthread(self, target=EPCHandler._handle, args=(self, sexp)).start()


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

        This method returns the given `function` as-is, so that you
        can use it as a decorator.

        """
        if name is None:
            name = function.__name__
        self.funcs[name] = function
        return function


class EPCCallManager:

    Dict = LockingDict  # FIXME: make it configurable from server class.
    """
    Dictionary class used to store callbacks.
    """

    def __init__(self):
        self.callbacks = self.Dict()
        counter = itertools.count(1)
        self.get_uid = callwith(threading.Lock())(lambda: next(counter))
        # Wrapping by threading.Lock is useless for non-threading
        # handler.  Probably it is better to make it optional.

    def call(self, handler, name, args=[], callback=None, errback=None):
        uid = self.get_uid()
        self.callbacks[uid] = (callback, errback)
        handler._send('call', uid, Symbol(name), args)

    def methods(self, handler, callback=None, errback=None):
        uid = self.get_uid()
        self.callbacks[uid] = (callback, errback)
        handler._send('methods', uid)

    def handle_return(self, uid, reply):
        try:
            (callback, _) = self.callbacks.pop(uid)
        except (KeyError, TypeError):
            raise CallerUnknown(reply)
        if callback is not None:
            callback(reply)

    def _handle_error_reply(self, uid, reply, eclass, notfound):
        try:
            (_, errback) = self.callbacks.pop(uid)
        except (KeyError, TypeError):
            raise notfound(reply)
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


class EPCCore(EPCDispacher):

    """
    Core methods shared by `EPCServer` and `EPCClient`.
    """

    def __init__(self, debugger):
        EPCDispacher.__init__(self)
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


class EPCServer(SocketServer.TCPServer, EPCClientManager,
                EPCCore):

    """
    A server class to publish functions and call functions via EPC protocol.

    To publish Python functions, all you need is
    :meth:`register_function`,
    :meth:`print_port` and
    :meth:`serve_forever() <SocketServer.BaseServer.serve_forever>`.

    >>> server = EPCServer(('localhost', 0))
    >>> def echo(*a):
    ...     return a
    >>> server.register_function(echo)                 #doctest: +ELLIPSIS
    <function echo at 0x...>
    >>> server.print_port()                                #doctest: +SKIP
    9999
    >>> server.serve_forever()                             #doctest: +SKIP

    To call client's method, use :attr:`clients <EPCClientManager.clients>`
    attribute to get client handler and use its :meth:`EPCHandler.call` and
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
        EPCCore.__init__(self, debugger)
        self.logger.debug('-' * 75)
        self.logger.debug(
            "EPCServer is initialized: server_address = %r",
            self.server_address)

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

    def __init__(self, *args, **kwds):
        kwds.update(RequestHandlerClass=ThreadingEPCHandler)
        EPCServer.__init__(self, *args, **kwds)


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
