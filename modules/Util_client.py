import threading,queue
import multiprocessing
import time
import re
import pip
import socket
import pickle
import select
from datetime import date
from datetime import datetime

import os.path
import json
#from Symbol_data_manager import *
from modules.Symbol_data_manager import *

try:
    from finviz.screener import Screener
except ImportError:
    pip.main(['install', 'finviz'])
    from finviz.screener import Screener



class util_client:

	def __init__(self,util_request):
		#if a downloading request is already sent. 
		self.util_request = util_request
		self.pannel = None

		self.today  = date.today().strftime("%m%d")

		receive = threading.Thread(name="Util subthread",target=self.receive_request,daemon=True)
		receive.start()

	def set_symbols_manager(self,s: Symbol_data_manager):

		self.symbol_data_manager = s
		self.data = s.data_list
		self.data_status = s.data_ready

		symbols = self.symbol_data_manager.get_list()[:]
	
		self.send_requests(symbols)

		# count = 0
		# for i in symbols:
		# 	if count %5 ==0:
		# 		if count !=0:
		# 			self.util_request.send(l)
		# 		l=["Database Request init"]
		# 	if not self.check_if_file_exist(i):
		# 		l.append(i)
		# 	count+=1
		# if len(l)>1:
		# 	l[0]="Database Request finish"
		# 	self.util_request.send(l)

	def check_if_file_exist(self,symbol):

		if "/" in symbol:
			x = symbol.replace("/","_")
			file = "data/"+x+"_"+self.today+".txt"
		else:
			file = "data/"+symbol[:-3]+"_"+self.today+".txt"

		if os.path.isfile(file):
			print(symbol,"already exisit, loading local copy instd.")
			with open(file) as json_file:
				d = json.load(json_file)

				for key,item in d.items():

					if key!= "rel_volume":
						self.data[key][symbol].set(item)
					else:
						self.data[key][symbol] = item[:] 
			self.data_status[symbol].set(True)

			return True
		return False

	def set_pannel(self,scanner_pannel):
		self.pannel = scanner_pannel


	def send_requests(self,symbols):

		no = ["Database Request"]
		for symbol in symbols:
			if "/" in symbol:
				x = symbol.replace("/","_")
				file = "data/"+x+"_"+self.today+".txt"
			else:
				file = "data/"+symbol[:-3]+"_"+self.today+".txt"
			if os.path.isfile(file):
				print(symbol,"already exisit, loading local copy instd.")
				with open(file) as json_file:
					d = json.load(json_file)

				try:
					for key,item in d.items():
						if key!= "rel_volume":
							self.data[key][symbol].set(item)
						else:
							self.data[key][symbol] = item[:] 

					self.data_status[symbol].set(True)
				except Exception as e:
					print(symbol,"load failed",e)
			else:
				no.append(symbol)

		if len(no)>1:
			self.util_request.send(no)

	def send_request(self,symbol):

		if "/" in symbol:
			x = symbol.replace("/","_")
			file = "data/"+x+"_"+self.today+".txt"
		else:
			file = "data/"+symbol[:-3]+"_"+self.today+".txt"

		#file = "data/"+symbol+"_"+self.today+".txt"

		if os.path.isfile(file):
			#print(symbol,"already exisit, loading local copy instd.")
			with open(file) as json_file:
				d = json.load(json_file)

			for key,item in d.items():
				self.data[key][symbol].set(item)

			self.data_status[symbol].set(True)
		else:
			self.util_request.send(["Database Request",symbol])


	def receive_request(self):

		#self.util_request.send("HELLO!")
		while True:

			d = self.util_request.recv()
			#print("receiving:",d)
			try:
				if len(d)>0:

					#print(d[0])
					######### SCANNER PART ############
					# if d[0]=="Database Request":
					# 	print("send: ",d)
					# 	self.util_request.send(d)

					# elif d[0]=="Finviz Request":

					# 	self.util_request.send(d)

					if d[0]=="NasdaqTrader update":
						#self.pannel.add_nasdaq_labels(d[1])

						try:
							self.pannel.add_nasdaq_labels(d[1])
						except Exception as e:
							print("Error updating NasdaqTrader:",e)

					elif d[0]=="Scanner update":

						try:
							self.pannel.update_TNVscanner(d[1])
						except Exception as e:
							print("Error updating Nasdaq:",e)

					elif d[0]=="http":

						try:
							self.pannel.http_order_TNVscanner(d[1])
						except Exception as e:
							print("Error updating HTTP:",e)

					elif d[0] =="Database Response":

						dic = d[1]
						print("keys keys keys",dic.keys())

						for symbol,da in dic.items():
							#if len(d)-1 == len(self.data):
							#print("setting",symbol)
							for key,item in da.items():
								if key!= "rel_volume":
									self.data[key][symbol].set(item)
								else:
									self.data[key][symbol] = item[:] 
							# for i in range(len(self.data)):
							# 	self.data[i][symbol].set(d[i+1])

							self.data_status[symbol].set(True)

							# file = "data/"+symbol+"_"+self.today+".txt"
							# with open(file, 'w') as outfile:
							# 		json.dump(d, outfile)

								#save the file here.

					elif d[0] =="Finviz Response":
						try:
							self.pannel.add_labels(d)
						except Exception as e:
							print("Error updating finviz:",e)


					########## ALGO PART ###############
					elif d[0] =="Algo placed":
						symbols = d[1]
						#button. 
						for symbol in symbols:
							self.symbol_data_manager.algo_breakout_placement[symbol].set("Placed")
					elif d[0] =="algo manager":
		
						status = d[1]
						if status == "Connected":
							self.symbol_data_manager.algo_manager_connected.set("AM:True")
						else:
							self.symbol_data_manager.algo_manager_connected.set("AM:False")
					elif d[0] =="socket":
						status = d[1]
						if status == "Connected":
							self.symbol_data_manager.algo_socket.set("Socket:True")
						else:
							self.symbol_data_manager.algo_socket.set("Socket:False")


					

					else:
						print("unkown server package:",d)

			except Exception as e:
				print("Util receive unkown:",e,d)



# def server_group(ulti_response):
# 	receiver = threading.Thread(target=algo_server,args=(ulti_response,) daemon=True)
# 	receiver.start()

# 	util_comms(ulti_response)



def algo_server_shell(util_response):

	now  = datetime.now()
	ts = now.hour*60 +now.minute

	#if receiving ts is lagging by more than 2 minutes. disconnect and restart. 

	q = queue.Queue()

	algo_connection = threading.Thread(target=algo_server, args=(util_response,q),daemon=True)
	algo_connection.start()

	

	while True:

		now  = datetime.now()
		cur_ts = now.hour*60 +now.minute


		while q.qsize()>0:
			ts = q.get(timeout=30)
		print("system ts:",cur_ts,"package ts ",ts)

		if ts <= cur_ts -2:
			print("Server lagging detected. Restarting connection. ")
			algo_connection = threading.Thread(target=algo_server, args=(util_response,q),daemon=True)
			algo_connection.start()


		time.sleep(30)


		#data = threading.Thread(target=self.recv, name="Authen thread",daemon=True)
		#data.start()

def algo_server(ulti_response,supervisor):

	k=""
	counter = 0

	ts = 0

	package_ts = 0
	package_reception = 0


	while True:


		try:
			HOST = '10.29.10.132'  # The server's hostname or IP address
			PORT = 65425       # The port used by the server

			print("Trying to connect to the Algo server")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					s.connect((HOST, PORT))
					connected = True
				except:
					#pipe.send(["msg","Cannot connected. Try again in 2 seconds."])
					print("Cannot connect Algo server. Try again in 2 seconds.")
					time.sleep(5)

			connection = True
			#s.setblocking(0)

			print("Algo server Connection Successful")

			while connection:

				now  = datetime.now()

				cur_min_ts = now.hour*60+now.minute
				if now.hour*3600+now.minute *60+now.second - ts>10:
					try:
						s.sendall(("algo requesting update "+str(cur_min_ts)).encode())
						print(now.strftime("%H:%M:%S : ") ,"Algo requesting update:")
					except:
						connection = False
						break

				ready = select.select([s], [], [],10)
				if ready[0]:
					data = []
					while True:

						try:
							part = s.recv(2048)
						except:
							connection = False
							break

						data.append(part)
						if len(part) < 2048:
							
							try:
								k = pickle.loads(b"".join(data))
								break
							except:
								pass

					#problem. when a dead package is received, it will destroy the system.

					print(now.strftime("%H:%M:%S : ") ,"Algo update, package ts:",k[1][1])

					ts = now.hour*3600+now.minute *60+now.second

					if package_ts != k[1][2]:
						package_ts = k[1][2]
						package_reception = 0

						ulti_response.send(k)
					else:
						package_reception+=1

						print(now.strftime("%H:%M:%S : ") ,"older package received:",k[1][1])

						if package_reception>5:
							break

				# else:

				# 	counter+=1
				# 	print( datetime.now().strftime("%H:%M:%S : ") ,"No algo update")


				supervisor.put(now.hour*60+now.minute)
					#ulti_response.send(["Util init"])
			print("Algo Server disconnected")
		except Exception as e:

			print("algo server error",e)

def util_comms(ulti_response): #connects to server for db, nt, and finviz. 

	k=""
	while True:

		HOST = '10.29.10.133'  # The server's hostname or IP address
		PORT = 65424       # The port used by the server

		print("Trying to connect to the Util server")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connected = False

		reg_list = ["Database Request"]


		while not connected:
			try:
				s.connect((HOST, PORT))
				connected = True
			except:
				#pipe.send(["msg","Cannot connected. Try again in 2 seconds."])
				print("Cannot connect Util server. Try again in 2 seconds.")
				time.sleep(5)

		connection = True
		s.setblocking(0)
		print("Util server Connection Successful")
		#ulti_response.send(["Util init"])
		while connection:
			print("Util server: taking data")
			while True:

				try:
					s.sendall(pickle.dumps(['connection check']))
				except:
					connection = False
					break

				ready = select.select([s], [], [], 1)
				if ready[0]:
					data = []
					while True:

						try:
							part = s.recv(2048)
						except:
							connection = False
							break

						data.append(part)
						if len(part) < 2048:
							
							try:
								k = pickle.loads(b"".join(data))
								break
							except:
								pass
					#print("received:",k)
					ulti_response.send(k)

				# i think this part jam the signals. 
				# try:
				# 	if ulti_response.poll(2):
				# 		d = ulti_response.recv()
				# 		if d is not None:
				# 			print(d)
				# 			if d[0] == "Database Request init":
				# 				reg_list.extend(d[1:])
				# 				#print(reg_list)
				# 			elif d[0] == "Database Request finish":
				# 				#print(reg_list)
				# 				reg_list.extend(d[1:])
				# 				print("sending request:",reg_list)

				# 				s.sendall(pickle.dumps(reg_list))
				# 				reg_list = ["Database Request"]
				# 			else:
				# 				print("sending request:",d)
				# 				s.sendall(pickle.dumps(d))
				# except Exception as e:
				# 	print(e)
				# 	connection = False
				# 	break
				time.sleep(1)
				#ulti_response.send(["Util init"])
		print("Server disconnected")


#main part.

if __name__ == '__main__':


	algo_server(None)

