import threading
from modules.Symbol_data_manager import *


class algo_process_manager_client:

	#A big manager. Who has access to all the corresponding grids in the labels.
 	#update each symbols per, 39 seconds? 
	#run every ten seconds. 
	def __init__(self,GT_pipe,process_pipe):
		#need to track. 1 min range/ volume. 5 min range/volume.
		#self.depositLabel['text'] = 'change the value'
		#fetch this
		self.gt_pipe = GT_pipe
		self.process_pipe = process_pipe
		self.reg_list = []
		self.black_list = []
		self.lock = {}

		self.init = False

		#repeat this every 5 seconds.
		self.receive_start()

	def set_symbols_manager(self,s:Symbol_data_manager):

		##?
		self.data = s

		self.data_list = s.update_list

		# self.symbols = s.get_list()
		# self.ppro_status = s.ppro_status

		# #########
		# self.supoort = s.symbol_data_support
		# self.resistance = s.symbol_data_resistance
		# self.auto_support_resistance = s.auto_support_resistance

		# for i in self.symbols:
		# 	self.register(i)

		# self.init_info()
		# self.init = True
		# self.receive_start()

	def receive_start(self):
		receive = threading.Thread(name="Thread: Algo manager receiver",target=self.receive_request, daemon=True)
		receive.start()

	def receive_request(self):

		#put the receive in corresponding box.

		temp = {}

		while True:
			info = self.gt_pipe.recv()
			
			#id, symbol, type, status, description, position, shares, risk$
			message_type= info[0]

			if message_type =="New order":
				id_, symbol, type_, status, description, position, shares, risk = info[1],info[2],info[3],info[4],info[5],info[6],info[7],info[8]
				print("Algo manager :",id_, symbol, type_, status, description, position, shares, risk)

				self.process_pipe.send(info)

				if status == "Pending":

					#set it up. on GoodTrade. 

					if type_ == "Breakup":

						#status, id. symbol.
						self.data.algo_breakout_status[symbol].set(status)
						self.data.algo_breakout_up[symbol].set(id_)

					elif type_ == "Breakdown":
						self.data.algo_breakout_status[symbol].set(status)
						self.data.algo_breakout_down[symbol].set(id_)

			elif message_type =="Confirmed":
				id_ = info[1]
				print("Algo manager:",id_,"confirmed")
				self.process_pipe.send(info)

			
			



		#grab all info. 

		# take input
	
