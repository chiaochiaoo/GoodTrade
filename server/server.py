import socket
import pickle
import pandas as pd
import threading
from queue import Queue
import time

HOST = '10.29.10.132'  # Standard loopback interface address (localhost)
PORT = 65422        # Port to listen on (non-privileged ports are > 1023)

global client_count
client_count = 0

global client_queue
client_queue = []

global client_queue_lock
client_queue_lock = threading.Lock()

global package 

package = [0]

def client_connection(conn,addr,queue):

	global client_count
	global client_queue
	global client_queue_lock
	global package

	print('Connected by', addr)
	connection = True


	if not isinstance(package[0], int):
		conn.sendall(package[0])

	while connection:
		#data better be pickeled already 
		#pickle.dumps(a)
		data = queue.get()  
		try:
			conn.sendall(data)
		except:
			connection = False

		time.sleep(1)
	
	with client_queue_lock:
		client_queue.remove(queue)

	client_count -=1
	print(addr,"disconnected")
	conn.close()

### one more thread. listen to ppro, pickle, and distribute to each queue. 

def distribute_center(pipe):

	global client_queue
	global client_queue_lock
	global package

	while True:

		#1. listen to pipe. 
		data = pipe.recv()

		data = pickle.dumps(data)

		package[0] = data
		#2. distribute it to all. 
		with client_queue_lock:
			cy = client_queue[:]

		for i in cy:
			i.put(data)


def server_start(pipe):

	global client_queue
	global client_queue_lock
	global client_count

	dc = threading.Thread(target=distribute_center,args=(pipe,), daemon=True)
	dc.start()

	try:
		s=  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((HOST, PORT))
		s.listen()
		while True:
			conn, addr = s.accept()
			client_count+=1
			print('client count:',client_count)
			queue = Queue()
			with client_queue_lock:
				client_queue.append(queue)
			reg = threading.Thread(target=client_connection,args=(conn,addr,queue,), daemon=True)
			reg.start()
	except Exception as e:
		print(e)
		s.close()
		
	s.close()







#Todo - SERVER
	#fullthing together.

#TODO - client

	# quote the shit.
	# interface.

# Process - Server
# thread 1. just liten for new coming.
# thread 2. wait for new scanned data. upon received, send to each clients. 

# Process - Ppro data. 
	# thread 1 Loop through, receive. Upon wrapping up an object, send it to the server process. 
	# thread 2 Control core. 
	# thread 800. fetchdata for symbols 