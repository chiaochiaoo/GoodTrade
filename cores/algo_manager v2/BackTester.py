from pannel import *
from tkinter import ttk
from Symbol import *
from TradingPlan import *
from UI import *
from Ppro_in import *
from Ppro_out import *
from constant import *
import numpy as np

from Util_functions import *
from datetime import datetime
import json
#May this class bless by the Deus Mechanicus.

class BackTester:


	def ts_to_min(self,ts):

		hour= ts//3600
		minute = (ts%3600)//60
		secnds = (ts%3600)%60

		return str(hour)+":"+ str(minute)+":"+ str(secnds)

	def __init__(self,manager,receive_pipe,ppro_in,ppro_out):

		now = datetime.now()

		self.sec =  34180
		print(self.sec)
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

		self.buy_book = {}
		self.sell_book = {}

		self.price_stay = True
		self.price_flip = True

		self.pause = False
		self.rewind = False

		self.manager = manager
		# self.init= tk.Button(self.root ,text="Register",width=10,bg="#5BFF80",command=self.start_test)
		# self.init.grid(column=1,row=1) m

		self.price = tk.DoubleVar(value=412.55)
		tk.Label(self.root ,textvariable=self.price,width=10).grid(column=2,row=1)

		self.time = tk.StringVar()
		tk.Label(self.root ,textvariable=self.time,width=10).grid(column=1,row=1)

		tk.Button(self.root ,text="Start",command=self.deploy).grid(column=1,row=2)

		self.pause_button = tk.Button(self.root ,text="Pause",command=self.pause_function)
		self.pause_button.grid(column=1,row=3)
		tk.Button(self.root ,text="Rewind",command=self.rewind_function).grid(column=1,row=4)

		# tk.Button(self.root ,text="stay",command=self.price_stay).grid(column=2,row=4)
		# tk.Button(self.root ,text="down",command=self.price_down).grid(column=3,row=4)
		# tk.Button(self.root ,text="TimeX1",command=self.time_facotr_1).grid(column=1,row=3)
		# tk.Button(self.root ,text="TimeX10",command=self.time_factor_10).grid(column=2,row=3)
		# tk.Button(self.root ,text="up 0.1",command=self.price_up_little).grid(column=1,row=5)
		# tk.Button(self.root ,text="down 0.1",command=self.price_down_little).grid(column=2,row=5)
		# tk.Button(self.root ,text="up 1",command=self.price_upx).grid(column=1,row=6)
		# tk.Button(self.root ,text="down 1",command=self.price_downx).grid(column=2,row=6)
		# tk.Button(self.root ,text="add 1 share",command=self.add1).grid(column=1,row=7)
		# tk.Button(self.root ,text="sub 1 share",command=self.sub1).grid(column=2,row=7)

		#read the file
		with open('backtest/XLE.AM.txt') as json_file:
			tester = json.load(json_file)

		self.gt.send(["pkg",[[BREAKFIRST, tester['symbol'], tester["support"], tester["resistence"], 50.0, {'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441}]]])

		time.sleep(1)

		self.tester = tester
		wish_granter = threading.Thread(target=self.wish, daemon=True)
		wish_granter.start()

		# price_changer = threading.Thread(target=self.price_changer, daemon=True)
		# price_changer.start()

	def rewind_function(self):
		self.rewind = True
	def price_changer(self):
		start = np.where(np.array(self.tester['ts'])>34200)[0][0]

		while True:
			self.rewind = False
			for i in range(start,len(self.tester['ts'])):
				data={}
				data["bid"]= self.tester['bid'][i]
				data["ask"]= self.tester['ask'][i]
				data["symbol"]= self.tester['symbol']
				data["timestamp"]= self.tester['ts'][i]
				self.bid = data["bid"]
				self.ask = data["ask"]
				self.ppro.send(["order update",data])
				self.price.set(data["bid"])
				self.time.set(self.ts_to_min(data["timestamp"]))
				if i%1000 ==0:
					print(data)

				while self.pause==True:
					time.sleep(1)
				time.sleep(0.01)
				if self.rewind:
					break
	def pause_function(self):

		if self.pause:
			self.pause_button["text"] = "Pause"
			self.pause = False
		else:
			self.pause_button["text"] = "Resume"
			self.pause = True

		print(self.pause)
	def deploy(self):
		#do couple thing. 1. deploy. 2. jump to 34200 and start feading ppro. 
		self.manager.deploy_all()
		time.sleep(1)
		price_changer = threading.Thread(target=self.price_changer, daemon=True)
		price_changer.start()

	def wish(self): #a sperate process. GLOBALLY. 
		while True:
			try:
				d = self.ppro_out.recv()
				log_print("PPRO order:",d)
				type_ = d[0]

				#time.sleep(1)
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


				elif type_ == LIMITBUY:
					symbol = d[1]
					price = d[2]
					share = d[3]

					self.buy_book[price] = share
				elif type_ == LIMITSELL:
					symbol = d[1]
					price = d[2]
					share = d[3]

					self.sell_book[price] = share
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

	# def price_changer(self):
	# 	while True:
	# 		self.price.set(round(self.price.get()+self.change_sum,2))
	# 		self.change()
	# 		time.sleep(self.wait_time)

	def price_stay(self):
		self.price_stay = True
		self.change_sum = 0
	def time_facotr_1(self):
		self.wait_time=1

	def time_factor_10(self):
		self.wait_time=0.02

	def time_factor_50(self):
		self.wait_time=0.1

	def price_up(self):
		self.price_stay = False
		self.change_sum = 0.01
		# self.price.set(round(self.price.get()+0.1,2))
		# self.change()
	def price_down(self):
		self.price_stay = False
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
		#print(self.sec)
		data={}
		data["symbol"]= "SPY.AM"

		if self.price_stay:
			if self.price_flip:
				self.price.set(round(self.price.get()+0.01,2))
				self.price_flip = False
			else:
				self.price.set(round(self.price.get()-0.01,2))
				self.price_flip = True
		self.bid = round(float(self.price.get()-0.01),2)
		self.ask = round(float(self.price.get()+0.01),2)

		data["bid"]= round(float(self.price.get()-0.01),2)
		data["ask"]= round(float(self.price.get()+0.01),2)

		data["timestamp"]= self.sec
		self.ppro.send(["order update",data])
		self.limit_buy_sell()

	def limit_buy_sell(self):

		used = []
		for key,item in self.buy_book.items():
			if self.bid <= key:
				data={}
				data["symbol"]= "SPY.AM"
				data["side"]= LONG
				data["price"]= float(self.ask)
				data["shares"]= self.buy_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share -= data["shares"]

				used.append(key)

		for i in used:
			del self.buy_book[i]

		used = []
		for key,item in self.sell_book.items():
			if self.ask >= key:
				data={}
				data["symbol"]= "SPY.AM"
				data["side"]= SHORT
				data["price"]= float(self.bid)
				data["shares"]= self.sell_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share-= data["shares"]
				used.append(key)

		for i in used:
			del self.sell_book[i]



