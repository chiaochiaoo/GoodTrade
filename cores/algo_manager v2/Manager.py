from pannel import *
from tkinter import ttk
from Symbol import *
from TradingPlan import *
from UI import *
from Ppro_in import *
from Ppro_out import *
from constant import *

from Util_functions import *
import sys
import socket
import pickle
import time
import multiprocessing
import requests
from datetime import datetime
#May this class bless by the Deus Mechanicus.

try:
	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+".txt", "x")
except:
	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+".txt", "w")
f.close()


TEST = True
def algo_manager_voxcom(pipe):

	#tries to establish commuc
	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		PORT = 65499       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					s.connect((HOST, PORT))
					connected = True
				except:
					pipe.send(["msg","Disconnected"])
					log_print("Cannot connected. Try again in 2 seconds.")
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
					log_print("placed:",k[1][1])
					s.send(pickle.dumps(["Algo placed",k[1][1]]))
			log_print("Main disconnected")
			pipe.send(["msg","Main disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)
def algo_manager_voxcom2(pipe):

	#tries to establish commuc
	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		PORT = 65499       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					s.connect((HOST, PORT))
					s.send(pickle.dumps(["Connection","Connected"]))
					connected = True
				except:
					pipe.send(["msg","Disconnected"])
					log_print("Cannot connected. Try again in 3 seconds.")
					time.sleep(3)

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
						except Exception as e:
							log_print(e)
				#s.sendall(pickle.dumps(["ids"]))
				if k!=None:
					pipe.send(["pkg",k])
					#log_print("placed:",k[1][1])
					s.send(pickle.dumps(["Algo placed",k[1][1]]))
			log_print("Main disconnected")
			pipe.send(["msg","Disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)

def logging(pipe):

	f = open(datetime.now().strftime("%d/%m")+".txt", "w")
	while True:
		string = pipe.recv()
		time_ = datetime.now().strftime("%H:%M:%S")
		log_print(string)
		f.write(time_+" :"+string)
	f.close()

class Manager:

	def __init__(self,root,goodtrade_pipe=None,ppro_out=None,ppro_in=None,TEST_MODE=False):


		self.pipe_ppro_in = ppro_in
		self.pipe_ppro_out = ppro_out
		self.pipe_goodtrade = goodtrade_pipe

		self.test_mode = TEST_MODE

		self.symbols = []

		self.symbol_data = {}		
		self.tradingplan = {}

		self.ui = UI(root,self)
		#self.add_new_tradingplan("AAPL")
		#self.add_new_tradingplan("SDS")

		#self.add_new_tradingplan(['Break Any', 'SPY.AM', 10.0, 12.0, 5.0, {'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445}])

		good = threading.Thread(target=self.goodtrade_in, daemon=True)
		good.start()
		
		ppro_in = threading.Thread(target=self.ppro_in, daemon=True)
		ppro_in.start()

		timer = threading.Thread(target=self.timer, daemon=True)
		timer.start()

		#if Testerx==True:
			

	#data part, UI part
	def add_new_tradingplan(self,data,TEST_MODE):

		#['Any level', 'TEST.AM', 1.0, 2.0, 5.0, {'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445}]

		entryplan = data[0]
		symbol = data[1]
		support = data[2]
		resistence =  data[3]
		risk = data[4]
		stats = data[5]

		if symbol not in self.symbols:

			self.symbol_data[symbol]=Symbol(symbol,support,resistence,stats)  #register in Symbol.
			self.tradingplan[symbol]=TradingPlan(self.symbol_data[symbol],entryplan,INSTANT,NONE,risk,self.pipe_ppro_out,TEST_MODE)

			self.ui.create_new_entry(self.tradingplan[symbol])
			
			#register in ppro
			self.pipe_ppro_out.send(["Register",symbol])

			self.symbols.append(symbol)
			#append it to, UI.
		else:
			log_print("symbols already exists, modifying current parameter.")

	def timer(self):

		#570  34200
		#960  57600 
		time.sleep(2)
		#now = datetime.now()
		timestamp = 34200

		log_print("timer start")
		while True:
			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second
			remain = timestamp - ts
			#log_print(timestamp,ts)
			minute = remain//60
			seconds = remain%60

			if minute>0:
				self.ui.algo_timer_string.set(str(minute)+" minutes and "+str(seconds)+" seconds")
			else:
				self.ui.algo_timer_string.set(str(seconds)+" seconds")
			if remain<0:
				log_print("Trigger")
				break

			time.sleep(1)

		self.ui.algo_timer_string.set("Deployed")
		self.deploy_all()

	def goodtrade_in(self):
		time.sleep(3)
		count = 0
		while True:
			d = self.pipe_goodtrade.recv()

			if d[0] =="msg":
				try:
					self.ui.main_app_status.set(str(d[1]))
					if str(d[1])=="Connected":
						self.ui.main_status["background"] = "#97FEA8"
					else:
						self.ui.main_status["background"] = "red"
				except Exception as e:
					log_print(e)
			if d[0] =="pkg":
				log_print("new package arrived",d)

				if d[1][0] == "New order":
					#try
					self.add_new_tradingplan(d[1][1],self.test_mode)
					#except:
					#	log_print("adding con porra")

	def ppro_order_confirmation(self,data):

		symbol = data["symbol"]
		price = data["price"]
		shares = data["shares"]
		side = data["side"]

		if symbol in self.tradingplan:
			log_print("order",symbol,"side:",side,"shares",shares,"price",price)

			self.tradingplan[symbol].ppro_process_orders(price,shares,side)
		else:
			log_print("irrelavant orders detected,",symbol,shares,side)

	def ppro_in(self):
		while True:
			d = self.pipe_ppro_in.recv()

			#log_print("Ppro in:",d)

			if d[0] =="status":
				
				try:
					self.ui.ppro_status.set(str(d[1]))

					if str(d[1])=="Connected":
						self.ui.ppro_status_["background"] = "#97FEA8"
					else:
						self.ui.ppro_status_["background"] = "red"
				except Exception as e:
					log_print(e)

			if d[0] =="msg":
				log_print(d[1])

			if d[0] =="order confirm":

				data = d[1]
				symbol = data["symbol"]
				price = data["price"]
				shares = data["shares"]
				side = data["side"]

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_process_orders(price,shares,side)

				#if TEST:
					#log_print(self.tradingplan[symbol].data)

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

	def set_all_tp(self):

		timer=self.ui.all_timer.get()
		ep=self.ui.all_enp.get()
		et=self.ui.all_ent.get()
		managment=self.ui.all_mana.get() 

		for d in self.tradingplan.values():
			d.tkvars[ENTRYPLAN].set(ep)
			d.tkvars[ENTYPE].set(et)
			d.tkvars[MANAGEMENTPLAN].set(managment)
			d.tkvars[TIMER].set(timer)

	def set_selected_tp(self):

		timer=self.ui.all_timer.get()
		ep=self.ui.all_enp.get()
		et=self.ui.all_ent.get()
		managment=self.ui.all_mana.get() 

		for d in self.tradingplan.values():
			if d.tkvars[SELECTED].get()==True:
				d.tkvars[ENTRYPLAN].set(ep)
				d.tkvars[ENTYPE].set(et)
				d.tkvars[MANAGEMENTPLAN].set(managment)
				d.tkvars[TIMER].set(timer)
	def deploy_all(self):
		for d in self.tradingplan.values():
			d.deploy()

	def withdraw_all(self):
		for d in self.tradingplan.values():
			d.cancle_deployment()

	def flatten_all(self):
		for d in self.tradingplan.values():
			d.flatten_cmd()

	def cancel_all(self):
		for d in self.tradingplan.values():
			d.cancel_algo()
	
class Tester:

	def __init__(self,receive_pipe,ppro_in,ppro_out):


		self.sec = 0
		self.bid=0
		self.ask=0

		self.root = tk.Toplevel(width=780,height=250)
		self.gt = receive_pipe
		self.ppro = ppro_in

		self.ppro_out = ppro_out

		self.pos  = ""
		self.share = 0
		self.change_sum = 0

		self.wait_time = 1

		# self.init= tk.Button(self.root ,text="Register",width=10,bg="#5BFF80",command=self.start_test)
		# self.init.grid(column=1,row=1) m

		self.price = tk.DoubleVar(value=412.55)

		tk.Entry(self.root ,textvariable=self.price,width=10).grid(column=1,row=2)	

		tk.Button(self.root ,text="up",command=self.price_up).grid(column=1,row=4)	
		tk.Button(self.root ,text="stay",command=self.price_stay).grid(column=2,row=4)	
		tk.Button(self.root ,text="down",command=self.price_down).grid(column=3,row=4)	

		tk.Button(self.root ,text="TimeX1",command=self.time_facotr_1).grid(column=1,row=3)
		tk.Button(self.root ,text="TimeX10",command=self.time_factor_10).grid(column=2,row=3)	

		tk.Button(self.root ,text="up 0.1",command=self.price_up_little).grid(column=1,row=5)
		tk.Button(self.root ,text="down 0.1",command=self.price_down_little).grid(column=2,row=5)	

		tk.Button(self.root ,text="up 1",command=self.price_upx).grid(column=1,row=6)	
		tk.Button(self.root ,text="down 1",command=self.price_downx).grid(column=2,row=6)	

		tk.Button(self.root ,text="add 1 share",command=self.add1).grid(column=1,row=7)	
		tk.Button(self.root ,text="sub 1 share",command=self.sub1).grid(column=2,row=7)	
		self.gt.send(["pkg",['New order', [BREAKANY, 'SPY.AM', 412.5, 412.6, 50.0, {'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441}]]])

		time.sleep(1)
		wish_granter = threading.Thread(target=self.wish, daemon=True)
		wish_granter.start()

		price_changer = threading.Thread(target=self.price_changer, daemon=True)
		price_changer.start()

	def wish(self): #a sperate process. GLOBALLY. 
		while True:
			try:
				d = self.ppro_out.recv()
				log_print("PPRO order:",d)
				type_ = d[0]

				time.sleep(1)
				if type_ == "Buy":

					symbol = d[1]
					share = d[2]
					rationale = d[3]

					if self.share ==0:
						self.pos = LONG

					if self.pos ==LONG or self.pos=="":
						self.share +=share
					elif self.pos ==SHORT:
						self.share -=share

					data ={}
					data["symbol"]= symbol
					data["side"]= LONG
					data["price"]= float(self.ask)
					data["shares"]= int(share)
					data["timestamp"]= self.sec
					self.ppro.send(["order confirm",data])

				elif type_ =="Sell":

					symbol = d[1]
					share = d[2]
					rationale = d[3]

					if self.share ==0:
						self.pos = SHORT

					if self.pos ==SHORT or self.pos=="":
						self.share +=share
					elif self.pos ==LONG:
						self.share -=share

					data ={}
					data["symbol"]= symbol
					data["side"]= SHORT
					data["price"]= float(self.bid)
					data["shares"]= int(share)
					data["timestamp"]= self.sec
					self.ppro.send(["order confirm",data])


				elif type_ == "Flatten":

					symbol = d[1]
					if self.pos ==LONG:
						data ={}
						data["symbol"]= symbol
						data["side"]= SHORT
						data["price"]= float(self.bid)
						data["shares"]= int(self.share)
						data["timestamp"]= self.sec
						self.ppro.send(["order confirm",data])
					else:
						data ={}
						data["symbol"]= symbol
						data["side"]= LONG
						data["price"]= float(self.bid)
						data["shares"]= int(self.share)
						data["timestamp"]= self.sec
						self.ppro.send(["order confirm",data])
					self.share = 0
					self.pos =""
			except Exception as e:
				log_print(e)

	def add1(self):
		data = {}
		data["symbol"]= "SPY.AM"
		data["side"]= LONG
		data["price"]= float(self.ask)
		data["shares"]= int(1)
		data["timestamp"]= self.sec
		self.ppro.send(["order confirm",data])

	def sub1(self):
		data = {}
		data["symbol"]= "SPY.AM"
		data["side"]= SHORT
		data["price"]= float(self.ask)
		data["shares"]= int(1)
		data["timestamp"]= self.sec
		self.ppro.send(["order confirm",data])

	def price_changer(self):
		while True:
			self.price.set(round(self.price.get()+self.change_sum,2))
			self.change()
			time.sleep(self.wait_time)

	def price_stay(self):
		self.change_sum = 0

	def time_facotr_1(self):
		self.wait_time=1

	def time_factor_10(self):
		self.wait_time=0.1

	def price_up(self):
		self.change_sum = 0.01
		# self.price.set(round(self.price.get()+0.1,2))
		# self.change()
	def price_down(self):
		self.change_sum = -0.01

		# self.price.set(round(self.price.get()-0.1,2))
		# self.change()

	def price_up_little(self):
		self.price.set(round(self.price.get()+0.1,2))
		self.change()

	def price_down_little(self):
		self.price.set(round(self.price.get()-0.1,2))
		self.change()

	def price_upx(self):
		self.price.set(round(self.price.get()+1,2))
		self.change()

	def price_downx(self):
		self.price.set(round(self.price.get()-1,2))
		self.change()

	def change(self):
		self.sec+=1
		data={}
		data["symbol"]= "SPY.AM"

		self.bid = round(float(self.price.get()-0.01),2)
		self.ask = round(float(self.price.get()+0.01),2)

		data["bid"]= round(float(self.price.get()-0.01),2)
		data["ask"]= round(float(self.price.get()+0.01),2)

		data["timestamp"]= self.sec
		self.ppro.send(["order update",data])


if __name__ == '__main__':


	multiprocessing.freeze_support()

	port =4609

	goodtrade_pipe, receive_pipe = multiprocessing.Pipe()

	algo_voxcom = multiprocessing.Process(target=algo_manager_voxcom, args=(receive_pipe,),daemon=True)
	algo_voxcom.daemon=True
	

	ppro_in, ppro_pipe_end = multiprocessing.Pipe()

	ppro_in_manager = multiprocessing.Process(target=Ppro_in, args=(port,ppro_pipe_end),daemon=True)
	ppro_in_manager.daemon=True
	

	ppro_out, ppro_pipe_end2 = multiprocessing.Pipe()

	ppro_out_manager = multiprocessing.Process(target=Ppro_out, args=(ppro_pipe_end2,port,),daemon=True)
	ppro_out_manager.daemon=True
	

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager v2 b2") 
	root.geometry("1920x800")

	Manager(root,goodtrade_pipe,ppro_out,ppro_in,TEST)

	if len(sys.argv)>1:
		Tester(receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	else:
		algo_voxcom.start()
		ppro_out_manager.start()
		ppro_in_manager.start()		


	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()