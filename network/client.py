
import socket

HOST = '99.231.5.37'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

print(socket.gethostname())
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

print('Received', repr(data))