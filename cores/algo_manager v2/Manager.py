from pannel import *
from tkinter import ttk
from Symbol import *
from TradingPlan import *
from UI import *
from Ppro_in import *
from Ppro_out import *

import socket
import pickle
import time
import multiprocessing
import requests

#May this class bless by the Deus Mechanicus.


def algo_manager_voxcom(pipe):

	#tries to establish commuc
	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		PORT = 65499       # The port used by the server

		try:
			print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					s.connect((HOST, PORT))
					connected = True
				except:
					pipe.send(["msg","Disconnected"])
					print("Cannot connected. Try again in 2 seconds.")
					time.sleep(2)

			connection = True
			pipe.send(["msg","Connected"])
			while connection:

				data = []
				k = None
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
				#s.sendall(pickle.dumps(["ids"]))
				if k!=None:
					pipe.send(["pkg",k])
					print("placed:",k[1][1])
					s.send(pickle.dumps(["Algo placed",k[1][1]]))
			print("Main disconnected")
			pipe.send(["msg","Main disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			print(e)

class Manager:

	def __init__(self,root,goodtrade_pipe=None,ppro_out=None,ppro_in=None):


		self.pipe_ppro_in = ppro_in
		self.pipe_ppro_out = ppro_out
		self.pipe_goodtrade = goodtrade_pipe

		self.symbols = []

		self.symbol_data = {}		
		self.tradingplan = {}

		self.ui = UI(root)
		#self.add_new_tradingplan("AAPL")
		#self.add_new_tradingplan("SDS")

		self.add_new_tradingplan(['Break Any', 'SPY.AM', 10.0, 12.0, 5.0, {'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445}])

		good = threading.Thread(target=self.goodtrade_in, daemon=True)
		good.start()
		
		ppro_in = threading.Thread(target=self.ppro_in, daemon=True)
		ppro_in.start()

	#data part, UI part
	def add_new_tradingplan(self,data):

		#['Any level', 'TEST.AM', 1.0, 2.0, 5.0, {'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445}]

		print(data)

		entryplan = data[0]
		symbol = data[1]
		support = data[2]
		resistence =  data[3]
		risk = data[4]

		if symbol not in self.symbols:

			self.symbol_data[symbol]=Symbol(symbol,support,resistence)  #register in Symbol.
			self.tradingplan[symbol]=TradingPlan(self.symbol_data[symbol],entryplan,INSTANT,NONE,risk,self.pipe_ppro_out)

			self.ui.create_new_entry(self.tradingplan[symbol])
			
			#register in ppro
			self.pipe_ppro_out.send(["Register",symbol])
			#append it to, UI.
		else:
			print("symbols already exists, modifying current parameter.")

	def goodtrade_in(self):
		time.sleep(3)
		count = 0
		while True:
			d = self.pipe_goodtrade.recv()

			if d[0] =="msg":
				try:
					self.ui.main_app_status.set("Main: "+str(d[1]))
					if str(d[1])=="Connected":
						self.ui.main_status["background"] = "#97FEA8"
					else:
						self.ui.main_status["background"] = "red"
				except Exception as e:
					print(e)
			if d[0] =="pkg":
				print("new package arrived",d)

				if d[1][0] == "New order":
					#try:
					self.add_new_tradingplan(d[1][1])
					#except:
					#	print("adding con porra")


	def ppro_order_confirmation(self,data):

		symbol = data["symbol"]
		price = data["price"]
		shares = data["shares"]
		side = data["side"]

		if symbol in self.tradingplan:
			print("order",symbol,"side:",side,"shares",shares,"price",price)

			self.tradingplan[symbol].ppro_process_orders(price,shares,side)
		else:
			print("irrelavant orders detected,",symbol,shares,side)

	def ppro_in(self):
		while True:
			d = self.pipe_ppro_in.recv()

			if d[0] =="status":
				
				try:
					self.ui.ppro_status.set("Ppro : "+str(d[1]))

					if str(d[1])=="Connected":
						self.ui.ppro_status_["background"] = "#97FEA8"
					else:
						self.ui.ppro_status_["background"] = "red"
				except Exception as e:
					print(e)

			if d[0] =="msg":
				print(d[1])

			if d[0] =="order confirm":

				data = d[1]
				symbol = data["symbol"]
				price = data["price"]
				shares = data["shares"]
				side = data["side"]

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_confirm_new_order(price,shares,side)

			if d[0] =="order update":
				data = d[1]
				symbol = data["symbol"]
				bid = data["bid"]
				ask = data["ask"]
				ts = data["timestamp"]

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_update_price(bid,ask,ts)

			if d[0] =="order rejected":

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_order_rejection()

			# if d[0] =="new stoporder":

			# 	self.ppro_append_new_stoporder(d[1])


class Tester:

	def __init__(self,ppro_in):

		

if __name__ == '__main__':


	multiprocessing.freeze_support()

	port =4609

	goodtrade_pipe, receive_pipe = multiprocessing.Pipe()

	algo_voxcom = multiprocessing.Process(target=algo_manager_voxcom, args=(receive_pipe,),daemon=True)
	algo_voxcom.daemon=True
	algo_voxcom.start()

	ppro_in, ppro_pipe_end = multiprocessing.Pipe()

	ppro_in_manager = multiprocessing.Process(target=Ppro_in, args=(port,ppro_pipe_end),daemon=True)
	ppro_in_manager.daemon=True
	ppro_in_manager.start()

	ppro_out, ppro_pipe_end2 = multiprocessing.Pipe()

	ppro_out_manager = multiprocessing.Process(target=Ppro_out, args=(ppro_pipe_end2,port,),daemon=True)
	ppro_out_manager.daemon=True
	ppro_out_manager.start()

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager v2") 
	root.geometry("1920x800")

	Manager(root,goodtrade_pipe,ppro_out,ppro_in)


	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()