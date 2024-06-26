import threading
from modules.Symbol_data_manager import *


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

		self.ppro_status = s.ppro_status

		#########
		self.supoort = s.symbol_data_support
		self.resistance = s.symbol_data_resistance
		self.auto_support_resistance = s.auto_support_resistance

		for i in self.symbols:
			self.register(i)

		self.init_info()
		self.init = True
		self.receive_start()

	def receive_start(self):
		receive = threading.Thread(name="Thread: PPRO info receiver",target=self.receive_request, daemon=True)
		receive.start()

	def receive_request(self):

		#put the receive in corresponding box.

		temp = {}

		
		while True:
			if self.data.start ==True:
				break
			else:
				time.sleep(2)
		print("PPro subthread activated")
		time.sleep(5)


		#cap how much updates it creates.
		while True:

			try:

				# print("Threads:",threading.active_count())
				# for thread in threading.enumerate(): 
				# 	print(thread.name)
				d = self.request.recv()

				status = d[0]

			
				if status == "message":
					print(d[1])
					if d[1] == "Connection established.":
						if self.init:
							self.ppro_status.set("Ppro Status: Connected")
					elif d[1] == "Conection failed. try again in 3 sec.":
						if self.init:
							self.ppro_status.set("Ppro Status: Reconnecting..")
				else:

					#print(d)
					symbol = d[1]
					data = d[2]
					#print("receive",symbol)
					#self.data_list[0][symbol].set(status)

					if symbol in self.symbols:
						self.data_list[symbol_status][symbol].set(status)

						#	pipe.send([status,symbol,price,time,timestamp,
						#   d["high"],d["low"],\d["range"],d["last_5_range"],
						#   d["vol"],d["open"],d["oh"],d["ol"],d["f5r"],d["f5v"]])

						if status == "Connected" or status =="Lagged":
							#print(data)

							for key,item in data.items():
								self.data_list[key][symbol].set(item)
							#print(d)
							#if len(d)-1 == len(self.data_list):

							if 'symbol_price_premarket_high' in data:
								self.resistance[symbol].set(data['symbol_price_premarket_high'])
							if  'symbol_price_premarket_low' in data:
								self.supoort[symbol].set(data['symbol_price_premarket_low'])

								# for i in range(1,len(self.data_list)):
								# 	#print(self.data_list[i][symbol].get())
								# 	self.data_list[i][symbol].set(d[i+1])
									# if self.data_list[i][symbol].get() != d[i+1]:
									#  	self.data_list[i][symbol].set(d[i+1])

								# if self.auto_support_resistance[symbol].get() == 1:
								# 	#timestamp = d[4]
								# 	if 'symbol_price_premarket_high' in data:
								# 		high = data['symbol_price_premarket_high']

								# 	if  'symbol_price_premarket_low' in data:
								# 		low = data['symbol_price_premarket_low']

								# 	#need to check if its the same as previous set. if not, that means it's manually changed. 
								# 	#if timestamp < 570:

								# 	if symbol in temp:
								# 		cur = (self.resistance[symbol].get(),self.supoort[symbol].get())
								# 		if cur != temp[symbol]:
								# 			self.auto_support_resistance[symbol].set(0)
								# 		else:
								# 			temp[symbol] = (high,low)

								# 			self.resistance[symbol].set(high)
								# 			self.supoort[symbol].set(low)
								# 	else:
								# 		temp[symbol] = (high,low)
								# 		self.resistance[symbol].set(high)
								# 		self.supoort[symbol].set(low)
			except Exception as e:
				print("ppro hiccup ",e)

	def init_info(self):
		for i in self.symbols:
			self.data.change_status(i, "Connecting")
			#self.register(i)

	def register(self,symbol):
		#print("register send:",symbol)
		self.request.send("reg"+"_"+symbol)

	def deregister(self,symbol):
		self.request.send("dereg"+"_"+symbol)


	def long(self,symbol):
		self.request.send("long"+"_"+symbol)

	def short(self,symbol):
		self.request.send("short"+"_"+symbol)
	
