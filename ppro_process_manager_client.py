import threading
from Symbol_data_manager import *


class ppro_process_manager:

	#A big manager. Who has access to all the corresponding grids in the labels.
 	#update each symbols per, 39 seconds? 
	#run every ten seconds. 
	def __init__(self,request_pipe):
		#need to track. 1 min range/ volume. 5 min range/volume.
		#self.depositLabel['text'] = 'change the value'
		#fetch this 
		self.request = request_pipe

		self.reg_list = []
		self.black_list = []
		self.lock = {}

		self.init = False

		#repeat this every 5 seconds.

	def set_symbols_manager(self,s):

		##? 
		self.data = s

		self.data_list = s.update_list
		self.symbols = s.get_list()

		#########
		self.supoort = s.symbol_data_support
		self.resistance = s.symbol_data_resistance
		self.auto_support_resistance = s.auto_support_resistance

		for i in self.symbols:
			self.register(i)

		self.init_info()
		self.receive_start()

	def receive_start(self):
		receive = threading.Thread(name="Thread: Database info receiver",target=self.receive_request, daemon=True)
		receive.start()

	def receive_request(self):

		#put the receive in corresponding box.

		temp = {}

		while True:
			d = self.request.recv()

			status = d[0]

			if status == "message":
				print(d[1])
			else:

				symbol = d[1]

				self.data_list[0][symbol].set(status)

				#	pipe.send([status,symbol,price,time,timestamp,
				#   d["high"],d["low"],\d["range"],d["last_5_range"],
				#   d["vol"],d["open"],d["oh"],d["ol"],d["f5r"],d["f5v"]])

				if status == "Connected":
					if len(d)-1 == len(self.data_list):
						for i in range(1,len(self.data_list)):
							#self.data_list[i][symbol].set(d[i+1])
							if self.data_list[i][symbol].get()!=d[i+1]:
							 	self.data_list[i][symbol].set(d[i+1])

						if self.auto_support_resistance[symbol].get() == 1:
							timestamp = d[4]
							high = d[5]
							low = d[6]

							#need to check if its the same as previous set. if not, that means it's manually changed. 
							if timestamp < 570:

								if symbol in temp:
									cur = (self.resistance[symbol].get(),self.supoort[symbol].get())
									if cur != temp[symbol]:
										self.auto_support_resistance[symbol].set(0)
									else:
										temp[symbol] = (high,low)
										self.resistance[symbol].set(high)
										self.supoort[symbol].set(low)
								else:
									temp[symbol] = (high,low)
									self.resistance[symbol].set(high)
									self.supoort[symbol].set(low)
		#grab all info. 

		# take input

	def init_info(self):
		for i in self.symbols:
			self.data.change_status(i, "Connecting")
			#self.register(i)

	def register(self,symbol):
		print("register send:",symbol)
		self.request.send("reg"+"_"+symbol)

	def deregister(self,symbol):
		self.request.send("dereg"+"_"+symbol)


	def long(self,symbol):
		self.request.send("long"+"_"+symbol)

	def short(self,symbol):
		self.request.send("short"+"_"+symbol)
	
