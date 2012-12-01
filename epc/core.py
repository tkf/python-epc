import logging

from sexpdata import loads, dumps, Symbol

from .py3compat import Queue


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
logger = _get_logger()


def encode_string(string):
    data = string.encode('utf-8')
    datalen = '{0:06x}'.format(len(data) + 1).encode()
    return _JOIN_BYTES([datalen, data, _NEWLINE_BYTE])
_JOIN_BYTES = ''.encode().join
_NEWLINE_BYTE = '\n'.encode()


def encode_object(obj, **kwds):
    return encode_string(dumps(obj, **kwds))


def encode_message(name, *args, **kwds):
    return encode_object([Symbol(name)] + list(args), **kwds)


def unpack_message(bytes):
    data = loads(bytes.decode('utf-8'))
    return (data[0].value(), data[1], data[2:])


def itermessage(read):
    while True:
        head = read(6)
        if not head:
            return
        length = int(head, 16)
        data = read(length)
        if len(data) < length:
            raise ValueError('need {0}-length data; got {1}'
                             .format(length, len(data)))
        yield data


class BlockingCallback(object):

    def __init__(self):
        self.queue = q = Queue.Queue()
        self.callback = lambda x: q.put(('return', x))
        self.errback = lambda x: q.put(('error', x))
        self.cbs = {'callback': self.callback, 'errback': self.errback}

    def result(self, timeout):
        (rtype, reply) = self.queue.get(timeout=timeout)
        if rtype == 'return':
            return reply
        else:
            raise reply
