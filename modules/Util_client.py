import threading
import multiprocessing
import time
import re
import pip
import socket
import pickle
import select

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

		receive = threading.Thread(name="Util subthread",target=self.receive_request,daemon=True)
		receive.start()

	def set_symbols_manager(self,s: Symbol_data_manager):

		self.symbol_data_manager = s
		self.data = s.data_list
		self.data_status = s.data_ready

		symbols = self.symbol_data_manager.get_list()[:]
	
		count = 0
		for i in symbols:
			if count %5 ==0:
				if count !=0:
					self.util_request.send(l)
				l=["Database Request"]
			l.append(i)
			count+=1
		if len(l)>1:
			self.util_request.send(l)
			
		
		# self.data = s.data_list
		# self.symbols = s.get_list()[:]
		# print(self.symbols)
		# l = self.symbols.insert(0,"Database Request")
		# print("send::",self.symbols)
		# self.util_request.send(l)

	def set_pannel(self,scanner_pannel):
		self.pannel = scanner_pannel

	def send_request(self,symbol):
		print("db reg ",symbol)
		self.util_request.send(["Database Request",symbol])

	def receive_request(self):

		#self.util_request.send("HELLO!")
		while True:

			d = self.util_request.recv()
			#print("receiving:",d)

			if len(d)>0:

				if d[0]=="Database Request":
					#print("send send send",d)
					self.util_request.send(d)
				elif d[0]=="Finviz Request":

					self.util_request.send(d)

				elif d[0]=="Scanner Update":
					try:
						self.pannel.add_nasdaq_labels(d[1])
					except Exception as e:
						print("Error updating Nasdaq:",e)

				elif d[0] =="Database Response":

					dic = d[1]
					for symbol,d in dic.items():
						if len(d)-1 == len(self.data):
							for i in range(len(self.data)):
								self.data[i][symbol].set(d[i+1])

							self.data_status[symbol].set(True)

				elif d[0] =="Finviz Response":
					try:
						self.pannel.add_labels(d)
					except Exception as e:
						print("Error updating finviz:",e)

		#print(d)
		#check if it is normal type?
		# if d[0]=="Nasdaq":
		# 	self.pannel.add_nasdaq_labels(d)
		# else:
		# 	self.pannel.add_labels(d)

def util_comms(ulti_response): #connects to server for db, nt, and finviz. 

	k=""
	while True:

		HOST = '10.29.10.132'  # The server's hostname or IP address
		PORT = 65424       # The port used by the server


		print("Trying to connect to the Util server")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connected = False

		while not connected:
			try:
				s.connect((HOST, PORT))
				connected = True
			except:
				#pipe.send(["msg","Cannot connected. Try again in 2 seconds."])
				print("Cannot connect Util server. Try again in 2 seconds.")
				time.sleep(2)

		connection = True
		s.setblocking(0)
		print("Util server Connection Successful")
		#ulti_response.send(["Util init"])
		while connection:
			# try:
			# 	s.sendall(b'Alive check')
			# except:
			# 	connection = False
			# 	break
			
			print("Util server: taking data")
			while True:

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

				try:
					if ulti_response.poll(2):
						d = ulti_response.recv()
						if d is not None:
							print("sending request:",d)
							s.sendall(pickle.dumps(d))
					else:
						#print("taking nothing")
				except Exception as e:
					print(e)

				time.sleep(1)
				#ulti_response.send(["Util init"])
		print("Server disconnected")


#main part.

# if __name__ == '__main__':

# 	multiprocessing.freeze_support()

# 	util_request, util_response = multiprocessing.Pipe()

# 	#util_request.send(["Database Request","aapl"])

# 	s=util_client(util_request)
# 	#s.send_request("msft")
# 	util_comms(util_response)
# 	# s = util_client(util_request)
# 	# utility = multiprocessing.Process(target=util_comms, args=(util_response,),daemon=True)
# 	# utility.daemon=True
# 	# utility.start()

# 	while True:
# 		a=1
# 	request_pipe, receive_pipe = multiprocessing.Pipe()
# 	p = multiprocessing.Process(target=multi_processing_scanner, args=(receive_pipe,),daemon=True)
# 	p.daemon=True
# 	p.start()

# 	t = scanner_process_manager(None,request_pipe)
# 	t.send_request()

# 	while True:
# 		a = 1
# 		



