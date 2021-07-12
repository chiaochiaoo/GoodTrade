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

		self.manager = manager
		# self.init= tk.Button(self.root ,text="Register",width=10,bg="#5BFF80",command=self.start_test)
		# self.init.grid(column=1,row=1) m

		self.price = tk.DoubleVar(value=412.55)

		tk.Entry(self.root ,textvariable=self.price,width=10).grid(column=1,row=2)

		tk.Button(self.root ,text="deploy",command=self.deploy).grid(column=1,row=4)
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
		with open('backtest/AMD.NQ.txt') as json_file:
			tester = json.load(json_file)

		self.gt.send(["pkg",[[BREAKFIRST, tester['symbol'], tester["support"], tester["resistence"], 50.0, {'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441}]]])

		time.sleep(1)
		wish_granter = threading.Thread(target=self.wish, daemon=True)
		wish_granter.start()

		price_changer = threading.Thread(target=self.price_changer, daemon=True)
		price_changer.start()

	def deploy(self):

		#do couple thing. 1. deploy. 2. jump to 34200 and start feading ppro. 
		self.manager.deploy_all()

		print(np.where(tester['ts']>34200))


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

	def price_changer(self):
		while True:
			self.price.set(round(self.price.get()+self.change_sum,2))
			self.change()
			time.sleep(self.wait_time)

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

# class Tester:

# 	def __init__(self,receive_pipe,ppro_in,ppro_out):

# 		now = datetime.now()

# 		self.sec =  34180
# 		print(self.sec)
# 		self.bid=0
# 		self.ask=0

# 		self.root = tk.Toplevel(width=780,height=250)
# 		self.gt = receive_pipe
# 		self.ppro = ppro_in

# 		self.ppro_out = ppro_out

# 		self.pos  = ""
# 		self.share = 0
# 		self.change_sum = 0

# 		self.wait_time = 1

# 		self.buy_book = {}
# 		self.sell_book = {}

# 		self.price_stay = True
# 		self.price_flip = True

# 		# self.init= tk.Button(self.root ,text="Register",width=10,bg="#5BFF80",command=self.start_test)
# 		# self.init.grid(column=1,row=1) m

# 		self.price = tk.DoubleVar(value=412.55)

# 		tk.Entry(self.root ,textvariable=self.price,width=10).grid(column=1,row=2)

# 		tk.Button(self.root ,text="up",command=self.price_up).grid(column=1,row=4)
# 		tk.Button(self.root ,text="stay",command=self.price_stay).grid(column=2,row=4)
# 		tk.Button(self.root ,text="down",command=self.price_down).grid(column=3,row=4)
# 		tk.Button(self.root ,text="TimeX1",command=self.time_facotr_1).grid(column=1,row=3)
# 		tk.Button(self.root ,text="TimeX10",command=self.time_factor_10).grid(column=2,row=3)
# 		tk.Button(self.root ,text="up 0.1",command=self.price_up_little).grid(column=1,row=5)
# 		tk.Button(self.root ,text="down 0.1",command=self.price_down_little).grid(column=2,row=5)
# 		tk.Button(self.root ,text="up 1",command=self.price_upx).grid(column=1,row=6)
# 		tk.Button(self.root ,text="down 1",command=self.price_downx).grid(column=2,row=6)
# 		tk.Button(self.root ,text="add 1 share",command=self.add1).grid(column=1,row=7)
# 		tk.Button(self.root ,text="sub 1 share",command=self.sub1).grid(column=2,row=7)


# 		#self.gt.send(["pkg",[[BREAKFIRST, 'SPY.AM', 412, 413, 50.0, {'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441}]]])

# 		time.sleep(1)
# 		wish_granter = threading.Thread(target=self.wish, daemon=True)
# 		wish_granter.start()

# 		price_changer = threading.Thread(target=self.price_changer, daemon=True)
# 		price_changer.start()

# 	def wish(self): #a sperate process. GLOBALLY. 
# 		while True:
# 			try:
# 				d = self.ppro_out.recv()
# 				log_print("PPRO order:",d)
# 				type_ = d[0]

# 				#time.sleep(1)
# 				if type_ == "Buy":

# 					symbol = d[1]
# 					share = d[2]
# 					rationale = d[3]

# 					if self.share ==0:
# 						self.pos = LONG

# 					if self.pos ==LONG or self.pos=="":
# 						self.share +=share
# 					elif self.pos ==SHORT:
# 						self.share -=share

# 					data ={}
# 					data["symbol"]= symbol
# 					data["side"]= LONG
# 					data["price"]= float(self.ask)
# 					data["shares"]= int(share)
# 					data["timestamp"]= self.sec
# 					self.ppro.send(["order confirm",data])

# 				elif type_ =="Sell":

# 					symbol = d[1]
# 					share = d[2]
# 					rationale = d[3]

# 					if self.share ==0:
# 						self.pos = SHORT

# 					if self.pos ==SHORT or self.pos=="":
# 						self.share +=share
# 					elif self.pos ==LONG:
# 						self.share -=share

# 					data ={}
# 					data["symbol"]= symbol
# 					data["side"]= SHORT
# 					data["price"]= float(self.bid)
# 					data["shares"]= int(share)
# 					data["timestamp"]= self.sec
# 					self.ppro.send(["order confirm",data])


# 				elif type_ == LIMITBUY:
# 					symbol = d[1]
# 					price = d[2]
# 					share = d[3]

# 					self.buy_book[price] = share
# 				elif type_ == LIMITSELL:
# 					symbol = d[1]
# 					price = d[2]
# 					share = d[3]

# 					self.sell_book[price] = share
# 				elif type_ == "Flatten":

# 					symbol = d[1]
# 					if self.pos ==LONG:
# 						data ={}
# 						data["symbol"]= symbol
# 						data["side"]= SHORT
# 						data["price"]= float(self.bid)
# 						data["shares"]= int(self.share)
# 						data["timestamp"]= self.sec
# 						self.ppro.send(["order confirm",data])
# 					else:
# 						data ={}
# 						data["symbol"]= symbol
# 						data["side"]= LONG
# 						data["price"]= float(self.bid)
# 						data["shares"]= int(self.share)
# 						data["timestamp"]= self.sec
# 						self.ppro.send(["order confirm",data])
# 					self.share = 0
# 					self.pos =""
# 			except Exception as e:
# 				log_print(e)

# 	def add1(self):
# 		data = {}
# 		data["symbol"]= "SPY.AM"
# 		data["side"]= LONG
# 		data["price"]= float(self.ask)
# 		data["shares"]= int(1)
# 		data["timestamp"]= self.sec
# 		self.ppro.send(["order confirm",data])

# 	def sub1(self):
# 		data = {}
# 		data["symbol"]= "SPY.AM"
# 		data["side"]= SHORT
# 		data["price"]= float(self.ask)
# 		data["shares"]= int(1)
# 		data["timestamp"]= self.sec
# 		self.ppro.send(["order confirm",data])

# 	def price_changer(self):
# 		while True:
# 			self.price.set(round(self.price.get()+self.change_sum,2))
# 			self.change()
# 			time.sleep(self.wait_time)

# 	def price_stay(self):
# 		self.price_stay = True
# 		self.change_sum = 0
# 	def time_facotr_1(self):
# 		self.wait_time=1

# 	def time_factor_10(self):
# 		self.wait_time=0.02

# 	def time_factor_50(self):
# 		self.wait_time=0.1

# 	def price_up(self):
# 		self.price_stay = False
# 		self.change_sum = 0.01
# 		# self.price.set(round(self.price.get()+0.1,2))
# 		# self.change()
# 	def price_down(self):
# 		self.price_stay = False
# 		self.change_sum = -0.01

# 		# self.price.set(round(self.price.get()-0.1,2))
# 		# self.change()

# 	def price_up_little(self):
# 		self.price.set(round(self.price.get()+0.1,2))
# 		self.change()

# 	def price_down_little(self):
# 		self.price.set(round(self.price.get()-0.1,2))
# 		self.change()

# 	def price_upx(self):
# 		self.price.set(round(self.price.get()+1,2))
# 		self.change()

# 	def price_downx(self):
# 		self.price.set(round(self.price.get()-1,2))
# 		self.change()

# 	def change(self):
# 		self.sec+=1
# 		#print(self.sec)
# 		data={}
# 		data["symbol"]= "SPY.AM"

# 		if self.price_stay:
# 			if self.price_flip:
# 				self.price.set(round(self.price.get()+0.01,2))
# 				self.price_flip = False
# 			else:
# 				self.price.set(round(self.price.get()-0.01,2))
# 				self.price_flip = True
# 		self.bid = round(float(self.price.get()-0.01),2)
# 		self.ask = round(float(self.price.get()+0.01),2)

# 		data["bid"]= round(float(self.price.get()-0.01),2)
# 		data["ask"]= round(float(self.price.get()+0.01),2)

# 		data["timestamp"]= self.sec
# 		self.ppro.send(["order update",data])
# 		self.limit_buy_sell()

# 	def limit_buy_sell(self):

# 		used = []
# 		for key,item in self.buy_book.items():
# 			if self.bid <= key:
# 				data={}
# 				data["symbol"]= "SPY.AM"
# 				data["side"]= LONG
# 				data["price"]= float(self.ask)
# 				data["shares"]= self.buy_book[key]
# 				data["timestamp"]= self.sec
# 				self.ppro.send(["order confirm",data])
# 				self.share -= data["shares"]

# 				used.append(key)

# 		for i in used:
# 			del self.buy_book[i]

# 		used = []
# 		for key,item in self.sell_book.items():
# 			if self.ask >= key:
# 				data={}
# 				data["symbol"]= "SPY.AM"
# 				data["side"]= SHORT
# 				data["price"]= float(self.bid)
# 				data["shares"]= self.sell_book[key]
# 				data["timestamp"]= self.sec
# 				self.ppro.send(["order confirm",data])
# 				self.share-= data["shares"]
# 				used.append(key)

# 		for i in used:
# 			del self.sell_book[i]


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
	root.title("GoodTrade Algo Manager v2 b6") 
	root.geometry("1920x800")

	manager = Manager(root,goodtrade_pipe,ppro_out,ppro_in,TEST)

	if len(sys.argv)>1:
		BackTester(manager,receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	else:
		algo_voxcom.start()
		ppro_out_manager.start()
		ppro_in_manager.start()		


	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()


	algo_voxcom.terminate()
	ppro_in_manager.terminate()
	ppro_out_manager.terminate()


	algo_voxcom.join()
	ppro_in_manager.join()
	ppro_out_manager.join()
	print("All subprocesses terminated")
	
	os._exit(1) 
	print("exit")