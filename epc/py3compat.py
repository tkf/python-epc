import sys
PY3 = (sys.version_info[0] >= 3)

try:
    import SocketServer
except:
    import socketserver as SocketServer


if PY3:
    utf8 = lambda s: s
else:
    utf8 = lambda s: s.decode('utf-8')

utf8.__doc__ = """
Decode a raw string into unicode object.  Do nothing in Python 3.
"""
