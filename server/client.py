
import socket
import pickle
import pandas as pd
import time


print(socket.gethostname())
HOST = '10.29.10.132'  # The server's hostname or IP address
PORT = 65421       # The port used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


while True:

	print("Trying to connect to the server")
	connected = False

	while not connected:
		try:
			s.connect((HOST, PORT))
			connected = True
		except:
			print("Cannot connected. Try again in 2 seconds.")
			time.sleep(2)



	connection = True
	print("Connection Successful")
	while connection:
		try:
			s.sendall(b'Alive check')
		except:
			connection = False
			break
		data = []
		while True:
			try:
				part = s.recv(2048)
			except:
				connection = False
				break
			#if not part: break
			data.append(part)
			if len(part) < 2048:
				#try to assemble it, if successful.jump. else, get more. 
				try:
					k = pickle.loads(b"".join(data))
					break
				except:
					pass
		print(k)

	print("Server disconnected")

	#restarted the whole thing 