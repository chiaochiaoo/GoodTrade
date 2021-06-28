import socket
import pickle

import threading
import multiprocessing

import select
import time

import os
from datetime import datetime
import json
#### HERE I NEED SELECT. ### Dua channel. ####



def kill():

	fail = 0
	while True:
		try:
			for i in os.popen("netstat -ano|findstr 65491").read().split("\n"):
				pid=int(i[-8:])
				os.system("taskkill /f /t /pid "+str(pid))
		except:
			fail+=1
			if fail>=3:
				break


def algo_manager_commlink(pipe,util_pipe):

	HOST = 'localhost'  # Standard loopback interface address (localhost)

	PORT_START = 65491
	PORT_END = 65991
	#PORT = 65491        # Port to listen on (non-privileged ports are > 1023)

	p = {}
	p[datetime.now().strftime("%m%d")] = 0


	file_location = "cores/commlink.json"
	#flush the file with 00000
	with open(file_location,"w") as f:
		json.dump(p,f)

	while True:

		PORT = PORT_START	
		s=  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		failed = 0
		success = False
		while True:
			try:
				s.bind((HOST, PORT))
				success = True
				break
			except Exception as e:
				PORT +=1
				#kill()
				if PORT >PORT_END:
					print("algo failed to initialize",e)
					break

		if success:  #save the file
			p[datetime.now().strftime("%m%d")] = PORT
			print("Socket creation successful:",PORT)
			with open(file_location,"w") as f:
				json.dump(p,f)

		if not success:
			break

		util_pipe.send(["socket","Connected"])
		util_pipe.send(["algo manager","Disconnected"])
		print("Waitting for algo manager to connect")
		s.listen()
		
		conn, addr = s.accept()

		util_pipe.send(["algo manager","Connected"])

		print("Algo manager connected.")
		s.setblocking(0)
		Connection = True

		order_list = ["New order"]
		while Connection:
			try:
				#if something comes from pipe.
				if pipe.poll(0):
					data = pipe.recv()
					#print(data)

					if data[0] == "Orders Request add":
						order_list.extend(data[1:])
					elif data[0] == "Orders Request finish":

						if len(data)>1:
							order_list.extend(data[1:])

						#print(order_list)
						data=pickle.dumps(order_list)
						try:
							print(order_list)
							conn.sendall(data)
							order_list = ["New order"]
						except Exception as e:
							print(e)
							Connection=False
							break
					elif data[0] == "New order":
						data=pickle.dumps(data)
						try:
							conn.sendall(data)
						except Exception as e:
							print(e)
							Connection=False
							break
				#if client sends something 
				#print(2)
				if Connection:
					
					try:
						ready = select.select([conn], [], [], 0)
						
						if ready[0]:
							data = []
							while True:
								try:
									part = conn.recv(2048)
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
							#k is the confirmation from client. send it back to pipe.


							print("algo_manager_comms:",pickle.loads(b"".join(data)))
							if k[0] == "Termination":
								util_pipe.send(["Termination"])
								break
							util_pipe.send(pickle.loads(b"".join(data)))
					except Exception as e:
						print(e)
						Connection= False
				#print("running")
				#print(3)
			except Exception as e:
				print(e)
				Connection= False	
	s.close()


def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

if __name__ == '__main__':

	# for i in os.popen("netstat -ano|findstr 65499").read().split("\n"):
	# 	print(i[-8:])
	# 	print(int(i[61:])

	
	server_side_comm, client_side_comm = multiprocessing.Pipe()

	
	#algo_comm_link = multiprocessing.Process(target=algo_manager_commlink, args=(client_side_comm,),daemon=True)

	#algo_comm_link = threading.Thread(target=algo_manager_commlink,args=(client_side_comm,), daemon=True)
	
	
	#algo_comm_link.daemon=True
	#algo_comm_link.start()

	# server_side_comm.send("bsbsbsbs1")
	# server_side_comm.send("bsbsbsbs2")
	# server_side_comm.send("bsbsbsbs3")
	# server_side_comm.send("bsbsbsbs4")
	# algo_comm_link.terminate()
	# algo_comm_link.join()
	algo_manager_commlink(client_side_comm)
	#algo_comm_link.start()
	print("finish")
	while True:
		a=1


