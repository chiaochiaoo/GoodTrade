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

# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan_Basket:

	#symbols:Symbols,risk=None

	def __init__(self,algo_name="",risk=5,Manager=None):

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

		# First time its expected is fullfilled. shall the management starts.
		self.read_lock = {}
		self.have_request = {}

		self.expected_shares = {}
		self.current_shares = {}
		self.current_request = {}
		self.average_price = {}

		self.stock_price ={}

		self.data = {}
		self.tkvars = {}

		self.tklabels= {} ##returned by UI.

		self.holdings = {}

		self.current_price_level = 0

		self.price_levels = {}

		self.algo_ui_id = 0

		self.last_ts = 0
		
		self.numeric_labels = [ESTRISK,UNREAL,REALIZED,TOTAL_REALIZED]

		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO]

		self.bool_labels= [SELECTED]

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
		# for i in self.symbol.numeric_labels:
		# 	self.tkvars[i] = tk.DoubleVar(value=self.symbol.data[i])


	def internal(self):
		log_print(self.name,"holding:",self.current_shares ,"expected:",self.expected_shares,"requested:",self.current_request)

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

			self.average_price[symbol_name] = 0
			self.stock_price[symbol_name] = 0

			self.holdings[symbol_name] = []

			self.read_lock[symbol_name] = threading.Lock()

	def update_stockprices(self,symbol,price):

		self.stock_price[symbol] = price

	def submit_expected_shares(self,symbol,shares):

		log_print(self.algo_name,"expect",symbol,shares)

		with self.read_lock[symbol]:
			self.expected_shares[symbol] = shares
			
			self.recalculate_current_request(symbol)

			# self.notify_request(symbol)

	def recalculate_current_request(self,symbol):
		self.current_request[symbol] = self.expected_shares[symbol] - self.current_shares[symbol]

	def get_current_expected(self,symbol):

		return self.expected_shares[symbol]

	def get_current_request(self,symbol):

		return self.current_request[symbol]




	def request_fufill(self,symbol,share,price):

		# if it takes, return the remaining. otherwise return it back
		prev_share = self.current_shares[symbol]
		prev_price = self.average_price[symbol]
		if self.current_request[symbol]*share<0:
			# wu gui yuan zhu 
			return share 
		else:

			if abs(self.current_request[symbol])>=abs(share):  # eats everything
				self.current_shares[symbol] += share 

				self.recalculate_current_request(symbol)

				

				ret = 0 
			else:
				self.current_shares[symbol] += self.current_request[symbol] 
				
				ret = share-self.current_request[symbol] 
				self.recalculate_current_request(symbol)

			if self.current_shares[symbol]!=0:
				self.average_price[symbol] = (prev_share*self.average_price[symbol] + share*price)/self.current_shares[symbol]
			else:
				self.average_price[symbol] = 0 
				
			log_print(self.algo_name,symbol,"incmonig,",share,"want",self.current_request[symbol]," now have",self.current_shares[symbol],"return",ret, "prev p",prev_price,"cur price",self.average_price[symbol])

			return ret






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

		return self.have_request[symbol]

	def get_holdings(self,symbol=None):

		return self.current_shares[symbol]

	def notify_request(self,symbol=None):

		log_print(self.algo_name," ",symbol,"have:",self.current_shares[symbol],"want:",self.expected_shares[symbol],"change:",self.current_request[symbol])
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
		if self.data[STATUS] == DEPLOYED:
			self.submit_expected_shares(symbol,0)
		else:

			log_print("rejection messge received on ",self.name)


	def get_flatten_order(self):

		return self.flatten_order

	def flatten_cmd(self):
		
		# if self.tkvars[STATUS].get()==PENDING:
		# 	self.cancel_algo()
		# else:

		#self.deactive()
		log_print(self.algo_name," flattening")
		self.flatten_order=True

		for symbol,item in self.symbols.items():
			self.submit_expected_shares(symbol,0)

			#if emergency.
			#item.flatten_cmd(self.algo_name)


	""" Deployment initialization """

	def check_pnl(self):


		"""
		PNL, STOP TRIGGER.  ONLY CHECK EVERY 3 SECONDS 
		"""

		#now = datetime.now()
		#ts = now.hour*3600 + now.minute*60+ now.second
		

		total_unreal = 0

		for symbol,val in self.current_shares.items():

			if val>0:
				total_unreal +=  (self.stock_price[symbol] - self.average_price[symbol]) * abs(self.current_shares[symbol])  #self.data[AVERAGE_PRICE]-price
			else:
				total_unreal +=  (self.average_price[symbol] - self.stock_price[symbol]) * abs(self.current_shares[symbol]) #self.data[AVERAGE_PRICE]-price

		self.data[UNREAL] = round(total_unreal,2)
		self.tkvars[UNREAL].set(self.data[UNREAL])

		#log_print("cheking unreal",self.data[UNREAL] , "target",self.data[ESTRISK]*-1)
		if self.data[UNREAL]<self.data[ESTRISK]*-1:
			self.flatten_cmd()
			self.mark_algo_status(DONE)
			self.shut_down = True

		self.update_displays()


	def update_displays(self):


		#self.tkvars[SIZE_IN].set(str(self.data[CURRENT_SHARE])+"/"+str(self.data[TARGET_SHARE]))
		self.tkvars[REALIZED].set(str(self.data[REALIZED]))
		self.tkvars[TOTAL_REALIZED].set(str(self.data[TOTAL_REALIZED]))
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

		if self.data[TOTAL_REALIZED]==0:
			self.tklabels[TOTAL_REALIZED]["background"] = DEFAULT
		elif self.data[TOTAL_REALIZED]>0:
			self.tklabels[TOTAL_REALIZED]["background"] = STRONGGREEN
		elif self.data[TOTAL_REALIZED]<0:
			self.tklabels[TOTAL_REALIZED]["background"] = STRONGRED


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
