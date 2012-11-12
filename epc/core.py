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
