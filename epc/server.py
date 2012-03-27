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
            yield data
            self.logger.debug(
                'received: length = %r; data = %r', length, data)

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
    def _handle_call(self, uid, meth, *args):
        func = self.server.funcs[meth.value()]
        return [Symbol('return'), uid, func(*args)]

    def _handle_return(self, uid, meth, args):
        pass

    def _handle_return_error(self, uid, meth, args):
        pass

    def _handle_epc_error(self, uid, meth, args):
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


class EPCDispacher:

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


class EPCServer(SocketServer.TCPServer, EPCDispacher):

    logger = _logger

    def __init__(self, server_address,
                 RequestHandlerClass=EPCHandler,
                 bind_and_activate=True):
        SocketServer.TCPServer.__init__(
            self, server_address, RequestHandlerClass, bind_and_activate)
        EPCDispacher.__init__(self)
        self.logger.debug('-' * 75)
        self.logger.debug(
            "EPCServer is initialized: server_address = %r",
            server_address)

    @autolog('debug')
    def handle_error(self, request, client_address):
        self.logger.error('handle_error: trying to get traceback.format_exc')
        try:
            import traceback
            self.logger.error('handle_error: \n%s', traceback.format_exc())
        except:
            self.logger.error('handle_error: OOPS')

# see also: SimpleXMLRPCServer.SimpleXMLRPCDispatcher


def echo_server(address='localhost', port=50000):
    server = EPCServer((address, port))

    def echo(*a):
        return a
    server.register_function(echo)
    return server


if __name__ == '__main__':
    port = 50000
    server = echo_server(port=port)
    print port  # needed for Emacs client

    server.serve_forever()
    server.logger.info('exit')
