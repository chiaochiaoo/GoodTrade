import threading
from modules.Symbol_data_manager import *


class algo_process_manager_client:

	#A big manager. Who has access to all the corresponding grids in the labels.
 	#update each symbols per, 39 seconds? 
	#run every ten seconds. 
	def __init__(self,process_pipe,root):
		#need to track. 1 min range/ volume. 5 min range/volume.
		#self.depositLabel['text'] = 'change the value'
		#fetch this
		#self.gt_pipe = GT_pipe
		self.process_pipe = process_pipe
		self.reg_list = []
		self.black_list = []
		self.lock = {}
		self.root = root
		self.init = False

		#repeat this every 5 seconds.
		#self.receive_start()

	def set_symbols_manager(self,s:Symbol_data_manager):

		##?
		self.data = s

		self.data_list = s.update_list

	def receive_start(self):

		#integrate this within UTIL.
		receive = threading.Thread(name="Thread: Algo manager receiver",target=self.receive_request, daemon=True)
		receive.start()


	def receive_request(self):

		#put the receive in corresponding box.

		while True:
			try:

				info = self.process_pipe.recv()
				type_ = info[0]
			
				if type_ =="Algo placed":
					symbols = info[1]
					#button. 
					for symbol in symbols:
						self.data.algo_breakout_placement[symbol].set("Placed")
				if type_ =="algo manager":
	
					status = info[1]
					if status == "Connected":
						self.data.algo_manager_connected.set("AM:True")
					else:
						self.data.algo_manager_connected.set("AM:False")
				if type_ =="socket":
					status = info[1]
					if status == "Connected":
						self.data.algo_socket.set("Socket:True")
					else:
						self.data.algo_socket.set("Socket:False")

			except Exception as e:
				print(e)

		#grab all info. 

		# take input
	
