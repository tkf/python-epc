import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

rets = [
    sock.connect(('localhost', 50000)),
    sock.sendall('000012(call 10 echo 10)\n'),
    sock.sendall('000012(call 11 echo 10)\n'),
    sock.recv(1024),
]

print rets
