import sys
PY3 = (sys.version_info[0] >= 3)

try:
    import SocketServer
except:
    import socketserver as SocketServer

try:
    import SimpleXMLRPCServer
except:
    import xmlrpc.server as SimpleXMLRPCServer

try:
    import Queue
except:
    import queue as Queue


try:
    from contextlib import nested
except ImportError:
    from contextlib import contextmanager

    @contextmanager
    def nested(*managers):
        if managers:
            with managers[0] as ctx:
                with nested(*managers[1:]) as rest:
                    yield (ctx,) + rest
        else:
            yield ()


if PY3:
    utf8 = lambda s: s
else:
    utf8 = lambda s: s.decode('utf-8')

utf8.__doc__ = """
Decode a raw string into unicode object.  Do nothing in Python 3.
"""
