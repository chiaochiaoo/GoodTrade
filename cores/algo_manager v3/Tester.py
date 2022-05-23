
from datetime import datetime, timedelta
import tkinter as tk                     
from pannel import *
from tkinter import ttk
from Symbol import *
from TradingPlan import *
from Pair_TP import *
from UI import *
from Ppro_in import *
from Ppro_out import *
from constant import *
class Tester:

	def __init__(self,receive_pipe,ppro_in,ppro_out):

		now = datetime.now()

		print("TESTING INIT")
		self.sec =  now.hour*3600 + now.minute*60 + now.second

		self.qbid = 0
		self.qask = 0

		self.data = {}
		self.root = tk.Toplevel(width=780,height=250)
		self.gt = receive_pipe
		self.ppro = ppro_in

		self.algonum = 3

		self.spybid=0
		self.spyask=0
		self.qqqbid=0
		self.qqqask=0

		self.ppro_out = ppro_out

		self.pos  = ""
		self.share = 0
		self.change_sum = 0

		self.wait_time = 1

		self.spy_buy_book = {}
		self.spy_sell_book = {}

		self.qqq_buy_book = {}
		self.qqq_sell_book = {}


		self.price_stay = True
		self.price_flip = True

		# self.init= tk.Button(self.root ,text="Register",width=10,bg="#5BFF80",command=self.start_test)
		# self.init.grid(column=1,row=1) m

		self.price = tk.DoubleVar(value=412.55)

		tk.Entry(self.root ,textvariable=self.price,width=10).grid(column=1,row=2)	

		tk.Button(self.root ,text="up",command=self.price_up).grid(column=1,row=4)	
		tk.Button(self.root ,text="stay",command=self.price_stayx).grid(column=2,row=4)	
		tk.Button(self.root ,text="down",command=self.price_down).grid(column=3,row=4)	

		tk.Button(self.root ,text="TimeX1",command=self.time_facotr_1).grid(column=1,row=3)
		tk.Button(self.root ,text="TimeX10",command=self.time_factor_10).grid(column=2,row=3)	

		tk.Button(self.root ,text="up 0.1",command=self.price_up_little).grid(column=1,row=5)
		tk.Button(self.root ,text="down 0.1",command=self.price_down_little).grid(column=2,row=5)	

		tk.Button(self.root ,text="add new",command=self.addnew).grid(column=1,row=6)	
		tk.Button(self.root ,text="down 1",command=self.price_downx).grid(column=2,row=6)	

		tk.Button(self.root ,text="add 1 share",command=self.add1).grid(column=1,row=7)	
		tk.Button(self.root ,text="sub 1 share",command=self.sub1).grid(column=2,row=7)	



		dic = {}

		dic["algo_id"] = 'TEST1'
		dic["type_name"] = 'Single'
		dic["algo_name"] = 'TEST'
		dic["entry_type"] = MARKETACTION    #INSTANTLONG
		dic["symbol"] ='SPY.AM'
		dic["support"] =413
		dic["resistence"] =414
		dic["risk"] =50.0
		#dic["statistics"] ={'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441,"expected_momentum":2}
		dic["immediate_deployment"] = True
		dic["management"] = HOLDXSECOND


		s=""
		for key,item in dic.items():
			s+=key+":"+str(item)

		print(s)

		self.gt.send(["pkg",[dic]])

		dic = {}

		dic["algo_id"] = 'TEST2'
		dic["type_name"] = 'Single'
		dic["algo_name"] = 'TEST'
		dic["entry_type"] = FADEUP#INSTANTSHORT
		dic["symbol"] ='SPY.AM'
		dic["support"] =413
		dic["resistence"] =412
		dic["risk"] =50.0
		dic["statistics"] ={'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441,"expected_momentum":2}
		dic["immediate_deployment"] = False
		dic["management"] = ONETOTWORISKREWARD


		self.gt.send(["pkg",[dic]])



		dic = {}

		dic["algo_id"] = 'PairTest'
		dic["type_name"] = 'Pair'
		dic["algo_name"] = 'TEST'
		dic["symbol1"] ='SPY.AM'
		dic["symbol2"] ='QQQ.NQ'
		dic["ratio"] =(1,-1)
		dic["share"] =20
		dic["risk"] =50.0
		dic["symbol1_statistics"] ={}
		dic["symbol2_statistics"] = {}
		dic["management"] = ONETOTWORISKREWARD#MARKETMAKING



		#self.gt.send(["pkg",[dic]])


		time.sleep(1)
		wish_granter = threading.Thread(target=self.wish, daemon=True)
		wish_granter.start()

		price_changer = threading.Thread(target=self.price_changer, daemon=True)
		price_changer.start()

	def addnew(self):

		
		dic={}
		dic["algo_id"] = 'TEST'+str(self.algonum)
		dic["type_name"] = 'Single'
		dic["algo_name"] = 'TEST'
		dic["entry_type"] = FADEUP#INSTANTSHORT
		dic["symbol"] =str(self.algonum)
		dic["support"] =413
		dic["resistence"] =412
		dic["risk"] =50.0
		dic["statistics"] ={'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441,"expected_momentum":2}
		dic["immediate_deployment"] = True
		dic["management"] = ONETOTWORISKREWARD
		self.algonum+=1

		self.gt.send(["pkg",[dic]])

	def wish(self): #a sperate process. GLOBALLY. 
		while True:
			try:
				d = self.ppro_out.recv()
				log_print("PPRO order:",d)
				type_ = d[0]

				#time.sleep(1)
				
				if type_ == "Buy" or type_ == IOCBUY:

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
					data["timestamp"]= self.sec

					if symbol == "SPY.AM":
						data["price"]= float(self.spyask)
					else:
						data["price"]=float(self.qask)

					data["shares"]= int(share)
					self.ppro.send(["order confirm",data])
					# if share>3:
					# 	data["shares"]= int(share)//3
						
					# 	self.ppro.send(["order confirm",data])
					# 	self.ppro.send(["order confirm",data])
					# 	self.ppro.send(["order confirm",data])
					# else:


				elif type_ =="Sell" or type_ == IOCSELL:

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

					if symbol == "SPY.AM":
						data["price"]= float(self.spybid)
					else:
						data["price"]=float(self.qbid)


					data["timestamp"]= self.sec
					data["shares"]= int(share)
					self.ppro.send(["order confirm",data])

					# if share>3:
					# 	data["shares"]= int(share)//3
						
					# 	self.ppro.send(["order confirm",data])
					# 	self.ppro.send(["order confirm",data])
					# 	self.ppro.send(["order confirm",data])
					# else:



				elif type_ == LIMITBUY :
					symbol = d[1]
					price = d[2]
					share = d[3]

					#self.buy_book[price] = share
				elif type_ == LIMITSELL :
					symbol = d[1]
					price = d[2]
					share = d[3]

					#self.sell_book[price] = share

				elif type_ == PASSIVEBUY:

					symbol = d[1]
					price = d[3]
					share = d[2]

					
					if symbol == "SPY.AM":
						if self.spybid not in self.spy_buy_book:
							self.spy_buy_book[self.spybid] = share
						else:
							self.spy_buy_book[self.spybid] += share
					else:

						if self.qbid not in self.qqq_buy_book:
							self.qqq_buy_book[self.qbid] = share
						else:
							self.qqq_buy_book[self.qbid] += share


				elif type_ == PASSIVESELL:

					symbol = d[1]
					price = d[3]
					share = d[2]

					if symbol == "SPY.AM":
						if self.spyask not in self.spy_sell_book:
							self.spy_sell_book[self.spyask] = share
						else:
							self.spy_sell_book[self.spyask] += share
					else:

						if self.qask not in self.qqq_sell_book:
							self.qqq_sell_book[self.qask] = share
						else:
							self.qqq_sell_book[self.qask] += share



				elif type_ == "Cancel":


					self.sell_book ={}
					self.buy_book = {}
				elif type_ == "Flatten":

					symbol = d[1]
					print(self.share)
					if self.share >0:
						data ={}
						data["symbol"]= symbol
						data["side"]= SHORT
						data["price"]= float(self.spybid)
						data["shares"]= abs(int(self.share))
						data["timestamp"]= self.sec
						print(data)
						self.ppro.send(["order confirm",data])
					else:
						data ={}
						data["symbol"]= symbol
						data["side"]= LONG
						data["price"]= float(self.spybid)
						data["shares"]= abs(int(self.share))
						data["timestamp"]= self.sec
						print(data)
						self.ppro.send(["order confirm",data])
					self.share = 0
					self.pos =""
			except Exception as e:
				PrintException(e)

	def add1(self):
		data = {}
		data["symbol"]= "SPY.AM"
		data["side"]= LONG
		data["price"]= float(self.spyask)
		data["shares"]= int(1)
		data["timestamp"]= self.sec
		self.ppro.send(["order confirm",data])


	def sub1(self):
		data = {}
		data["symbol"]= "SPY.AM"
		data["side"]= SHORT
		data["price"]= float(self.spyask)
		data["shares"]= int(1)
		data["timestamp"]= self.sec
		self.ppro.send(["order confirm",data])

	def price_changer(self):
		while True:
			self.price.set(round(self.price.get()+self.change_sum,2))
			self.change()
			time.sleep(self.wait_time)

	def price_stayx(self):
		#print("stay")
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

		if self.price_stay:
			if self.price_flip:
				self.price.set(round(self.price.get()+0.01,2))
				self.price_flip = False
			else:
				self.price.set(round(self.price.get()-0.01,2))
				self.price_flip = True
			#print("hello")

		self.spybid = round(float(self.price.get()-0.02),2)
		self.spyask = round(float(self.price.get()+0.02),2)


		self.qbid = self.spybid -100
		self.qask = self.spyask - 100

		# data["symbol"]= "SPY.AM"
		# data["bid"]= round(float(self.price.get()-0.01),2)
		# data["ask"]= round(float(self.price.get()+0.01),2)
		# data["timestamp"]= self.sec

		#self.ppro.send(["order update",data])

		self.decode_l1("SPY.AM",self.spybid,self.spyask,self.sec,self.ppro,self.data)

		self.decode_l1("QQQ.NQ",self.qbid,self.qask,self.sec,self.ppro,self.data)
		self.limit_buy_sell()

	def decode_l1(self,symbol,bid,ask,ts,pipe,l1data):

		#ts= timestamp_seconds(find_between(stream_data, "MarketTime=", ",")[:-4])

		ms = ts//60

		send = False

		if symbol in l1data:
			#if either level has changed. register. 
			if l1data[symbol]["bid"]!=bid or l1data[symbol]["ask"]!=ask:
				send = True
			elif ts-l1data[symbol]["timestamp"] >1:
				send = True

			#if has been more then 2 leconds. registered.

		else:
			l1data[symbol] = {}

			l1data[symbol]["symbol"] = symbol
			l1data[symbol]["bid"] = bid
			l1data[symbol]["ask"] = ask
			l1data[symbol]["timestamp"] = ts

			l1data[symbol]["internal"] = {}
			l1data[symbol]["internal"]["timestamp"] = ms
			l1data[symbol]["internal"]["current_minute_bins"] = [bid,ask]
			l1data[symbol]["internal"]["EMA_count"] = 0

			#Realizing - I won't need to track these values no more.
			l1data[symbol]["internal"]["high"] = ask
			l1data[symbol]["internal"]["low"] = bid
			l1data[symbol]["internal"]["open"] = ask
			l1data[symbol]["internal"]["close"] = bid

			l1data[symbol]["internal"]["EMA_count"] = 0

			l1data[symbol]["internal"]["EMA5H"] = 0
			l1data[symbol]["internal"]["EMA5L"] = 0
			l1data[symbol]["internal"]["EMA5C"] = 0

			l1data[symbol]["internal"]["EMA8H"] = 0
			l1data[symbol]["internal"]["EMA8L"] = 0
			l1data[symbol]["internal"]["EMA8C"] = 0


			l1data[symbol]["internal"]["EMA21H"] = 0
			l1data[symbol]["internal"]["EMA21L"] = 0
			l1data[symbol]["internal"]["EMA21C"] = 0

			send = True

		#process the informations. process internal only. 

		#two kinds of update. normal second; and new second. 
		if send:

			update = process_l1(l1data[symbol]["internal"],bid,ask,ms)
			"""two cases. small, and big."""
			l1data[symbol]["symbol"] = symbol
			l1data[symbol]["bid"] = bid
			l1data[symbol]["ask"] = ask
			l1data[symbol]["timestamp"] = ts

			if update:
				update_ = {}
				update_["EMA5H"]=l1data[symbol]["internal"]["EMA5H"]
				update_["EMA5L"]=l1data[symbol]["internal"]["EMA5L"]
				update_["EMA5C"]=l1data[symbol]["internal"]["EMA5C"]
				update_["EMA8H"]=l1data[symbol]["internal"]["EMA8H"]
				update_["EMA8L"]=l1data[symbol]["internal"]["EMA8L"]
				update_["EMA8C"]=l1data[symbol]["internal"]["EMA8C"]

				update_["EMA21H"]=l1data[symbol]["internal"]["EMA21H"]
				update_["EMA21L"]=l1data[symbol]["internal"]["EMA21L"]
				update_["EMA21C"]=l1data[symbol]["internal"]["EMA21C"]

				update_["EMAcount"]=l1data[symbol]["internal"]["EMA_count"]
				pipe.send(["order update_m",l1data[symbol],update_])

				#print(l1data[symbol])
				# writer.writerow([symbol,mili_ts,bid,ask,\
				# 	l1data[symbol]["internal"]["EMA5H"],\
				# 	l1data[symbol]["internal"]["EMA5L"],\
				# 	l1data[symbol]["internal"]["EMA5C"],\
				# 	l1data[symbol]["internal"]["EMA8H"],\
				# 	l1data[symbol]["internal"]["EMA8L"],\
				# 	l1data[symbol]["internal"]["EMA8C"]])
				#print(symbol,l1data[symbol],update_)
			else:

				#print(l1data[symbol])
				#add time
				pipe.send(["order update",l1data[symbol]])
				#writer.writerow([symbol,mili_ts,bid,ask])


	def process_l1(dic,bid,ask,ms):

		"""two senarios. within current timestamp, and out. """


		if dic["timestamp"]  != ms: #a new minute. 

			dic["timestamp"] = ms
			if len(dic["current_minute_bins"])>1:
				dic["high"]=max(dic["current_minute_bins"])
				dic["low"]=min(dic["current_minute_bins"])
				dic["open"]=dic["current_minute_bins"][0]
				dic["close"]=dic["current_minute_bins"][-1]

				dic["current_minute_bins"] = []

				if dic["EMA_count"]==0: #first time setting up.
					### HERE. What i need to do is have the GT&server also track the EMA values of these. 
					dic["EMA5H"] = dic["high"]
					dic["EMA5L"] = dic["low"]
					dic["EMA5C"] = dic["close"]

					dic["EMA8H"] = dic["high"]
					dic["EMA8L"] = dic["low"]
					dic["EMA8C"] = dic["close"]

				else: #induction! 
					dic["EMA5H"] = self.new_ema(dic["high"],dic["EMA5H"],5)
					dic["EMA5L"] = self.new_ema(dic["low"],dic["EMA5L"],5)
					dic["EMA5C"] = self.new_ema(dic["close"],dic["EMA5C"],5)

					dic["EMA8H"] = self.new_ema(dic["high"],dic["EMA8H"],8)
					dic["EMA8L"] = self.new_ema(dic["low"],dic["EMA8L"],8)
					dic["EMA8C"] = self.new_ema(dic["close"],dic["EMA8C"],8)

					dic["EMA21H"] = new_ema(dic["high"],dic["EMA21H"],21)
					dic["EMA21L"] = new_ema(dic["low"],dic["EMA21L"],21)
					dic["EMA21C"] = new_ema(dic["close"],dic["EMA21C"],21)
					
				dic["EMA_count"]+=1
				return True
			else:
				return False
		else: #same minute 
			dic["current_minute_bins"].append(bid)
			dic["current_minute_bins"].append(ask)
			return False
			
	def new_ema(self,current,last_EMA,n):
		
		return round((current - last_EMA)*(2/(n+1)) + last_EMA,2)

	def limit_buy_sell(self):

		#print("checking limit book SPY",self.spy_buy_book,self.spy_sell_book)

		used = []
		for key,item in self.spy_buy_book.items():

			#print("checking",key,self.spybid,self.spybid <= key)
			if self.spybid <= key:
				#print("order___CONFIRMED")
				data={}
				data["symbol"]= "SPY.AM"
				data["side"]= LONG
				data["price"]= float(self.spyask)
				data["shares"]= self.spy_buy_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share += data["shares"]

				used.append(key)

		for i in used:
			del self.spy_buy_book[i]

		used = []
		for key,item in self.spy_sell_book.items():
			if self.spyask >= key:
				data={}
				data["symbol"]= "SPY.AM"
				data["side"]= SHORT
				data["price"]= float(self.spybid)
				data["shares"]= self.spy_sell_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share -= data["shares"]
				used.append(key)

		for i in used:
			del self.spy_sell_book[i]
	
		used = []
		for key,item in self.qqq_buy_book.items():

			#print("checking",key,self.spybid,self.spybid <= key)
			if self.qbid <= key:
				#print("order___CONFIRMED")
				data={}
				data["symbol"]= "QQQ.NQ"
				data["side"]= LONG
				data["price"]= float(self.qask)
				data["shares"]= self.qqq_buy_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share += data["shares"]

				used.append(key)

		for i in used:
			del self.qqq_buy_book[i]

		used = []
		for key,item in self.qqq_sell_book.items():
			if self.qask >= key:
				data={}
				data["symbol"]= "QQQ.NQ"
				data["side"]= SHORT
				data["price"]= float(self.qask)
				data["shares"]= self.qqq_sell_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share -= data["shares"]
				used.append(key)

		for i in used:
			del self.qqq_sell_book[i]




# dic = {}

# dic["algo_id"] = 'TEST1'
# dic["type_name"] = 'Single'
# dic["algo_name"] = 'TEST'
# dic["entry_type"] = MARKETACTION    #INSTANTLONG
# dic["symbol"] ='SPY.AM'
# dic["support"] =413
# dic["resistence"] =414
# dic["risk"] =50.0
# #dic["statistics"] ={'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441,"expected_momentum":2}
# dic["immediate_deployment"] = True
# dic["management"] = HOLDXSECOND


# s=""
# for key,item in dic.items():
# 	s+=key+":"+str(item)+','

# print(s)