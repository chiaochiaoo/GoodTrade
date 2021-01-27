
import socket
import pickle
import pandas as pd

HOST = '10.29.10.132'  # The server's hostname or IP address
PORT = 65421       # The port used by the server

print(socket.gethostname())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
s.connect((HOST, PORT))

connection = True
while connection:
	try:
		s.sendall(b'Alive check')
	except:
		connection = False
		break
	data = b''
	while True:
		try:
			part = s.recv(1024)
		except:
			connection = False
			break
		if not part: break
		data += part
		# if len(part) < 1024:
		# 	break

	k = pickle.loads(data)
	print(k)

print("Server disconnected")



def recvall(sock):
	BUFF_SIZE = 1024 # 4 KiB
	data = b''
	while True:
		part = sock.recv(BUFF_SIZE)
		data += part
		if len(part) < BUFF_SIZE:
			# either 0 or end of data
			break
	return data