
import socket
import pickle

HOST = '10.29.10.132'  # The server's hostname or IP address
PORT = 65437       # The port used by the server

print(socket.gethostname())
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = b''
    while True:
	    part = s.recv(4096)
	    data += part
	    if len(part) < 4096:
	    	break

    k = pickle.loads(data)
    print(data)


def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data