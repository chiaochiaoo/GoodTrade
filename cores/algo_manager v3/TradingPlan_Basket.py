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

	def __init__(self,algo_name="",Manager=None):

		self.algo_name = algo_name
		self.symbols = {}

		self.in_use = False
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

		self.data = {}
		self.tkvars = {}

		self.tklabels= {} ##returned by UI.

		self.holdings = {}

		self.current_price_level = 0

		self.price_levels = {}

		self.algo_ui_id = 0
		
		self.numeric_labels = [ACTRISK,ESTRISK,CUR_PROFIT_LEVEL,CURRENT_SHARE,TARGET_SHARE,INPUT_TARGET_SHARE,AVERAGE_PRICE,LAST_AVERAGE_PRICE,\
		RISK_PER_SHARE,STOP_LEVEL,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER,PXT1,PXT2,PXT3,FLATTENTIMER,BREAKPRICE,RISKTIMER,\
		FIBCURRENT_MAX,FIBLEVEL1,FIBLEVEL2,FIBLEVEL3,FIBLEVEL4,EXIT,RELOAD_TIMES,RESISTENCE,SUPPORT]

		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO,SIZE_IN,ENTRYPLAN,ENTYPE,MANAGEMENTPLAN]

		self.bool_labels= [AUTORANGE,AUTOMANAGE,RELOAD,SELECTED,ANCART_OVERRIDE,USING_STOP]

		self.init_data()


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

			self.holdings[symbol_name] = []

			self.read_lock[symbol_name] = threading.Lock()


	def request_granted(self,symbol=None):

		# if request becomes 0  . match off. 

		with self.read_lock:

			self.current_request[symbol] = self.expected_shares[symbol] - self.current_shares[symbol]

			if self.current_request[symbol] ==0:
				self.have_request[symbol] = False

	def having_request(self,symbol=None):

		return self.have_request[symbol]

	def get_holdings(self,symbol=None):

		return self.current_shares[symbol]

	def notify_request(self,symbol=None):

		log_print(self.name,"have:",self.current_shares[symbol],"want:",self.expected_shares[symbol],"change:",self.current_request[symbol])
		self.have_request[symbol] = True
		self.symbols[symbol].request_notified()

	def notify__request_with_delay(self,symbol=None):

		#time.sleep(1.5)
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

		# delayed_notification = threading.Thread(target=self.notify__request_with_delay, daemon=True)
		# delayed_notification.start()


	def read_current_request(self,symbol=None):

		return self.current_request[symbol]


	# absolute sense. 
	def submit_expected_shares(self,symbol,shares):

		with self.read_lock:
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

	def init_data(self):


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

		self.data[ESTRISK] = 0
		self.tkvars[ESTRISK].set(0)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)



	""" PASSSIVE ENTRY/EXIT OVER A PERIOD AMONT OF TIME """

	def ppro_update_price(self,symbol="",bid=0,ask=0,ts=0):

		#if bid!=self.symbol.get_bid() or ask!=self.symbol.get_ask():

			#move this to symbol
			#self.symbol.update_price(bid,ask,ts,self.tkvars[AUTORANGE].get(),self.tkvars[STATUS].get())

			#check stop. 

		#print("check_pnl",bid,ask,ts,self.current_running_strategy.get_name())

		#print("Checking status:"," Current Stategy:",self.current_running_strategy.strategy_name," strategy status:",self.current_running_strategy.get_status())

		if self.data[POSITION]!="":
			self.check_pnl(bid,ask,ts)

		#check triggers
		if self.current_running_strategy!=None:
			self.current_running_strategy.update()

		# except Exception as e:
		# 	log_print("TP issue:",e)

	def check_pnl(self,bid,ask,ts):
		"""
		PNL, STOP TRIGGER.
		"""

		#log_print("PNL CHECK ON",self.symbol_name,self.data[POSITION])
		flatten = False
		gain = 0
		stillbreak = True

		#print("check_pnl",bid,ask,ts)
		if self.data[POSITION]==LONG:

			price = bid

			#print("PRICE:",bid)
			gain = round((price-self.data[AVERAGE_PRICE]),4)

			#gap = abs(self.data[BREAKPRICE]-self.data[STOP_LEVEL])*0.05
			# if price < self.data[BREAKPRICE]:#-gap:
			# 	stillbreak = False

			if price <= self.data[STOP_LEVEL]:
				flatten=True
				#print("flatening,",price,self.data[STOP_LEVEL])
		elif self.data[POSITION]==SHORT:
			price = ask
			gain = round(self.data[AVERAGE_PRICE]-price,4)

			#gap = abs(self.data[STOP_LEVEL]-self.data[BREAKPRICE])*0.05


			# if price > self.data[BREAKPRICE]:#+gap:
			# 	stillbreak = False

			if price >=  self.data[STOP_LEVEL]:
				flatten=True
				#print("flatening,",price,)

		if self.data[CURRENT_SHARE] >0:
			self.data[UNREAL_PSHR] = gain
			self.data[UNREAL]= round(gain*self.data[CURRENT_SHARE],4)


			try:
				self.data[CUR_PROFIT_LEVEL] = self.data[UNREAL_PSHR]/self.data[RISK_PER_SHARE]
			except:
				self.data[CUR_PROFIT_LEVEL] = 0 
			#print("profit level:",round(self.data[CUR_PROFIT_LEVEL],2))

		if  self.data[UNREAL] < -self.data[ACTRISK]*0.05:#+gap:
			stillbreak = False

		##IMPlement PNL timer here

		#print(self.symbol_name,self.data[UNREAL],round(-self.data[ACTRISK]*0.1,2),self.data[BREAKPRICE],price,self.data[FLATTENTIMER],self.data[RISKTIMER],stillbreak)

		if self.data[FLATTENTIMER]==0:
			if not stillbreak: #first time set. 
				self.data[FLATTENTIMER] = ts
		else:
			if not stillbreak:
				#print(self.symbol_name,"timer:",ts-self.data[FLATTENTIMER],self.data[RISKTIMER])
				if ts-self.data[FLATTENTIMER]>self.data[RISKTIMER]:
					flatten=True
					log_print(self.symbol_name,"risk timer triggered. flattening")
			else:
				self.data[FLATTENTIMER]=0
				#print("reset flatten timer to 0")

		if flatten and self.flatten_order==False and self.data[USING_STOP]:
			self.flatten_order=True
			self.data[FLATTENTIMER]=0

			log_print(self.name,"flattening",self.data[STOP_LEVEL],self.name)

			self.flatten_cmd()



		self.update_displays()



	def ppro_process_orders(self,price,shares,side,symbol):

		###

		with self.read_lock[symbol]:


			if side == SHORT:
				shares = -shares

			if (side == LONG and self.current_request[symbol]>0) or (side == SHORT and self.current_request[symbol]<0) :
				
				self.ppro_orders_loadup(symbol,price,shares,side)
			else:
				self.ppro_orders_loadoff(symbol,price,shares,side)


	def ppro_orders_loadup(self,symbol,price,side):


		if self.current_shares[symbol]==0:
			self.average_price[symbol] = round(price,3)
		else:
			self.average_price[symbol]= round(((self.average_price[symbol]*abs(self.current_shares[symbol]))+(price*abs(shares)))/(abs(self.current_shares[symbol]+abs(shares)),3))

		self.current_shares[symbol] = self.current_shares[symbol] + shares

		for i in range(abs(shares)):
			
			self.holdings[symbol].append(price)


	def ppro_orders_loadoff(self,symbol,price,shares,side):

		self.current_shares[symbol] = self.current_shares[symbol] - shares


		gain = 0

		if self.current_shares[symbol]>0:
			for i in range(abs(shares)):
				try:
					gain += price-self.holdings[symbol].pop()
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")
		else:
			for i in range(abs(shares)):
				try:
					gain += self.holdings.pop() - price	
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")	

		self.data[REALIZED]+=gain
		self.data[REALIZED]= round(self.data[REALIZED],2)

				
	# def ppro_process_orders(self,price,shares,side,symbol):
		
	# 	log_print("TP processing:",self.symbol_name,price,shares,side)
	# 	if self.data[POSITION]=="": # 1. No position.
	# 		if self.expect_orders==side: # or self.management_plan.strategy_name=="ScalpaTron":
	# 			self.ppro_confirm_new_order(price,shares,side)
	# 		else:
	# 			log_print("TP processing: unexpected orders on",self.symbol_name)
		
	# 	else:  # 2. Have position. 

	# 		if self.data[POSITION]==side: #same side.
	# 			self.ppro_orders_loadup(price,shares,side)
	# 		else: #opposite
	# 			self.ppro_orders_loadoff(price,shares,side)

	# 	# if self.test_mode:
	# 	# 	log_print("TP processing:",self.data)
	# 	self.update_displays()
	# 	self.request_granted()

	# def ppro_confirm_new_order(self,price,shares,side):

	# 	"""set the state as running, then load up"""

	# 	log_print(self.symbol_name,"New order confirmed:",price,shares,side)
	# 	self.mark_algo_status(RUNNING)
	# 	self.data[POSITION]=side
	# 	self.tkvars[POSITION].set(side)
	# 	self.data[REALIZED] = 0
	# 	self.data[FLATTENTIMER]=0
	# 	self.flatten_order = False
	# 	self.ppro_orders_loadup(price,shares,side)


	# 	### INITIAL ACCUMULATING STAGE? ###

	# def ppro_orders_loadup(self,price,shares,side):

	# 	current = self.data[CURRENT_SHARE]

	# 	#self.symbol.load_confirmation(self.name,shares)

	# 	self.data[CURRENT_SHARE] = self.data[CURRENT_SHARE] + shares

	# 	with self.read_lock:

	# 		if side == LONG:
	# 			self.current_shares = self.current_shares + shares
	# 		elif side == SHORT:
	# 			self.current_shares = self.current_shares - shares

	# 	if self.data[CURRENT_SHARE]==0:
	# 		self.data[AVERAGE_PRICE] = round(price,3)
	# 	else:
	# 		self.data[AVERAGE_PRICE]= round(((self.data[AVERAGE_PRICE]*current)+(price*shares))/self.data[CURRENT_SHARE],3)

	# 	for i in range(shares):
			
	# 		self.holdings.append(price)

	# 	self.adjusting_risk()

	# 	if self.data[AVERAGE_PRICE]!=self.data[LAST_AVERAGE_PRICE]:
	# 		self.management_plan.on_loading_up()
			
	# 		log_print(self.symbol_name," ",side,",",self.data[AVERAGE_PRICE]," at ",self.data[CURRENT_SHARE],self.current_shares,"act risk:",self.data[ACTRISK])

	# 	self.data[LAST_AVERAGE_PRICE] = self.data[AVERAGE_PRICE]

	# def ppro_orders_loadoff(self,price,shares,side):

	# 	current = self.data[CURRENT_SHARE]

	# 	self.data[CURRENT_SHARE] = current-shares	

	# 	with self.read_lock:

	# 		if side == LONG:
	# 			self.current_shares = self.current_shares + shares
	# 		elif side == SHORT:
	# 			self.current_shares = self.current_shares - shares

	# 	log_print(self.name,"load off:",self.data[CURRENT_SHARE],self.current_shares,shares)
	# 	gain = 0

	# 	if self.data[POSITION] == LONG:
	# 		for i in range(shares):
	# 			try:
	# 				gain += price-self.holdings.pop()
	# 			except:
	# 				log_print("TP processing: Holding calculation error,holdings are empty.")
	# 	elif self.data[POSITION] == SHORT:
	# 		for i in range(shares):
	# 			try:
	# 				gain += self.holdings.pop() - price	
	# 			except:
	# 				log_print("TP processing: Holding calculation error,holdings are empty.")	

	# 	self.data[REALIZED]+=gain
	# 	self.data[REALIZED]= round(self.data[REALIZED],2)

	# 	self.adjusting_risk()

	# 	#log_print(self.symbol_name," sold:",shares," current shares:",self.data[CURRENT_SHARE],"realized:",self.data[REALIZED])

	# 	#finish a trade if current share is 0.

	# 	if self.data[CURRENT_SHARE] == 0:


	# 		self.manager.new_record(self)

	# 		self.clear_trade()

	# 		log_print(self.symbol_name,"Trade completed."," this trade:",self.data[REALIZED]," total:",self.data[TOTAL_REALIZED])

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
	def rejection_handling(self):


		if self.data[STATUS] == DEPLOYED:
			# cancel whatever requested on symbol.
			# withdraw the algo. 
			# show rejection. 

			self.submit_expected_shares(0)

			#self.symbol.cancel_all_request(self.name)
			self.mark_algo_status(REJECTED)

		else:

			log_print("rejection messge received on ",self.name)




	def flatten_cmd(self):
		
		if self.tkvars[STATUS].get()==PENDING:
			self.cancel_algo()
		else:
			self.submit_expected_shares(0)

			self.flatten_order=True
			self.symbol.flatten_cmd(self.name)


	""" Deployment initialization """


	def deploy(self,risktimer=0):

		if self.tkvars[STATUS].get() ==PENDING or self.tkvars[STATUS].get() ==DONE:

			log_print("Deploying:",self.symbol_name,self.name)

			self.mark_algo_status(DEPLOYED)
			self.flatten_order	 = False
			self.symbol.register_tradingplan(self.name,self)

			self.activate()
			
			entryplan=self.tkvars[ENTRYPLAN].get()
			#entrytimer=self.tkvar

			if risktimer ==0:
				self.data[RISKTIMER] = 9600
				# int(self.tkvars[RISKTIMER].get())
			else:
				self.data[RISKTIMER] = 9600# risktimer

			self.data[RISK_PER_SHARE] = abs(self.symbol.get_resistence()-self.symbol.get_support())

			self.set_mind("",DEFAULT)

			# only if it is not set. 

			self.entry_plan_decoder(entryplan, 0)

			self.manage_plan_decoder(self.tkvars[MANAGEMENTPLAN].get())
			#self.manage_plan_decoder(manage_plan)

			self.start_tradingplan()


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


		self.tkvars[SIZE_IN].set(str(self.data[CURRENT_SHARE])+"/"+str(self.data[TARGET_SHARE]))
		self.tkvars[REALIZED].set(str(self.data[REALIZED]))
		self.tkvars[TOTAL_REALIZED].set(str(self.data[TOTAL_REALIZED]))
		self.tkvars[UNREAL].set(str(self.data[UNREAL]))
		self.tkvars[UNREAL_PSHR].set(str(self.data[UNREAL_PSHR]))
		self.tkvars[AVERAGE_PRICE].set(self.data[AVERAGE_PRICE])

		#check color.f9f9f9

		self.tklabels[REALIZED]["background"]

		self.tklabels[UNREAL]["background"]

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




