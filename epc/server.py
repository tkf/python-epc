import SocketServer

from sexpdata import loads, dumps, Symbol, String


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

logger = getlogger()


def encode_string(string):
    return "{0:06x}{1}\n".format(len(string) + 1, string)


def encode_object(obj, **kwds):
    return encode_string(dumps(obj, **kwds))


class EPCHandler(SocketServer.StreamRequestHandler):

    def _recv(self):
        logger.debug('receiving...')
        while True:
            head = self.rfile.read(6)
            if not head:
                return
            length = int(head, 16)
            data = self.rfile.read(length)
            if len(data) < length:
                raise ValueError('need {0}-length data; got {1}'
                                 .format(length, len(data)))
            yield data
            logger.debug(
                'received: length = %r; data = %r', length, data)

    def _send(self, string):
        logger.debug('sending: %r', string)
        self.wfile.write(string)
        logger.debug('sent: %r', string)

    def handle(self):
        for sexp in self._recv():
            data = loads(sexp)
            obj = self._handle(data[0].value(), *data[1:])
            self._send(encode_object(obj))

    def _handle(self, name, uid, *args):
        logger.debug(
            'handle: name = %r; uid = %r; args = %r', name, uid, args)
        try:
            ret = getattr(self, '_handle_{0}'.format(name))(uid, *args)
        except Exception as err:
            ret = [
                Symbol('return-error'), uid,
                String('{0}({1!r})'.format(err.__class__.__name__, err))]
        logger.debug('handle: ret = %r', ret)
        return ret

    def _handle_call(self, uid, meth, *args):
        logger.debug(
            'handle-call: uid = %r, meth = %r, args = %r', uid, meth, args)
        func = self.server.funcs[meth.value()]
        return [Symbol('return'), uid, func(*args)]

    def _handle_return(self, uid, meth, args):
        pass

    def _handle_return_error(self, uid, meth, args):
        pass

    def _handle_epc_error(self, uid, meth, args):
        pass

    def _handle_methods(self, uid, meth, args):
        pass

    # def setup(self):
    #     logger.debug('setup')
    #     SocketServer.StreamRequestHandler.setup(self)

    # def finish(self):
    #     logger.debug('finish')
    #     SocketServer.StreamRequestHandler.finish(self)


class EPCDispacher:

    def __init__(self):
        self.funcs = {}
        self.instance = None

    def register_instance(self, instance, allow_dotted_names=False):
        self.instance = instance
        self.allow_dotted_names = allow_dotted_names

    def register_function(self, function, name=None):
        if name is None:
            name = function.__name__
        self.funcs[name] = function


class EPCServer(SocketServer.TCPServer, EPCDispacher):

    def __init__(self, server_address,
                 RequestHandlerClass=EPCHandler,
                 bind_and_activate=True):
        SocketServer.TCPServer.__init__(
            self, server_address, RequestHandlerClass, bind_and_activate)
        EPCDispacher.__init__(self)
        logger.debug('-' * 75)
        logger.debug(
            "EPCServer is initialized: server_address = %r",
            server_address)

    def handle_error(self, request, client_address):
        logger.error('ERROR!')
        logger.error(
            'handle_error: request = %r; client_address = %r',
            request, client_address)
        logger.error('handle_error: trying to get traceback.format_exc')
        try:
            import traceback
            logger.error('handle_error: \n%s', traceback.format_exc())
        except:
            logger.error('handle_error: OOPS')

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
    print port

    server.serve_forever()

    # for i in range(10):
    #     logger.debug('i = %r', i)
    #     server.handle_request()
    logger.info('exit')
