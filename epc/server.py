import SocketServer

from sexpdata import loads, dumps, Symbol, String
from epc.utils import autolog


def getlogger(name='epc'):
    import logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.FileHandler(filename='python-epc.log', mode='w')
    ch.setLevel(logging.DEBUG)

    # # create formatter
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # # add formatter to ch
    # ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger

_logger = getlogger()


def encode_string(string):
    return "{0:06x}{1}\n".format(len(string) + 1, string)


def encode_object(obj, **kwds):
    return encode_string(dumps(obj, **kwds))


class EPCHandler(SocketServer.StreamRequestHandler):

    # These attribute will are by `SocketServer.BaseRequestHandler`
    # self.server  : an instance of `EPCServer`
    # self.request :
    # self.client_address

    # These attribute will are by `SocketServer.StreamRequestHandler`
    # self.connection : = self.server
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
    def _send(self, string):
        self.wfile.write(string)

    @autolog('debug')
    def handle(self):
        for sexp in self._recv():
            data = loads(sexp)
            obj = self._handle(data[0].value(), *data[1:])
            self._send(encode_object(obj))

    @autolog('debug')
    def _handle(self, name, uid, *args):
        try:
            ret = getattr(self, '_handle_{0}'.format(name))(uid, *args)
        except Exception as err:
            ret = [Symbol('return-error'), uid, String(repr(err))]
        return ret

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
            in self.server.funcs.iteritems()]]

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

    logger = _logger

    def __init__(self, server_address,
                 RequestHandlerClass=EPCHandler,
                 bind_and_activate=True):
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

    @autolog('debug')
    def handle_error(self, request, client_address):
        self.logger.error('handle_error: trying to get traceback.format_exc')
        try:
            import traceback
            self.logger.error('handle_error: \n%s', traceback.format_exc())
        except:
            self.logger.error('handle_error: OOPS')

    def print_port(self):
        print self.server_address[1]

# see also: SimpleXMLRPCServer.SimpleXMLRPCDispatcher


def echo_server(address='localhost', port=0):
    server = EPCServer((address, port))

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
