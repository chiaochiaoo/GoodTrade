from Symbol import *
from Triggers import *
from Strategy import *
from Strategy_Management import *
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
		
		self.numeric_labels = [ACTRISK,ESTRISK,CUR_PROFIT_LEVEL,CURRENT_SHARE,TARGET_SHARE,INPUT_TARGET_SHARE,AVERAGE_PRICE,LAST_AVERAGE_PRICE,\
		RISK_PER_SHARE,STOP_LEVEL,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER,PXT1,PXT2,PXT3,FLATTENTIMER,BREAKPRICE,RISKTIMER,\
		FIBCURRENT_MAX,FIBLEVEL1,FIBLEVEL2,FIBLEVEL3,FIBLEVEL4,EXIT,RELOAD_TIMES,RESISTENCE,SUPPORT]

		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO,SIZE_IN,ENTRYPLAN,ENTYPE,MANAGEMENTPLAN]

		self.bool_labels= [AUTORANGE,AUTOMANAGE,RELOAD,SELECTED,ANCART_OVERRIDE,USING_STOP]

		self.init_data(risk)

		#self.mark_algo_status(DEPLOYED)

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
	def submit_expected_shares(self,symbol,shares):

		log_print(self.algo_name,"expect",symbol,shares)
		with self.read_lock[symbol]:
			self.expected_shares[symbol] = shares
			self.current_request[symbol] = self.expected_shares[symbol] - self.current_shares[symbol]


			self.notify_request(symbol)


	def set_data(self):
		#default values.
		self.tkvars[SELECTED].set(False)
		self.tkvars[RELOAD].set(False)

		self.data[ESTRISK] = 0
		self.tkvars[ESTRISK].set(0)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)


		self.update_symbol_tkvar()

	def init_data(self,risk):


		for i in self.numeric_labels:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar(value=0)

		for i in self.string_labels:
			self.data[i] = ""
			self.tkvars[i] = tk.StringVar(value="")

		# for i in self.symbol.numeric_labels:
		# 	self.tkvars[i] = tk.DoubleVar(value=self.symbol.data[i])

		for i in self.bool_labels:
			self.data[i] = True
			self.tkvars[i] = tk.BooleanVar(value=True)

		self.data[ANCART_OVERRIDE]=False

		self.tkvars[SELECTED].set(False)
		self.tkvars[RELOAD].set(False)

		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)


	""" PASSSIVE ENTRY/EXIT OVER A PERIOD AMONT OF TIME """

	def ppro_update_price(self,symbol="",bid=0,ask=0,ts=0):

		# pass

		# if self.data[POSITION]!="":
		# 	self.check_pnl(bid,ask,ts)

		if self.current_shares[symbol]>0:
			self.stock_price[symbol] = ask 
		else:
			self.stock_price[symbol] = bid

		self.check_pnl(ts)



	def check_pnl(self,ts):


		"""
		PNL, STOP TRIGGER.  ONLY CHECK EVERY 3 SECONDS 
		"""

		#now = datetime.now()
		#ts = now.hour*3600 + now.minute*60+ now.second
		
		if ts > self.last_ts+2:

			total_unreal = 0

			for symbol,val in self.current_shares.items():

				if val>0:
					total_unreal +=  (self.stock_price[symbol] - self.average_price[symbol]) * abs(self.current_shares[symbol])  #self.data[AVERAGE_PRICE]-price
				else:
					total_unreal +=  (self.average_price[symbol] - self.stock_price[symbol]) * abs(self.current_shares[symbol]) #self.data[AVERAGE_PRICE]-price

			self.last_ts=ts
			self.data[UNREAL] = round(total_unreal,2)
			self.tkvars[UNREAL].set(self.data[UNREAL])

			if self.data[UNREAL]<-20:
				self.flatten_cmd()

			self.update_displays()

		


	def ppro_process_orders(self,price,shares,side,symbol):

		###
		with self.read_lock[symbol]:


			if side == SHORT:
				shares = -shares

			if (side == LONG and self.current_shares[symbol]>=0) or (side == SHORT and self.current_shares[symbol]<=0) :
				
				self.ppro_orders_loadup(symbol,price,shares,side)
			else:
				self.ppro_orders_loadoff(symbol,price,shares,side)

		self.request_granted(symbol)

	def ppro_orders_loadup(self,symbol,price,shares,side):


		if self.current_shares[symbol]==0:
			self.average_price[symbol] = round(price,3)
		else:
			self.average_price[symbol]= round(((self.average_price[symbol]*abs(self.current_shares[symbol]))+(price*abs(shares)))/(abs(self.current_shares[symbol])+abs(shares)),3)

		self.current_shares[symbol] = self.current_shares[symbol] + shares

		for i in range(abs(shares)):
			
			self.holdings[symbol].append(price)


		log_print(self.algo_name,symbol," load on : current:",self.current_shares[symbol])


	def ppro_orders_loadoff(self,symbol,price,shares,side):

		gain = 0

		print(self.holdings[symbol])

		if self.current_shares[symbol]>0:
			for i in range(abs(shares)):
				try:
					gain += price - self.holdings[symbol].pop()
				except Exception as e:
					log_print("TP processing: Holding calculation error,holdings are empty.",e)
		else:
			for i in range(abs(shares)):
				try:
					gain += self.holdings[symbol].pop() - price	
				except Exception as e:
					log_print("TP processing: Holding calculation error,holdings are empty.",e)	

		self.current_shares[symbol] = self.current_shares[symbol] + shares

		log_print(self.algo_name,"gain:",symbol,gain)
		self.data[REALIZED]+=gain
		self.data[REALIZED]= round(self.data[REALIZED],2)

		log_print(self.algo_name,symbol," load off : current:",self.current_shares[symbol], "gain:",gain,"realized",self.data[REALIZED])

		self.update_displays()

	def clear_trade(self):

		gain = self.data[UNREAL]
		risk = self.data[ESTRISK]

		#log_print("XXXX:",gain,risk)

		self.data[UNREAL] = 0
		self.data[UNREAL_PSHR] = 0
		self.data[TOTAL_REALIZED] += self.data[REALIZED]
		self.data[TOTAL_REALIZED] = round(self.data[TOTAL_REALIZED],2)
		self.data[REALIZED] = 0

		self.data[TARGET_SHARE] = 0
		#mark it done.

		#prevent manual conflit.
		

		##################
		self.symbol.deregister_tradingplan(self.name,self)
		self.deactive()
		self.mark_algo_status(DONE)
		self.set_mind("Trade completed.",VERYLIGHTGREEN)
		self.data[POSITION] = ""

		self.tkvars[POSITION].set("")

		#self.tklabels[AUTORANGE]["state"] = "normal"
		self.current_price_level = 0
		self.current_running_strategy = None

		#if reload is on, revert it back to entry stage. 
		if self.tkvars[RELOAD].get() == True and gain<0 and abs(gain)>0.5*risk:
			log_print("TP processing:",self.symbol_name,":"," Reload activated. Trading triggers re-initialized. reload remaining:",self.data[RELOAD_TIMES])
			self.tkvars[RELOAD].set(False)
			self.deploy()
			

	# need to know which symbol got rejected. cancel the request. 
	def rejection_handling(self,symbol):


		if self.data[STATUS] == DEPLOYED:
			# cancel whatever requested on symbol.
			# withdraw the algo. 
			# show rejection. 

			self.submit_expected_shares(symbol,0)

			#self.symbol.cancel_all_request(self.name)
			#self.mark_algo_status(REJECTED)

		else:

			log_print("rejection messge received on ",self.name)


	def get_flatten_order(self):

		return self.flatten_order

	def flatten_cmd(self):
		
		# if self.tkvars[STATUS].get()==PENDING:
		# 	self.cancel_algo()
		# else:

		#self.deactive()

		self.flatten_order=True

		for symbol,item in self.symbols.items():
			self.submit_expected_shares(symbol,0)
			item.flatten_cmd(self.algo_name)


	""" Deployment initialization """


	def deploy(self,risktimer=0):

		if self.tkvars[STATUS].get() ==PENDING or self.tkvars[STATUS].get() ==DONE:

			self.mark_algo_status(DEPLOYED)
			self.flatten_order	 = False
			#self.symbol.register_tradingplan(self.name,self)

			self.activate()

			
			# entryplan=self.tkvars[ENTRYPLAN].get()
			# #entrytimer=self.tkvar

			# if risktimer ==0:
			# 	self.data[RISKTIMER] = 9600
			# 	# int(self.tkvars[RISKTIMER].get())
			# else:
			# 	self.data[RISKTIMER] = 9600# risktimer

			# self.data[RISK_PER_SHARE] = abs(self.symbol.get_resistence()-self.symbol.get_support())

			# self.set_mind("",DEFAULT)

			# # only if it is not set. 

			# self.entry_plan_decoder(entryplan, 0)

			# self.manage_plan_decoder(self.tkvars[MANAGEMENTPLAN].get())
			# #self.manage_plan_decoder(manage_plan)

			# self.start_tradingplan()


	def cancel_algo(self):

		pass

	def cancle_deployment(self):
		pass

	def input_lock(self,lock):

		pass


	""" DATA MANAGEMENT  """
	
	def get_risk(self):
		return self.data[ESTRISK]

	def get_data(self):
		return self.data

	def update_displays(self):


		#self.tkvars[SIZE_IN].set(str(self.data[CURRENT_SHARE])+"/"+str(self.data[TARGET_SHARE]))
		self.tkvars[REALIZED].set(str(self.data[REALIZED]))
		self.tkvars[TOTAL_REALIZED].set(str(self.data[TOTAL_REALIZED]))
		self.tkvars[UNREAL].set(str(self.data[UNREAL]))
		self.tkvars[UNREAL_PSHR].set(str(self.data[UNREAL_PSHR]))
		#self.tkvars[AVERAGE_PRICE].set(self.data[AVERAGE_PRICE])

		#check color.f9f9f9

		if self.data[UNREAL_PSHR]>0:
			self.tklabels[UNREAL_PSHR]["background"] = STRONGGREEN
			self.tklabels[UNREAL]["background"] = STRONGGREEN
		elif self.data[UNREAL_PSHR]<0:
			self.tklabels[UNREAL_PSHR]["background"] = STRONGRED
			self.tklabels[UNREAL]["background"] = STRONGRED
		else:
			self.tklabels[UNREAL_PSHR]["background"] = DEFAULT
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

	"""	UI related  """
	def update_symbol_tkvar(self):
		#print("updatem",elf.symbol.get_support(),elf.symbol.get_resistence())
		self.tkvars[SUPPORT].set(self.symbol.get_support())


	""" risk related ## """

	def adjusting_risk(self):

		if self.data[POSITION] == LONG:
			self.data[ACTRISK] = round(((self.data[AVERAGE_PRICE]-self.data[STOP_LEVEL])*self.data[CURRENT_SHARE]),2)
		else:
			self.data[ACTRISK] = round(((self.data[STOP_LEVEL]-self.data[AVERAGE_PRICE])*self.data[CURRENT_SHARE]),2)

		#diff = self.data[ACTRISK]-self.data[ESTRISK]
		ratio = (self.data[ACTRISK]/self.data[ESTRISK])-0.3#self.data[ESTRISK]/diff
		if ratio>1.2 : ratio = 1.2
		if ratio<0 : ratio = 0
		##change color and change text.

		self.tklabels[RISK_RATIO]["background"] = hexcolor_red(ratio)
		self.tkvars[RISK_RATIO].set(str(self.data[ACTRISK])+"/"+str(self.data[ESTRISK]))

		if self.data[CURRENT_SHARE] == 0:
			self.tklabels[RISK_RATIO]["background"] = DEFAULT

		# HERE, IF IT IS OVER RISK. ADJUST IT. it is overwhelmed. 




# a= []


# a.append(1)
# a.append(2)

# print(a.pop(0))