from sexpdata import dumps, Symbol


def encode_string(string):
    data = string.encode('utf-8')
    datalen = '{0:06x}'.format(len(data) + 1).encode()
    return _JOIN_BYTES([datalen, data, _NEWLINE_BYTE])
_JOIN_BYTES = ''.encode().join
_NEWLINE_BYTE = '\n'.encode()


def encode_object(obj, **kwds):
    return encode_string(dumps(obj, **kwds))


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
