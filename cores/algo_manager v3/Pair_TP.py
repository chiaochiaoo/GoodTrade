from Symbol import *
from Triggers import *
from Strategy import *
from Strategy_Management import *

from Strategy_Management_Pair import *

from constant import*
from Util_functions import *
import tkinter as tkvars
import time
import threading
import random
# MAY THE MACHINE GOD BLESS THY AIM



# PTP

# Different Stop level - purely on PNL based. shares are already given. 
# Symbol1 , Symbol2, Share 1, Share 2. 

class PairTP:


	def __init__(self,name:"",Symbol1,Symbol2,ratio,share,manage_plan=None,risk=None,TEST_MODE=False,algo_name="",Manager=None):

		self.name = name 

		self.pair_plan = True
		self.in_use = True

		#self.read_lock = threading.Lock()
		
		self.read_lock = {}
		self.read_lock[Symbol1.ticker] = threading.Lock()
		self.read_lock[Symbol2.ticker] = threading.Lock()
		self.pair_read_lock = threading.Lock()

		self.management_start = False

		### MANAGEMENT DATA #####

		self.ratio = ratio

		self.expected_pairs = share
		self.current_pairs = 0
		self.current_request_pairs = 0

		self.have_request = {}
		self.have_request[Symbol1.ticker] = False
		self.have_request[Symbol2.ticker] = False

		self.expected_shares = {}
		self.expected_shares[Symbol1.ticker] = 0
		self.expected_shares[Symbol2.ticker] = 0

		self.current_shares = {}
		self.current_shares[Symbol1.ticker] = 0
		self.current_shares[Symbol2.ticker] = 0

		self.current_request = {}
		self.current_request[Symbol1.ticker] = 0
		self.current_request[Symbol2.ticker] = 0

		###########################################
		self.symbols ={}

		self.symbol1 = Symbol1.ticker
		self.symbol2 = Symbol2.ticker

		self.symbols[Symbol1.ticker] = Symbol1
		self.symbols[Symbol2.ticker] = Symbol2

		self.side = {}

		if ratio[0]>0:
			self.side[self.symbol1] = LONG
		else:
			self.side[self.symbol1] = SHORT

		if ratio[1]>0:
			self.side[self.symbol2] = LONG
		else:
			self.side[self.symbol2] = SHORT
		
		if abs(ratio[0])>=abs(ratio[1]):
			self.main_symbol = self.symbol1
			self.matching_symbol = self.symbol2
			self.main_ratio = self.ratio[0]
			self.matching_ratio = self.ratio[1]
		else:
			self.main_symbol = self.symbol2
			self.matching_symbol = 	self.symbol1		
			self.main_ratio = self.ratio[1]
			self.matching_ratio = self.ratio[0]
		# self.symbol1share = share1
		# self.symbol2share = share2

		#self.symbol.set_tradingplan(self)

		self.manager = Manager

		self.symbol_name = Symbol1.ticker[:-3] + ":" + Symbol2.ticker[:-3] #symbol.get_name()

		self.test_mode = TEST_MODE

		self.current_running_strategy = None
		self.entry_strategy_start = False

		self.entry_plan = None
		self.entry_type = None
		self.management_plan = None
		self.algo_name = algo_name

		#self.default_reload = default_reload
		#self.ppro_out = ppro_out

		self.expect_orders = ""

		# self.expect_long = False
		# self.expect_short = False

		self.flatten_order = False

		self.data = {}
		self.tkvars = {}

		self.tklabels= {} #returned by UI.

		self.holdings1 = []
		self.holdings2 = []


		self.current_price_level = 0
		self.price_levels = {}

		self.passive_in_process = False
		self.passive_position = ""
		self.passive_action = ""
		self.passive_current_shares = 0
		self.passive_init_shares = 0
		self.passive_remaining_shares = 0
		self.passive_price = 0

		self.passive_boundary = 0

		self.algo_ui_id = 0
		
		self.numeric_labels = [ACTRISK,ESTRISK,CUR_PROFIT_LEVEL,SYMBOL1_SHARE,SYMBOL2_SHARE,INPUT_TARGET_SHARE,AVERAGE_PRICE,AVERAGE_PRICE1,AVERAGE_PRICE2,LAST_AVERAGE_PRICE,RISK_PER_SHARE,STOP_LEVEL,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER,PXT1,PXT2,PXT3,FLATTENTIMER,BREAKPRICE,RISKTIMER,FIBCURRENT_MAX,FIBLEVEL1,FIBLEVEL2,FIBLEVEL3,FIBLEVEL4,EXIT]
		
		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO,SIZE_IN,ENTRYPLAN,ENTYPE,MANAGEMENTPLAN]

		self.bool_labels= [AUTORANGE,AUTOMANAGE,RELOAD,SELECTED,ANCART_OVERRIDE,USING_STOP]

		self.init_data(risk,manage_plan)


	""" Initialization Steps """

	def deactive(self):
		self.in_use = False

	def activate(self):
		self.in_use	 = True

	def if_activated(self):
		return self.in_use

	def set_data(self,risk,manage_plan,support,resistence):

		#default values.
		self.tkvars[SELECTED].set(False)
		self.tkvars[RELOAD].set(False)

		#self.data[RELOAD_TIMES]=self.default_reload
		#Non String, Non Numeric Value

		#Set some default value
		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))
 
		# self.tkvars[ENTRYPLAN].set(entry_plan)
		# self.tkvars[ENTYPE].set(entry_type)
		self.tkvars[MANAGEMENTPLAN].set(manage_plan)

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)

		self.update_symbol_tkvar()

	def init_data(self,risk,manage_plan):


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

		#default values.

		self.tkvars[SELECTED].set(False)
		self.tkvars[RELOAD].set(False)

		#self.data[RELOAD_TIMES]=self.default_reload
		#Non String, Non Numeric Value
		#Set some default value

		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		# self.tkvars[ENTRYPLAN].set(entry_plan)
		# self.tkvars[ENTYPE].set(entry_type)

		self.tkvars[MANAGEMENTPLAN].set(manage_plan)

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)

		# self.entry_plan_decoder(entry_plan,entry_type)
		# self.manage_plan_decoder(manage_plan)



	""" SHARES MANAGEMENT """

	def request_granted(self,symbol):

		# if request becomes 0  . match off. 
		print(self.name,symbol,"request granted",self.current_shares[symbol],self.expected_shares[symbol])
		with self.read_lock[symbol]:

			self.current_request[symbol] = self.expected_shares[symbol] - self.current_shares[symbol]

			if self.current_request[symbol] ==0:
				self.have_request[symbol] = False

		if not self.management_start and self.current_request[self.symbol1] ==0 and self.current_request[self.symbol2] ==0:
			self.entry_strategy_done()
			self.management_start = True

	def having_request(self,symbol):

		#Called by the symbol to see if there is specific request by the TP. 
		return self.have_request[symbol]

	def get_holdings(self,symbol):

		return self.current_shares[symbol]

	def notify_request(self,symbol):

		log_print(self.name,symbol,"Notify Request","have:",self.current_shares[symbol],"want:",self.expected_shares[symbol],"change:",self.current_request[symbol])
		self.have_request[symbol] = True
		#self.symbol.request_notified()
		self.symbols[symbol].request_notified()

	# def notify__request_with_delay(self,symbol):

	# 	#time.sleep(1.5)


	def notify_immediate_request(self,shares,symbol):

		# add a little delay using thread.

		
		
		self.symbols[symbol].expecting_marketorder()

		

		if symbol==self.matching_symbol:
			#self.expected_shares[symbol] += shares

			previous_request = self.current_request[symbol]
			self.submit_expected_shares(shares,symbol)

		#print(symbol,"request:",self.expected_shares)
		self.symbols[symbol].immediate_request(self.current_request[symbol]-previous_request)
		self.notify_request(symbol)

		# delayed_notification = threading.Thread(target=self.notify__request_with_delay, daemon=True)
		# delayed_notification.start()

	def read_current_request(self,symbol):

		return self.current_request[symbol]
		# with self.read_lock:
		# 	r,e = self.current_request,self.expected_shares
		# return r,e

	# INTERNAL USE
	def submit_expected_shares(self,shares,symbol):

		with self.read_lock[symbol]:

			self.expected_shares[symbol] = int(shares)
			self.current_request[symbol] = int(self.expected_shares[symbol]) - int(self.current_shares[symbol])


			self.notify_request(symbol)

			log_print(self.name,"submit_expected_shares",symbol,self.expected_shares[symbol],self.current_request[symbol])

	def change_to_shares(self,shares,symbol=None,immediately=False):

		log_print(self.symbol_name, "change to shares:",shares, "immediately:",immediately)

		flatten = False
		with self.read_lock[symbol]:

			#rationality check. if greater and opposite of current shares. just set to 0.

			if shares*self.current_shares[symbol]<0 and abs(shares)>abs(self.current_shares[symbol]):
				self.submit_expected_shares(0,symbol)
				flatten= True
				#if immediately. just go flatten then. 


			else:
				self.expected_shares[symbol] += shares
				self.current_request[symbol] = self.expected_shares[symbol] - self.current_shares[symbol]

			if not immediately:
				self.notify_request(symbol)
			else:
				if flatten:
					self.flatten_cmd()
				else:
					self.notify_immediate_request(self.current_request,symbol)




	""" PAIR MANAGEMENT """


	def submit_expected_pairs(self,pairs):

		log_print(self.name," expected paris",self.current_pairs,self.expected_pairs)
		with self.pair_read_lock:
			self.expected_pairs = int(pairs)
			self.current_request_pairs = int(self.expected_pairs) - int(self.current_pairs)

			# now i need to figure out who needs from whom. 

			self.expected_shares[self.main_symbol] = int(self.current_request_pairs*self.main_ratio)
			#self.expected_shares[self.symbol2] = int(self.current_request_pairs*self.ratio[1])

			# put the main to work.

			if pairs ==0:
				self.submit_expected_shares(0,self.main_symbol)
			else:
				self.submit_expected_shares(self.expected_shares[self.main_symbol],self.main_symbol)
			#self.submit_expected_shares(self.expected_shares[self.symbol2],self.symbol2)


			log_print(self.name,": want",self.expected_pairs," pairs,","main symbol",self.main_symbol,self.current_request_pairs*self.main_ratio,\
				"maching symbol",self.matching_symbol,self.current_request_pairs*self.matching_ratio)

			# self.current_request[self.symbol1] = 
			# self.current_request[self.symbol2] =

	def pairs_count(self):

		### change the state of the thing. 

		with self.pair_read_lock:

			self.current_pairs = min(self.current_shares[self.main_symbol]//self.main_ratio,self.current_shares[self.main_symbol]//self.main_ratio)


	def recalibrated_pairs(self):

		# count. according to the shares. how many pairs i do have now
		# By knowing much many shares i have. compute the pairs. 
		# if I get out too much? get out too less? 

		### I want X% increment at most each request ### But this is other version. Current version, see the imbalance, cancel all position, punch in. minimal latency principles.

		#recheck the holdings of two.


		#self.symbols[othersymbool].incoming_shares_pairing()


		matching_expected = (self.current_shares[self.main_symbol]//self.main_ratio)* self.matching_ratio

		log_print(self.name,"imbalance pair imbalance check:, current :",self.current_shares[self.main_symbol],self.current_shares[self.matching_symbol])


		self.notify_immediate_request(matching_expected,self.matching_symbol)


		#log_print("recalibration ends")


	""" PASSSIVE ENTRY/EXIT OVER A PERIOD AMONT OF TIME """


	def ppro_update_price(self,symbol="",bid=0,ask=0,ts=0):

		#if bid!=self.symbol.get_bid() or ask!=self.symbol.get_ask():

			#move this to symbol
			#self.symbol.update_price(bid,ask,ts,self.tkvars[AUTORANGE].get(),self.tkvars[STATUS].get())

			#check stop. 

		flatten = False

		#if self.data[POSITION]!="":
			#self.check_pnl(bid,ask,ts)

		### depending on the postition. 

		if self.management_start:

			if self.side[self.symbol1]==LONG:
				gain = (self.symbols[self.symbol1].get_bid() - self.data[AVERAGE_PRICE1]) *self.data[SYMBOL1_SHARE]
			else:
				gain = (self.data[AVERAGE_PRICE1]-self.symbols[self.symbol1].get_ask()) *self.data[SYMBOL1_SHARE]

			if self.side[self.symbol2]==LONG:
				gain +=(self.symbols[self.symbol2].get_bid() -  self.data[AVERAGE_PRICE2] ) *self.data[SYMBOL2_SHARE]
			else:
				gain +=( self.data[AVERAGE_PRICE2]- self.symbols[self.symbol2].get_ask() ) *self.data[SYMBOL2_SHARE]

			#print(self.symbols[self.symbol1].get_bid(),self.data[AVERAGE_PRICE1],self.data[AVERAGE_PRICE2],self.symbols[self.symbol2].get_ask() )
			self.data[UNREAL]= round(gain,2)

			if gain + self.data[ESTRISK] <0:
				flatten = True


		#check triggers
		#print("updating",self.current_running_strategy)
		if self.current_running_strategy!=None:
			self.current_running_strategy.update()

		if flatten:
			self.flatten_order = True
			self.flatten_cmd()

		if self.flatten_order and self.if_activated():

			self.submit_expected_pairs(0)
		# except Exception as e:
		# 	log_print("TP issue:",e)

		self.update_displays()

	def ppro_process_orders(self,price,shares,side,symbol):
		
		log_print("TP processing:",self.name,price,shares,side)



		if self.side[symbol] == side:
			self.ppro_orders_loadup(price,shares,side,symbol)
		else:
			self.ppro_orders_loadoff(price,shares,side,symbol)


		self.update_displays()

		#check the other holdings? need to avoid loop. 
		self.request_granted(symbol)

		
		if symbol == self.main_symbol and self.if_activated():
			# may call the function again. 

			self.recalibrated_pairs()

		self.pairs_count()

		log_print(self.name,'current',self.current_shares,'expected',self.expected_shares,'request',self.current_request)

	def ppro_orders_loadup(self,price,shares,side,symbol):

		self.mark_algo_status(RUNNING)

		if symbol == self.symbol1:

			CURRENT = SYMBOL1_SHARE
			AVG_P = AVERAGE_PRICE1
			holding = self.holdings1

		elif symbol == self.symbol2:

			CURRENT = SYMBOL2_SHARE
			AVG_P = AVERAGE_PRICE2
			holding = self.holdings2

		current = self.data[CURRENT]

		self.data[CURRENT] = self.data[CURRENT] + shares

		with self.read_lock[symbol]:
			if side ==LONG:
				self.current_shares[symbol] += shares
			else:
				self.current_shares[symbol] -= shares

		if current ==0 or self.data[CURRENT]==0:
			self.data[AVG_P] = round(price,3)
		else:
			self.data[AVG_P]= round(((self.data[AVG_P]*current)+(price*shares))/self.data[CURRENT],3)

		for i in range(shares):
			holding.append(price)

		#self.adjusting_risk()

		# if self.data[AVG_P]!=self.data[LAST_AVERAGE_PRICE]:
		# 	self.management_plan.on_loading_up()
			
		# 	log_print(self.symbol_name," ",side,",",self.data[AVG_P]," at ",self.data[CURRENT],"act risk:",self.data[ACTRISK])

		# self.data[LAST_AVERAGE_PRICE] = self.data[AVG_P]

	def ppro_orders_loadoff(self,price,shares,side,symbol):

		#print("load off",symbol,price,shares,side)

		if symbol == self.symbol1:

			CURRENT = SYMBOL1_SHARE
			AVG_P = AVERAGE_PRICE1
			holding = self.holdings1
		elif symbol == self.symbol2:

			CURRENT = SYMBOL2_SHARE
			AVG_P = AVERAGE_PRICE2
			holding = self.holdings2


		current = self.data[CURRENT]

		self.data[CURRENT] = current-shares	
		
		with self.read_lock[symbol]:
			if side ==LONG:
				self.current_shares[symbol] += shares
			else:
				self.current_shares[symbol] -= shares

		gain = 0

		if symbol == self.symbol1:
			for i in range(shares):
				try:
					gain += price-holding.pop()
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")
		elif symbol == self.symbol2:
			for i in range(shares):
				try:
					gain +=  holding.pop() - price 	
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")	

		self.data[REALIZED]+=gain
		self.data[REALIZED]= round(self.data[REALIZED],2)

		#self.adjusting_risk()

		#log_print(self.symbol_name," sold:",shares," current shares:",self.data[CURRENT],"realized:",self.data[REALIZED])

		#finish a trade if current share is 0.

		if self.data[SYMBOL1_SHARE] == 0 and self.data[SYMBOL2_SHARE] == 0:


			self.manager.new_record(self)

			self.clear_trade()
			log_print(self.symbol_name,"Trade completed."," this trade:",self.data[REALIZED]," total:",self.data[TOTAL_REALIZED])


	def clear_trade(self):


		#self.ppro_out.send([DEREGISTER,self.symbol_name])
		#self.ppro_out.send(["Flatten",self.symbol_name])

		
		self.data[UNREAL] = 0
		self.data[UNREAL_PSHR] = 0
		self.data[TOTAL_REALIZED] += self.data[REALIZED]
		self.data[TOTAL_REALIZED] = round(self.data[TOTAL_REALIZED],2)
		self.data[REALIZED] = 0

		self.data[TARGET_SHARE] = 0
		#mark it done.

		#prevent manual conflit.
		self.expect_orders = ""
		##################
		self.deactive()
		self.mark_algo_status(DONE)
		self.set_mind("Trade completed.",VERYLIGHTGREEN)
		self.data[POSITION] = ""

		self.tkvars[POSITION].set("")

		#self.tklabels[AUTORANGE]["state"] = "normal"
		self.current_price_level = 0
		self.current_running_strategy = None

		#if reload is on, revert it back to entry stage. 
		if self.tkvars[RELOAD].get() == True:
			log_print("TP processing:",self.symbol_name,":"," Reload activated. Trading triggers re-initialized. reload remaining:")
			self.tkvars[RELOAD].set(False)
			self.start_tradingplan()

	def ppro_order_rejection(self):

		self.mark_algo_status(REJECTED)

	def rejection_handling(self):


		### if have position, ignore. ###


		### if no position, flatten. ###

		if self.management_start!=True:

			self.data[STATUS] = REJECTED
			log_print("rejection messge received on ",self.name)
			self.flatten_cmd()


			

	""" Trade management """

	def manage_trades(self,side,action,percentage,passive):

		process = False
		if side!=None:
			if self.data[POSITION] == side:
				process = True
		else:
			process = True

		if self.data[CURRENT]>0 and process:
			shares = int(self.data[CURRENT]*percentage)
			pproaction = ""
			if shares ==0:
				shares = 1

			if action ==ADD:
				if self.data[POSITION] == LONG:
					pproaction = BUY
				elif self.data[POSITION] == SHORT:
					pproaction = SELL
			elif action ==MINUS:
				if self.data[POSITION] == LONG:
					pproaction = SELL
				elif self.data[POSITION] == SHORT:
					pproaction = BUY

			description = "Trades aggregation"
			if pproaction!="":

				if passive:

					if percentage ==1:
						self.passive_initialization(pproaction,shares,final_target=0)
					else:
						self.passive_initialization(pproaction,shares)
				else:
					self.ppro_out.send([pproaction,self.symbol_name,shares,description])

	def flatten_cmd(self):
		
		if self.tkvars[STATUS].get()==PENDING:
			self.cancel_algo()
		else:

			self.flatten_order= True

			self.submit_expected_pairs(0)
			# once the flatten cmd is on. NoMore management received.


			# self.ppro_out.send(["Flatten",self.symbol_name])
			#self.symbols[self.symbol1].new_request(self.name,-1*self.data[SYMBOL1_SHARE])
			#self.symbols[self.symbol2].new_request(self.name,self.data[SYMBOL2_SHARE])
			# if self.data[POSITION]==LONG:
				
			# elif self.data[POSITION]==SHORT:
				
	def update_displays(self):

		self.tkvars[SIZE_IN].set(str(self.current_pairs)+" |"+str(self.data[SYMBOL1_SHARE])+"/"+str(-self.data[SYMBOL2_SHARE]))
		self.tkvars[REALIZED].set(str(self.data[REALIZED]))
		self.tkvars[TOTAL_REALIZED].set(str(self.data[TOTAL_REALIZED]))
		self.tkvars[UNREAL].set(str(self.data[UNREAL]))
		self.tkvars[UNREAL_PSHR].set(str(self.data[UNREAL_PSHR]))
		self.tkvars[AVERAGE_PRICE].set(str(self.data[AVERAGE_PRICE1])+"/"+str(self.data[AVERAGE_PRICE2]))

		#check color.f9f9f9

		self.tklabels[REALIZED]["background"]

		self.tklabels[UNREAL]["background"]

		if self.data[UNREAL]>0:
			self.tklabels[UNREAL_PSHR]["background"] = STRONGGREEN
			self.tklabels[UNREAL]["background"] = STRONGGREEN
		elif self.data[UNREAL]<0:
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

		current_level = self.current_price_level

		if  current_level==1:
			self.tklabels[PXT1]["background"] = LIGHTYELLOW
			self.tklabels[PXT2]["background"] = DEFAULT
			self.tklabels[PXT3]["background"] = DEFAULT
		elif  current_level==2:
			self.tklabels[PXT1]["background"] = DEFAULT
			self.tklabels[PXT2]["background"] = LIGHTYELLOW
			self.tklabels[PXT3]["background"] = DEFAULT
		elif  current_level==3:
			self.tklabels[PXT1]["background"] = DEFAULT
			self.tklabels[PXT2]["background"] = DEFAULT
			self.tklabels[PXT3]["background"] = LIGHTYELLOW
		else:
			self.tklabels[PXT1]["background"] = DEFAULT
			self.tklabels[PXT2]["background"] = DEFAULT
			self.tklabels[PXT3]["background"] = DEFAULT	

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

			#if reload is on, turn it back on.
		# elif status == CANCELED:#canceled 

		# 	if self.order_tkstring[id_]["algo_status"].get() == "Pending":
		# 		self.order_tkstring[id_]["algo_status"].set(status)

	def set_mind(self,str,color=DEFAULT):

		self.tkvars[MIND].set(str)
		self.tklabels[MIND]["background"]=color

	""" DATA MANAGEMENT  """
	
	def get_risk(self):
		return self.data[ESTRISK]

	def get_data(self):
		return self.data

	def get_flatten_order(self):
		return False #self.flatten_order

	""" Deployment initialization """

	def input_lock(self,lock):

		state =""
		if lock: state="disabled"
		else: state = "normal"

		self.tklabels[ENTRYPLAN]["state"] = state
		self.tklabels[ENTYPE]["state"] = state
		self.tklabels[TIMER]["state"] = state
		self.tklabels[MANAGEMENTPLAN]["state"] = state
		self.tklabels[AUTORANGE]["state"] = state

	def cancel_algo(self):
		if self.tkvars[STATUS].get()==PENDING:
			self.mark_algo_status(CANCELED)

	def cancle_deployment(self):
		if self.data[POSITION] =="" and self.data[SYMBOL1_SHARE]==0 and self.data[SYMBOL2_SHARE]==0:
			self.mark_algo_status(PENDING)
			self.stop_tradingplan()
		else:
			log_print("cannot cancel, holding positions.")

	def deploy(self,risktimer=0):

		if self.tkvars[STATUS].get() ==PENDING:

			self.symbols[self.symbol1].register_tradingplan(self.name,self) 
			self.symbols[self.symbol2].register_tradingplan(self.name,self) 

			self.activate()
			self.submit_expected_pairs(self.expected_pairs)



			manage_plan =self.tkvars[MANAGEMENTPLAN].get()


		

			if risktimer ==0:
				self.data[RISKTIMER] = int(self.tkvars[RISKTIMER].get())
			else:
				self.data[RISKTIMER] = risktimer

			#self.data[RISK_PER_SHARE] = abs(self.symbol.get_resistence()-self.symbol.get_support())

			self.set_mind("",DEFAULT)
			#self.entry_plan_decoder(entryplan, entry_type, entrytimer)
			#self.manage_plan_decoder(manage_plan)

			self.start_tradingplan()

			# if self.AR_toggle_check():
			# 	try:
			# 		log_print("Deploying:",self.symbol_name,self.entry_plan.get_name(),self.symbol.get_support(),self.symbol.get_resistence(),entry_type,entrytimer,self.management_plan.get_name(),"risk:",self.data[ESTRISK],"risk timer:",self.data[RISKTIMER],"reload:",self.data[RELOAD_TIMES],"rps",self.data[RISK_PER_SHARE])
			# 	except:
			# 		pass
			# 	self.start_tradingplan()

			# except Exception as e:

			# 	log_print("Deplying Error:",self.symbol_name,e)
	
	def start_tradingplan(self):
		self.mark_algo_status(DEPLOYED)

		#self.entry_plan.on_deploying()
		self.management_plan.on_deploying()
		#self.current_running_strategy = self.entry_plan

		# if self.tkvars[RELOAD].get()==False:
		# 	#print("h",self.data[RELOAD_TIMES] )
		# 	if self.data[RELOAD_TIMES] >0:
		# 		self.tkvars[RELOAD].set(True)
		# 		self.data[RELOAD_TIMES] -= 1
		# 		if self.data[RELOAD_TIMES]== 0:
		# 			log_print(self.symbol_name," no more reload.")


	def stop_tradingplan(self):
		self.current_running_strategy = None



	def set_EntryStrategy(self,entry_plan:Strategy):
		self.entry_plan = entry_plan
		#self.entry_plan.set_symbol(self.symbol,self)

		self.data[ENTRYPLAN] = entry_plan.get_name()
		#self.tkvars[ENTRYPLAN].set(entry_plan.get_name())

	def set_ManagementStrategy(self,management_plan:Strategy):
		self.management_plan = management_plan
		self.management_plan.set_symbol(self.symbol,self)		
		self.data[MANAGEMENTPLAN] = management_plan.get_name()

	def on_finish(self,plan):
		
		if plan==self.entry_plan:
			log_print(self.symbol_name,self.entry_plan.get_name()," completed.")
			#self.entry_strategy_done()
			# done = threading.Thread(target=self.entry_strategy_done, daemon=True)
			# done.start()
		elif plan==self.management_plan:
			self.management_strategy_done()
			log_print(self.symbol_name,"management strategy completed.")
		else:
			log_print("Trading Plan: UNKONW CALL FROM Strategy",plan)

	def entry_strategy_done(self):

		#log_print(self.symbol_name,self.entry_plan.get_name()," loaded. management starts.")

		self.set_mind("Managemetn Starts:",GREEN)
		#self.management_plan.on_start()
		self.current_running_strategy = self.management_plan

	def management_strategy_done(self):

		pass


	""" Plan Handler """	
	def entry_plan_decoder(self,entry_plan,entry_type,entrytimer):

		if entry_type ==None or entry_type ==INSTANT:
			instant = 1 
		if entry_type ==INCREMENTAL:
			instant = 3 
		if entry_type ==INCREMENTAL2:
			instant = 5

		if instant >1:
			if entrytimer<5:
				entrytimer = 5

		if entry_plan == BREAKANY:
			self.set_EntryStrategy(BreakAny(entrytimer,instant,self.symbol,self))
		elif entry_plan == BREAKUP:
			self.set_EntryStrategy(BreakUp(entrytimer,instant,self.symbol,self))
		elif entry_plan == BREAKDOWN:
			
			self.set_EntryStrategy(BreakDown(entrytimer,instant,self.symbol,self))
		elif entry_plan == BREAISH:
			self.set_EntryStrategy(Bearish(entrytimer,instant,self.symbol,self))
		elif entry_plan == BULLISH:
			self.set_EntryStrategy(Bullish(entrytimer,instant,self.symbol,self))
		elif entry_plan == RIPSELL:
			self.set_EntryStrategy(Ripsell(entrytimer,instant,self.symbol,self))
		elif entry_plan == DIPBUY:
			self.set_EntryStrategy(Dipbuy(entrytimer,instant,self.symbol,self))
		elif entry_plan == FADEANY:
			self.set_EntryStrategy(Fadeany(entrytimer,instant,self.symbol,self))
		elif entry_plan == BREAKFIRST:
			self.set_EntryStrategy(BreakFirst(entrytimer,instant,self.symbol,self))

		elif entry_plan == FREECONTROL:
			self.set_EntryStrategy(FreeControl(entrytimer,instant,self.symbol,self))
		elif entry_plan == INSTANTLONG:
			self.set_EntryStrategy(InstantLong(self.symbol,self))
		elif entry_plan == INSTANTSHORT:
			self.set_EntryStrategy(InstantShort(self.symbol,self))
		elif entry_plan == TARGETLONG:
			self.set_EntryStrategy(TargetLong(self.symbol,self))
		elif entry_plan == TARGETSHORT:
			self.set_EntryStrategy(TargetShort(self.symbol,self))


		else:
			log_print("unkown plan")
			self.set_EntryStrategy(BreakAny(entrytimer,instant,self.symbol,self))

	def manage_plan_decoder(self,manage_plan):

		if manage_plan ==NONE: self.tkvars[MANAGEMENTPLAN].set(NONE)


		elif manage_plan == MARKETMAKING:
			self.set_ManagementStrategy(MarketMaking(self.symbols[self.symbol1],self.symbols[self.symbol2],self))

		elif manage_plan == THREE_TARGETS:
			self.set_ManagementStrategy(ThreePriceTargets(self.symbol,self))
		elif manage_plan == SMARTTRAIL:
			self.set_ManagementStrategy(SmartTrail(self.symbol,self))


		elif manage_plan == ONETOTWORISKREWARD:
			self.set_ManagementStrategy(OneToTWORiskReward(self.symbol,self))

		elif manage_plan == ONETOTWOWIDE:
			self.set_ManagementStrategy(OneToTwoWideStop(self.symbol,self))

		elif manage_plan == ONETOTWORISKREWARDOLD:
			self.set_ManagementStrategy(OneToTWORiskReward_OLD(self.symbol,self))

		elif manage_plan == FULLMANUAL:
			self.set_ManagementStrategy(FullManual(self.symbol,self))
		elif manage_plan == SEMIMANUAL:
			self.set_ManagementStrategy(SemiManual(self.symbol,self))

		elif manage_plan == SCALPATRON:
			self.set_ManagementStrategy(ScalpaTron(self.symbol,self))

		elif manage_plan == EMASTRAT:
			self.set_ManagementStrategy(EMAStrategy(self.symbol,self))

		elif manage_plan == TRENDRIDER:
			self.set_ManagementStrategy(TrendStrategy(self.symbol,self))

		else:
			#set default
			log_print("Setting default plan")
			self.set_ManagementStrategy(OneToTWORiskReward(self.symbol,self))

		self.current_running_strategy = self.management_plan



	# def ppro_confirm_new_order(self,price,shares,side):

	# 	"""set the state as running, then load up"""

	# 	log_print(self.symbol_name,"New order confirmed:",price,shares,side)

	# 	self.mark_algo_status(RUNNING)

	# 	# self.data[POSITION]=side
	# 	# self.tkvars[POSITION].set(side)
	# 	self.data[REALIZED] = 0
	# 	self.data[FLATTENTIMER]=0
	# 	self.flatten_order = False
	# 	self.ppro_orders_loadup(price,shares,side)