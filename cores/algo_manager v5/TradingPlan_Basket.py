from Symbol import *
#from Triggers import *
# from Strategy import *
# from Strategy_Management import *
from constant import*
from Util_functions import *
import tkinter as tkvars
import time
import threading
import random
from datetime import datetime, timedelta
import math

# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan_Basket:

	#symbols:Symbols,risk=None

	def __init__(self,algo_name="",risk=5,Manager=None,info={}):


		self.source = "TP Basket: "

		self.algo_name = algo_name

		self.name = algo_name
		self.symbols = {}

		self.in_use = True
		self.pair_plan = False
		
		self.shut_down = False

		#self.symbol.set_tradingplan(self)

		self.manager = Manager

		self.expect_orders = ""
		self.flatten_order = False


		self.stop = 0
		self.profit = 0

		self.manual_addable = False 
		self.manual_flattabl = False 
		if "Profit" in info:
			self.profit = int(info["Profit"])

		if "Risk" in info:
			self.stop = int(info["Risk"])

		if "Addable" in info:
			self.manual_addable = True 

		if "Flattable" in info:
			self.manual_flattable = True 


		log_print(algo_name,"  profit & risk : ",self.profit,self.stop)
		#### BANED SYMBOL

		self.banned = []

		# First time its expected is fullfilled. shall the management starts.
		self.read_lock = {}
		self.have_request = {}

		self.expected_shares = {}
		self.current_shares = {}
		self.current_request = {}

		####################################################################################

		self.incremental_state = {}
		self.incremental_expected_shares = {}
		self.incremental_expected_shares_increments = {}
		self.incremental_expected_shares_last_register = {}
		self.incremental_expected_shares_intervals = {}
		self.incremental_expected_shares_deadline = {}

		####################################################################################


		self.current_exposure = {}

		self.average_price = {}

		self.stock_price ={}

		self.recent_action_ts = {}

		self.data = {}
		self.tkvars = {}

		self.tklabels= {} ##returned by UI.

		self.holdings = {}

		self.current_price_level = 0

		self.price_levels = {}

		self.algo_ui_id = 0

		self.last_ts = 0
		
		self.numeric_labels = [ESTRISK,UNREAL,REALIZED,UNREAL_MAX,UNREAL_MIN,WR,MR,TR]

		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO]

		self.bool_labels= [SELECTED]

		self.display_count = 0

		self.init_data(risk)

	def init_data(self,risk):

		for i in self.numeric_labels:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar(value=0)

		for i in self.string_labels:
			self.data[i] = ""
			self.tkvars[i] = tk.StringVar(value="")
		for i in self.bool_labels:
			self.data[i] = False
			self.tkvars[i] = tk.BooleanVar(value=False)

		self.data[ESTRISK] = float(risk)
		self.tkvars[ESTRISK].set(float(risk))

		wr,mr,tr = self.manager.get_record(self.algo_name)

		self.tkvars[WR].set(wr)
		self.tkvars[MR].set(mr)
		self.tkvars[TR].set(tr)
		# for i in self.symbol.numeric_labels:
		# 	self.tkvars[i] = tk.DoubleVar(value=self.symbol.data[i])


	def internal(self):
		log_print(self.source,self.name,"holding:",self.current_shares ,"expected:",self.expected_shares,"requested:",self.current_request)

	def activate(self):
		self.in_use	 = True

	def deactive(self):
		self.in_use = False

	def if_activated(self):
		return self.in_use	


	def register_symbol(self,symbol_name,symbol):

		if symbol_name not in self.symbols:
			self.symbols[symbol_name] = symbol
			self.symbols[symbol_name].register_tradingplan(self.algo_name,self)


			self.have_request[symbol_name] = False

			self.expected_shares[symbol_name] = 0
			self.current_shares[symbol_name] = 0
			self.current_request[symbol_name] = 0
			self.current_exposure[symbol_name] = []

			################################################################
			self.incremental_state[symbol_name] = False
			self.incremental_expected_shares[symbol_name] = 0
			self.incremental_expected_shares_increments[symbol_name] = 0
			self.incremental_expected_shares_last_register[symbol_name] = 0
			self.incremental_expected_shares_intervals[symbol_name] = 0
			self.incremental_expected_shares_deadline[symbol_name] = 0
			#################################################################

			self.average_price[symbol_name] = 0
			self.stock_price[symbol_name] = 0

			self.recent_action_ts[symbol_name] = 0

			self.holdings[symbol_name] = []

			self.read_lock[symbol_name] = threading.Lock()

			##################################################################

	def update_stockprices(self,symbol,price):

		self.stock_price[symbol] = price


	def check_incremental(self,symbol,ts):

		#################################

		#### STEP 1 : check if it already matches ###

		if self.incremental_state[symbol] ==True:

			if self.incremental_expected_shares[symbol] == self.expected_shares[symbol]:

				### TURN OFF. 
				self.incremental_state[symbol] = False 
				return 

			#### SENARIO 1, expired ####
			elif ts>self.incremental_expected_shares_deadline[symbol]:

				self.expected_shares[symbol] = self.incremental_expected_shares[symbol]
				self.incremental_state[symbol] = False 


			elif ts-self.incremental_expected_shares_last_register[symbol] >= self.incremental_expected_shares_intervals[symbol]:

				self.incremental_expected_shares_last_register[symbol] = ts

				if abs(self.incremental_expected_shares[symbol]-self.expected_shares[symbol]) < self.incremental_expected_shares_increments[symbol]:
					self.expected_shares[symbol] = self.incremental_expected_shares[symbol]


				else:
					self.expected_shares[symbol] += self.incremental_expected_shares_increments[symbol]

			self.recalculate_current_request(symbol)

			if self.incremental_state[symbol]:
				log_print(self.source,self.algo_name,symbol," now increase to",self.expected_shares[symbol], " to",self.incremental_expected_shares[symbol])
				self.tkvars[MIND].set(str(self.expected_shares[symbol])+"/"+str(self.incremental_expected_shares[symbol]))
			else:
				log_print(self.source,self.algo_name,symbol," increment done.")



	def reduce_everything_by_half_ta(self,timetakes,percentage):

		log_print(self.source,self.algo_name," TA-MOC initiating")
		
		for symbol,item in self.symbols.items():
			#self.submit_expected_shares(symbol,0)
			self.submit_incremental_expected(symbol,int(self.current_shares[symbol]*percentage),timetakes,True)

	def get_future_remaining(self,symbol):

		return self.incremental_expected_shares[symbol]


	def reset_incremental_data(self,symbol):

		self.incremental_state[symbol] = False
		self.incremental_expected_shares[symbol] = 0
		self.incremental_expected_shares_increments[symbol] = 0
		self.incremental_expected_shares_last_register[symbol] = 0
		self.incremental_expected_shares_intervals[symbol] = 0
		self.incremental_expected_shares_deadline[symbol] = 0

	def submit_incremental_expected(self,symbol,shares,time_takes,aggresive):

		if symbol not in self.banned and self.flatten_order!=True:
			with self.read_lock[symbol]:
				now = datetime.now()
				ts = now.hour*3600 + now.minute*60 + now.second 

				################################################
				# EVERYTHING HERE DEAL WITH EXPECT. OVERWRITE ALL. 

				####
				# self.incremental_state[symbol_name] = False
				# self.incremental_expected_shares[symbol_name] = 0
				# self.incremental_expected_shares_increments[symbol_name] = 0
				# self.incremental_expected_shares_last_register[symbol_name] = 0
				# self.incremental_expected_shares_intervals[symbol_name] = 0
				# self.incremental_expected_shares_deadline[symbol_name] = 0

				# STEP 1 CALC EACH INCREMENT. 
				difference = shares-self.current_shares[symbol]

				if difference!=0:

					period_number = (time_takes//4)

					increments = math.ceil(abs(difference)/period_number)

					if difference>0:
						increments = abs(increments)
					else:
						increments = increments*-1

					if increments>0 and increments<1:
						increments = 1 
					if increments<0 and increments>-1:
						increments = -1

					self.incremental_state[symbol] = True 
					self.incremental_expected_shares[symbol] = shares 
					self.incremental_expected_shares_increments[symbol] = increments
					self.incremental_expected_shares_deadline[symbol] = ts+time_takes
					self.incremental_expected_shares_last_register[symbol] = ts
					self.expected_shares[symbol] = self.current_shares[symbol]

					if increments ==1 or increments==-1:
						self.incremental_expected_shares_intervals[symbol] = 4 * abs(period_number//difference)
					else:
						self.incremental_expected_shares_intervals[symbol] = 4

					if aggresive:
						self.symbols[symbol].turn_on_aggresive_only()
					else:
						self.symbols[symbol].turn_off_aggresive_only()

					log_print(self.source,self.algo_name," incrementally expect",symbol,shares,"expect: ",shares," in:",time_takes, "increments:",increments,'interval',self.incremental_expected_shares_intervals[symbol])


					##########

	def submit_expected_shares(self,symbol,shares,aggresive=0):

		log_print(self.source,self.algo_name,"expect",symbol,shares," aggresive ", aggresive,"current have",self.current_shares[symbol])

		##################################################################################################
		##############     I THINK THIS IS WHY. ORDER STILL PROCESS UNTIL 1600   #########################
		##################################################################################################

		if symbol not in self.banned and self.flatten_order!=True:
			with self.read_lock[symbol]:
				now = datetime.now()
				ts = now.hour*3600 + now.minute*60 + now.second
				self.incremental_state[symbol] = False

				self.expected_shares[symbol] = shares
				self.recalculate_current_request(symbol)
				self.reset_incremental_data(symbol)
				
				if aggresive:

					if ts - self.recent_action_ts[symbol] >= 1 and ts<57600-30:
						self.recent_action_ts[symbol] = ts
						self.symbols[symbol].immediate_request(self.current_request[symbol])
					else:
						log_print(self.source,self.algo_name,symbol," AGGRESIVE TOO FREQUENT : ",ts - self.recent_action_ts[symbol])
				# self.notify_request(symbol)

	def recalculate_current_request(self,symbol):
		self.current_request[symbol] = self.expected_shares[symbol] - self.current_shares[symbol]

	def get_current_expected(self,symbol):

		with self.read_lock[symbol]:
			ret = self.expected_shares[symbol]
		return ret

	def get_current_share(self,symbol):

		return self.current_shares[symbol]

	def get_current_request(self,symbol):

		return self.current_request[symbol]


	def calculate_avg_price(self,symbol):

		if self.current_shares[symbol]!=0:
				self.average_price[symbol] = sum(self.current_exposure[symbol])/self.current_shares[symbol]


	def holding_update(self,symbol,share_added,price):

		if share_added<0:
			price=price*-1

		for i in range(abs(share_added)):

			if len(self.current_exposure[symbol])==0:
				self.current_exposure[symbol].append(price)

			elif self.current_exposure[symbol][-1]*price >0: #same side.
				self.current_exposure[symbol].append(price)

			elif self.current_exposure[symbol][-1]*price <0:

				self.data[REALIZED]+= -1*price - self.current_exposure[symbol].pop()
				
				#self.manager.new_record(self)
			else:
				log_print("HOLDING UPDATE ERROR")

		self.data[REALIZED] = round(self.data[REALIZED],2)
		#self.manager.new_record(self)

	def notify_holding_change(self,symbol):
		pass 
		
	def request_fufill(self,symbol,share,price):

		# if it takes, return the remaining. otherwise return it back
		prev_share = self.current_shares[symbol]
		prev_price = self.average_price[symbol]
		share_added = 0

		### 1. need to read if actually request anything
		### 2. need to verify if it's the same sign as requested.
		### WHAT HAPPENS IF PRICE IS 0 ????? ######################
		###########################################################
		###########################################################

		if self.current_request[symbol]!=0:

			if self.current_request[symbol]*share<=0:
				# wrong side, wu gui yuan zhu 
				return share 
			else:

				if abs(self.current_request[symbol])>=abs(share):  # eats everything from share 

					self.current_shares[symbol] += share 

					self.recalculate_current_request(symbol)

					share_added = share
					ret = 0 
				else:

					self.current_shares[symbol] += self.current_request[symbol]  # eats partially from share 
					
					ret = share-self.current_request[symbol] 

					share_added = self.current_request[symbol]

					self.recalculate_current_request(symbol)

				### IT ONLY CHANGE THE AVG PRICE DURING LOADING UP. NO LOADING OFF. ? no it does. actually. 

				### current share ==0 , or current share same sign as share, load.  else unload.

				# This process has a problem. if the shares causing the position flip, then it's first calcualte realized, then recaculate avg price. then it's fucked. 

				try:
					self.holding_update(symbol,share_added,price)
				except	Exception	as e:
					PrintException(e,"Basket Holding Update Error:"+self.source+symbol)
				self.calculate_avg_price(symbol)

				log_print(self.source,self.algo_name,symbol,"Loading up :incmonig,",share,"want",self.expected_shares[symbol]," now have",self.current_shares[symbol],"return",ret, "prev avg",prev_price,"cur price",self.average_price[symbol])

				return ret

		else:

			### MANUAL CONTROL SIDE ###
			change = False 
			if self.manual_addable and self.flatten_order!=True: ### NEED ON SAME SIDE. AND LESS THAN THE LIMIT. 
				if self.expected_shares[symbol]*share>=0:

					### WHATS THE MAXIUM TO ADD??? Infinity.
					self.expected_shares[symbol] += share 
					self.current_shares[symbol] += share 

					share_added = share
					ret = 0 

					change = True 

					log_print(self.source,self.algo_name,symbol,"Manual Loading UP :incmonig,",share," now have",self.current_shares[symbol],"return",ret)

			if self.manual_flattable: ### NEED ON DIFF SIDE
				if self.expected_shares[symbol]*share<=0:

					### AT MOST REDUCE IT TO 0. 

					if abs(self.current_shares[symbol]) > abs(share):

						### has remainer 
						self.expected_shares[symbol] += share 
						self.current_shares[symbol] += share 

						share_added = share
						ret = 0 

						change = True 

					else:
						### no remainder or even overflow.  

						# self.current_shares[symbol] += self.current_request[symbol]  # eats partially from share 
						# ret = share-self.current_request[symbol] 
						# share_added = self.current_request[symbol]
						ret = share + self.current_shares[symbol]
						share_added = self.current_shares[symbol] * -1 #share + self.current_shares[symbol]
						self.expected_shares[symbol] += share_added 
						self.current_shares[symbol] += share_added 

					log_print(self.source,self.algo_name,symbol,"Manual Loading off :incmonig,",share," now have",self.current_shares[symbol],"return",ret)

					change = True 

			if change:

				try:
					self.holding_update(symbol,share_added,price)
				except	Exception	as e:
					PrintException(e,"Basket Holding Update Error:"+self.source+symbol)
				self.calculate_avg_price(symbol)

				if sum(self.current_shares.values())==0:
					### COMPLETELY FLAT. ###
					self.flatten_order = True 

				return ret 


			return share


	def cancel_request(self,symbol=None):

		with self.read_lock[symbol]:
			self.current_request[symbol] = 0
			self.have_request[symbol] = False
			self.expected_shares[symbol] = self.current_shares[symbol]

	def request_granted(self,symbol=None):

		# if request becomes 0  . match off. 

		with self.read_lock[symbol]:

			self.current_request[symbol] = self.expected_shares[symbol] - self.current_shares[symbol]

			if self.current_request[symbol] ==0:
				self.have_request[symbol] = False

	def having_request(self,symbol=None):

		return self.current_request[symbol]!=0

	def get_holdings(self,symbol=None):

		return self.current_shares[symbol]

	def notify_request(self,symbol=None):

		log_print(self.source,self.algo_name," ",symbol,"have:",self.current_shares[symbol],"want:",self.expected_shares[symbol],"change:",self.current_request[symbol])
		self.have_request[symbol] = True
		self.symbols[symbol].request_notified()

	def notify__request_with_delay(self,symbol=None):

		self.symbols[[symbol]].expecting_marketorder()
		self.notify_request(symbol)

	def market_in(self,shares,symbol=None):

		if shares>0:
			self.expect_orders = LONG
		else:
			self.expect_orders = SHORT

		self.current_request = shares
		self.expected_shares = shares
		self.notify_immediate_request(shares)

	def notify_immediate_request(self,shares,symbol=None):

		# add a little delay using thread.
		self.notify__request_with_delay(symbol)

		self.symbols[symbol].immediate_request(shares)

	def read_current_request(self,symbol=None):

		return self.current_request[symbol]

	# absolute sense. 

	def set_data(self):
		#default values.
		self.tkvars[SELECTED].set(False)
		self.tkvars[RELOAD].set(False)

		self.data[ESTRISK] = 0
		self.tkvars[ESTRISK].set(0)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)

	# need to know which symbol got rejected. cancel the request. 
	def rejection_handling(self,symbol):

		#self.submit_expected_shares(symbol,0)

		self.expected_shares[symbol] = 0
		self.banned.append(symbol)

		log_print(self.source," BANNED:",symbol)

	def get_flatten_order(self):

		return self.flatten_order

	def flatten_cmd(self):
		
		# if self.tkvars[STATUS].get()==PENDING:
		# 	self.cancel_algo()
		# else:

		#self.deactive()
		log_print(self.source,self.algo_name," flattening")
		

		for symbol,item in self.symbols.items():
			self.submit_expected_shares(symbol,0)

			#if emergency.
			#item.flatten_cmd(self.algo_name)

		self.flatten_order=True

	""" Deployment initialization """

	def check_pnl(self):


		"""
		PNL, STOP TRIGGER.  ONLY CHECK EVERY 3 SECONDS 
		"""

		#now = datetime.now()
		#ts = now.hour*3600 + now.minute*60+ now.second

		total_unreal = 0

		check = {}
		for symbol,val in self.current_shares.items():

			cur_stock_price = self.symbols[symbol].get_bid()
			self.stock_price[symbol] = cur_stock_price

			if self.current_shares[symbol]!=0 and cur_stock_price!=0 and self.average_price[symbol]!=0:

				if val>0:
					total_unreal +=  ((cur_stock_price - self.average_price[symbol])-0.01) * abs(self.current_shares[symbol])  #self.data[AVERAGE_PRICE]-price
					check[symbol] = [cur_stock_price,self.average_price[symbol],self.current_shares[symbol],((cur_stock_price - self.average_price[symbol])-0.01) * abs(self.current_shares[symbol])]
					#log_print(self.algo_name,symbol,"avg price",self.average_price[symbol],"cur price",cur_stock_price,"share",val,"result", (cur_stock_price - self.average_price[symbol]) * abs(self.current_shares[symbol]))
				else:
					cur_stock_price = self.symbols[symbol].get_ask()
					total_unreal +=  ((self.average_price[symbol] - cur_stock_price)-0.01) * abs(self.current_shares[symbol]) #self.data[AVERAGE_PRICE]-price
					check[symbol] = [cur_stock_price,self.average_price[symbol],self.current_shares[symbol],((self.average_price[symbol] - cur_stock_price)-0.01) * abs(self.current_shares[symbol])]
					#log_print(self.algo_name,symbol,"avg price",self.average_price[symbol],"cur price",cur_stock_price,"share",val,"result",(self.average_price[symbol] - cur_stock_price) * abs(self.current_shares[symbol]))
		
		# self.display_count +=1

		# if self.display_count %3==0:
		# 	log_print(self.source,"PNL checking",self.algo_name,check,total_unreal,self.current_shares, self.average_price)
		
		if self.profit!=0:
			if total_unreal>self.profit:
				log_print(self.source, self.algo_name, " MEET PROFIT TARGET",self.profit)
				self.flatten_cmd()
		if self.stop!=0:
			if total_unreal*-1 > self.stop:
				log_print(self.source, self.algo_name, " MEET STOP ",self.stop)
				self.flatten_cmd()
		self.data[UNREAL] = round(total_unreal,2)
		self.tkvars[UNREAL].set(self.data[UNREAL])

		if self.data[UNREAL]<self.data[UNREAL_MIN]:
			self.data[UNREAL_MIN] = self.data[UNREAL]
			self.tkvars[UNREAL_MIN].set(self.data[UNREAL_MIN])

		if self.data[UNREAL_MAX]<self.data[UNREAL]:
			self.data[UNREAL_MAX] = self.data[UNREAL]
			self.tkvars[UNREAL_MAX].set(self.data[UNREAL_MAX])

		# log_print("Tradingplan: ",self.algo_name, " Unreal",total_unreal,"Avg",self.average_price,"Shares:",self.current_shares,"Stock prices",self.stock_price)

		#log_print("cheking unreal",self.data[UNREAL] , "target",self.data[ESTRISK]*-1)
		# if self.data[UNREAL]<self.data[ESTRISK]*-1:

		# 	log_print("TradingPlan Risk Excceded, unreal",self.data[UNREAL] , "risk",self.data[ESTRISK]*-1)
		# 	self.flatten_cmd()
		# 	self.mark_algo_status(DONE)
		# 	self.shut_down = True

		self.update_displays()

	def shutdown(self):
		self.shutdown = True 

	def update_displays(self):


		#self.tkvars[SIZE_IN].set(str(self.data[CURRENT_SHARE])+"/"+str(self.data[TARGET_SHARE]))
		self.tkvars[REALIZED].set(str(self.data[REALIZED]))

		self.tkvars[UNREAL].set(str(self.data[UNREAL]))
		#self.tkvars[UNREAL_PSHR].set(str(self.data[UNREAL_PSHR]))
		#self.tkvars[AVERAGE_PRICE].set(self.data[AVERAGE_PRICE])

		#check color.f9f9f9

		if self.data[UNREAL]>0:
			#self.tklabels[UNREAL_PSHR]["background"] = STRONGGREEN
			self.tklabels[UNREAL]["background"] = STRONGGREEN
		elif self.data[UNREAL]<0:
			#self.tklabels[UNREAL_PSHR]["background"] = STRONGRED
			self.tklabels[UNREAL]["background"] = STRONGRED
		else:
			#self.tklabels[UNREAL_PSHR]["background"] = DEFAULT
			self.tklabels[UNREAL]["background"] =DEFAULT

		if self.data[REALIZED]==0:
			self.tklabels[REALIZED]["background"] = DEFAULT
		elif self.data[REALIZED]>0:
			self.tklabels[REALIZED]["background"] = STRONGGREEN
		elif self.data[REALIZED]<0:
			self.tklabels[REALIZED]["background"] = STRONGRED

	def mark_algo_status(self,status):

		self.data[STATUS] = status
		self.tkvars[STATUS].set(status)


		if status == DEPLOYED:
			#self.input_lock(True)
			self.tklabels[STATUS]["background"] = LIGHTYELLOW

		elif status == RUNNING:
			self.tklabels[STATUS]["background"] = GREEN

		elif status == REJECTED:
			self.tklabels[STATUS]["background"] = "red"

		elif status == DONE:
			self.tklabels[STATUS]["background"] = DEEPGREEN

		elif status == PENDING:
			#self.input_lock(False)
			self.tklabels[STATUS]["background"] = DEFAULT

	def set_mind(self,str,color=DEFAULT):

		self.tkvars[MIND].set(str)
		self.tklabels[MIND]["background"]=color


	def deploy(self):


		self.data[STATUS] = DEPLOYED
		self.tkvars[STATUS].set(DEPLOYED)

