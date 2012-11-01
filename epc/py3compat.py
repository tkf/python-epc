import sys
PY3 = (sys.version_info[0] >= 3)

try:
    import SocketServer
except:
    import socketserver as SocketServer
