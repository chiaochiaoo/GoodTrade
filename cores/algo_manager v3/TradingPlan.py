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

class TradingPlan:

	def __init__(self,name:"",symbol:Symbol,entry_plan=None,manage_plan=None,support=0,resistence=0,risk=None,TEST_MODE=False,algo_name="",Manager=None):

		self.name = name 
		self.symbol = symbol

		
		#self.symbol.set_tradingplan(self)

		self.manager = Manager

		self.symbol_name = symbol.get_name()
		self.test_mode = TEST_MODE

		self.current_running_strategy = None
		self.entry_strategy_start = False

		self.entry_plan = None

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

		self.tklabels= {} ##returned by UI.

		self.holdings = []
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
		
		self.numeric_labels = [ACTRISK,ESTRISK,CUR_PROFIT_LEVEL,CURRENT_SHARE,TARGET_SHARE,INPUT_TARGET_SHARE,AVERAGE_PRICE,LAST_AVERAGE_PRICE,\
		RISK_PER_SHARE,STOP_LEVEL,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER,PXT1,PXT2,PXT3,FLATTENTIMER,BREAKPRICE,RISKTIMER,\
		FIBCURRENT_MAX,FIBLEVEL1,FIBLEVEL2,FIBLEVEL3,FIBLEVEL4,EXIT,RELOAD_TIMES,RESISTENCE,SUPPORT]


		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO,SIZE_IN,ENTRYPLAN,ENTYPE,MANAGEMENTPLAN]

		self.bool_labels= [AUTORANGE,AUTOMANAGE,RELOAD,SELECTED,ANCART_OVERRIDE,USING_STOP]

		self.init_data(risk,entry_plan,manage_plan,support,resistence)


	def set_data(self,risk,entry_plan,manage_plan,support,resistence):
		#default values.
		self.tkvars[SELECTED].set(False)
		self.tkvars[RELOAD].set(False)
		#self.data[RELOAD_TIMES]=self.default_reload
		#Non String, Non Numeric Value

		#Set some default value
		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		self.tkvars[ENTRYPLAN].set(entry_plan)

		self.tkvars[MANAGEMENTPLAN].set(manage_plan)

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)

		self.data[SUPPORT] = support
		self.data[RESISTENCE] = resistence

		self.update_symbol_tkvar()

	def init_data(self,risk,entry_plan,manage_plan,support,resistence):


		for i in self.numeric_labels:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar(value=0)

		for i in self.string_labels:
			self.data[i] = ""
			self.tkvars[i] = tk.StringVar(value="")

		for i in self.symbol.numeric_labels:
			self.tkvars[i] = tk.DoubleVar(value=self.symbol.data[i])

		for i in self.bool_labels:
			self.data[i] = True
			self.tkvars[i] = tk.BooleanVar(value=True)

		self.data[ANCART_OVERRIDE]=False

		self.data[SUPPORT] = support
		self.data[RESISTENCE] = resistence

		#default values.
		self.tkvars[SELECTED].set(False)
		self.tkvars[RELOAD].set(False)
		#self.data[RELOAD_TIMES]=self.default_reload
		#Non String, Non Numeric Value

		#Set some default value
		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		self.tkvars[ENTRYPLAN].set(entry_plan)

		self.tkvars[MANAGEMENTPLAN].set(manage_plan)

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)

		# self.entry_plan_decoder(entry_plan,entry_type)
		# self.manage_plan_decoder(manage_plan)


	""" PASSSIVE ENTRY/EXIT OVER A PERIOD AMONT OF TIME """


	""" PASSIVE ENTRY/EXIT """

	def passive_initialization(self,side,target_shares,final_target=-1):


		if not self.passive_in_process:

			self.passive_position = side
			self.passive_action = ""
			self.passive_current_shares = self.data[CURRENT_SHARE] 
			
			#self.data[POSITION]

			if final_target ==-1:

				if (self.data[POSITION]==LONG and side ==BUY) or  (self.data[POSITION]==SHORT and side ==SELL):
					self.passive_target_shares = self.data[CURRENT_SHARE] + target_shares 

					self.passive_action = ADD
				else:
					self.passive_target_shares = self.data[CURRENT_SHARE] - target_shares  

					self.passive_action = MINUS
			#when no positions
			else: 

				self.passive_target_shares = final_target
				self.passive_action = ADD

				if final_target ==0:
					self.passive_action = MINUS
				
			

			log_print(self.symbol_name," passive order received, target shares:",target_shares,self.passive_target_shares)
			done = threading.Thread(target=self.passive_process,daemon=True)
			done.start()
		else:
			log_print("already passive in progress")


	def passive_orders(self):


		coefficient = 0.01

		k = self.symbol.get_bid()//100

		gap = (self.symbol.get_ask() -self.symbol.get_bid())
		midpoint = round((self.symbol.get_ask() +self.symbol.get_bid())/2,2)

		if k==0: k = 1

		if self.passive_position == BUY :

			price = self.symbol.get_bid()
			
			#log_print(price,"last price",self.passive_price)
			if price >= self.passive_price+0.01*k or self.passive_price==0:

				#step 1, cancel existing orders
				self.ppro_out.send([CANCEL,self.symbol_name])
				#step 2, placing around current.
				time.sleep(0.2)

				if price<=10:
					self.ppro_out.send([PASSIVEBUY,self.symbol_name,self.passive_remaining_shares,price])
				else:

					if self.passive_remaining_shares<=4:
						self.ppro_out.send([PASSIVEBUY,self.symbol_name,self.passive_remaining_shares,price])
					else:

						# share = self.passive_remaining_shares//3
						# sharer = self.passive_remaining_shares- 2*share

						share = self.passive_remaining_shares//2
						remaning = self.passive_remaining_shares-share
						#self.ppro_out.send([PASSIVEBUY,self.symbol_name,share,price])

						# when big gap, one order on bid, one order on midpoint. 
						if gap>=0.05:
							self.ppro_out.send([PASSIVEBUY,self.symbol_name, remaning,price])
							self.ppro_out.send([PASSIVEBUY,self.symbol_name,share,midpoint])
							#price-0.01*k
						# when tight spread. just one on bid. 
						elif gap<=0.01:
							self.ppro_out.send([PASSIVEBUY,self.symbol_name,self.passive_remaining_shares,price])
						else:
							self.ppro_out.send([PASSIVEBUY,self.symbol_name, remaning,price])
							self.ppro_out.send([PASSIVEBUY,self.symbol_name,share,round(price+0.01,2)])

						#self.ppro_out.send([PASSIVEBUY,self.symbol_name,sharer,price-0.01*2*k])

			self.passive_price = price			
		elif self.passive_position == SELL:

			price = self.symbol.get_ask()

			#log_print(price,"last price",self.passive_price)
			if price <= self.passive_price -0.01*k or self.passive_price==0:

				#step 1, cancel existing orders
				self.ppro_out.send([CANCEL,self.symbol_name])
				#step 2, placing around current.
				time.sleep(0.2)


				if price<=10:
					self.ppro_out.send([PASSIVESELL,self.symbol_name,self.passive_remaining_shares,price])
				else:

					if self.passive_remaining_shares<=4:
						self.ppro_out.send([PASSIVESELL,self.symbol_name,self.passive_remaining_shares,price])
					else:

						share = self.passive_remaining_shares//2
						remaning = self.passive_remaining_shares-share

						if gap>=0.05:
							self.ppro_out.send([PASSIVESELL,self.symbol_name, remaning,price])
							self.ppro_out.send([PASSIVESELL,self.symbol_name,share,midpoint])
							#price-0.01*k
						# when tight spread. just one on bid. 
						elif gap<=0.01:
							self.ppro_out.send([PASSIVESELL,self.symbol_name,self.passive_remaining_shares,price])
						else:
							self.ppro_out.send([PASSIVESELL,self.symbol_name, remaning,price])
							self.ppro_out.send([PASSIVESELL,self.symbol_name,share,round(price-0.01,2)])


			self.passive_price = price
	#if the price is 2C away. chase it.
	#if the price is unchanged, do nothing. 



	def remaining_room(self):

		#check the remaining risk room. 
		#set the share number. 

		risk_per_share = abs(self.symbol.get_bid() - self.data[STOP_LEVEL])		


		remaining_risk = self.data[ESTRISK] - self.data[ACTRISK]


		share = remaining_risk/risk_per_share

		if share >=1:
			return int(share)

		elif share>0.5:
			return 1
		else:
			return 0
		
	def passive_process(self):

		fullfilled = 0
		timecount = 0

		price = 0

		while timecount<120:

			#update current.

			#what's in stock
			#log_print(self.symbol_name," Remaining:",self.passive_remaining_shares)

			self.passive_current_shares = self.data[CURRENT_SHARE] 

			#what just gained. 

			### need to recalculate. ####
			self.passive_remaining_shares = self.remaining_room()

			#print("shares left:",self.passive_remaining_shares)
			#abs(self.passive_target_shares - self.passive_current_shares)


			if self.passive_action==ADD and self.passive_remaining_shares<1:#self.data[CURRENT_SHARE] >= self.passive_target_shares:
				log_print(self.symbol_name," passive fill completed")
				break
			if self.passive_action==MINUS and self.passive_remaining_shares<1:#self.data[CURRENT_SHARE] <= self.passive_target_shares:
				log_print(self.symbol_name," passive fill completed")
				break
			if self.flatten_order==True:
				break

			self.passive_orders()
				
			#ORDER SENDING MOUDULE. 

			wait =random.randrange(5,11)
			time.sleep(wait)
			timecount+=wait


		#clean. 
		
		self.passive_position = ""
		self.passive_current_shares = 0
		self.passive_init_shares = 0
		self.passive_remaining_shares = 0
		self.passive_in_process = False
		self.passive_price = 0



	def ppro_update_price(self,symbol="",bid=0,ask=0,ts=0):

		#if bid!=self.symbol.get_bid() or ask!=self.symbol.get_ask():

			#move this to symbol
			#self.symbol.update_price(bid,ask,ts,self.tkvars[AUTORANGE].get(),self.tkvars[STATUS].get())

			#check stop. 

		#print("check_pnl",bid,ask,ts)
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
			gain = round((price-self.data[AVERAGE_PRICE]),4)

			#gap = abs(self.data[BREAKPRICE]-self.data[STOP_LEVEL])*0.05
			# if price < self.data[BREAKPRICE]:#-gap:
			# 	stillbreak = False

			if price <= self.data[STOP_LEVEL]:
				flatten=True

		elif self.data[POSITION]==SHORT:
			price = ask
			gain = round(self.data[AVERAGE_PRICE]-price,4)

			#gap = abs(self.data[STOP_LEVEL]-self.data[BREAKPRICE])*0.05


			# if price > self.data[BREAKPRICE]:#+gap:
			# 	stillbreak = False

			if price >=  self.data[STOP_LEVEL]:
				flatten=True
				print("flatening,",price,self.data[STOP_LEVEL])

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

			log_print(self.name,"flattening")

			if self.data[POSITION]==LONG:
				self.symbol.new_request(self.name,-self.data[CURRENT_SHARE])
			elif self.data[POSITION]==SHORT:
				self.symbol.new_request(self.name,self.data[CURRENT_SHARE])
			

			#self.ppro_out.send(["Flatten",self.symbol_name])

			#self.symbol.

		self.update_displays()

	def ppro_process_orders(self,price,shares,side,symbol):
		
		log_print("TP processing:",self.symbol_name,price,shares,side)
		if self.data[POSITION]=="": # 1. No position.
			if self.expect_orders==side: # or self.management_plan.strategy_name=="ScalpaTron":
				self.ppro_confirm_new_order(price,shares,side)
			else:
				log_print("TP processing: unexpected orders on",self.symbol_name)
		
		else:  # 2. Have position. 

			if self.data[POSITION]==side: #same side.
				self.ppro_orders_loadup(price,shares,side)
			else: #opposite
				self.ppro_orders_loadoff(price,shares,side)

		# if self.test_mode:
		# 	log_print("TP processing:",self.data)
		self.update_displays()

	def ppro_confirm_new_order(self,price,shares,side):

		"""set the state as running, then load up"""

		log_print(self.symbol_name,"New order confirmed:",price,shares,side)
		self.mark_algo_status(RUNNING)
		self.data[POSITION]=side
		self.tkvars[POSITION].set(side)
		self.data[REALIZED] = 0
		self.data[FLATTENTIMER]=0
		self.flatten_order = False
		self.ppro_orders_loadup(price,shares,side)

	def ppro_orders_loadup(self,price,shares,side):

		current = self.data[CURRENT_SHARE]

		#self.symbol.load_confirmation(self.name,shares)

		self.data[CURRENT_SHARE] = self.data[CURRENT_SHARE] + shares

		if current ==0 or self.data[CURRENT_SHARE]==0:
			self.data[AVERAGE_PRICE] = round(price,3)
		else:
			self.data[AVERAGE_PRICE]= round(((self.data[AVERAGE_PRICE]*current)+(price*shares))/self.data[CURRENT_SHARE],3)

		for i in range(shares):
			self.holdings.append(price)

		self.adjusting_risk()

		if self.data[AVERAGE_PRICE]!=self.data[LAST_AVERAGE_PRICE]:
			self.management_plan.on_loading_up()
			
			log_print(self.symbol_name," ",side,",",self.data[AVERAGE_PRICE]," at ",self.data[CURRENT_SHARE],"act risk:",self.data[ACTRISK])

		self.data[LAST_AVERAGE_PRICE] = self.data[AVERAGE_PRICE]

	def ppro_orders_loadoff(self,price,shares,side):

		current = self.data[CURRENT_SHARE]

		self.data[CURRENT_SHARE] = current-shares	
		
		gain = 0

		if self.data[POSITION] == LONG:
			for i in range(shares):
				try:
					gain += price-self.holdings.pop()
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")
		elif self.data[POSITION] == SHORT:
			for i in range(shares):
				try:
					gain += self.holdings.pop() - price	
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")	

		self.data[REALIZED]+=gain
		self.data[REALIZED]= round(self.data[REALIZED],2)

		self.adjusting_risk()

		#log_print(self.symbol_name," sold:",shares," current shares:",self.data[CURRENT_SHARE],"realized:",self.data[REALIZED])

		#finish a trade if current share is 0.

		if self.data[CURRENT_SHARE] <= 0:


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

		self.mark_algo_status(DONE)
		self.set_mind("Trade completed.",VERYLIGHTGREEN)
		self.data[POSITION] = ""

		self.tkvars[POSITION].set("")

		#self.tklabels[AUTORANGE]["state"] = "normal"
		self.current_price_level = 0
		self.current_running_strategy = None

		#if reload is on, revert it back to entry stage. 
		if self.tkvars[RELOAD].get() == True:
			log_print("TP processing:",self.symbol_name,":"," Reload activated. Trading triggers re-initialized. reload remaining:",self.data[RELOAD_TIMES])
			self.tkvars[RELOAD].set(False)
			self.start_tradingplan()


	def rejection_handling(self):


		### if have position, ignore. ###


		### if no position, flatten. ###


		if self.data[STATUS] == DEPLOYED:

			# cancel whatever requested on symbol.

			# withdraw the algo. 

			# show rejection. 

			self.symbol.cancel_all_request(self.name)
			self.mark_algo_status(REJECTED)

		else:

			log_print("rejection messge received on ",self.name)

	# def ppro_order_rejection(self):

	# 	self.mark_algo_status(REJECTED)


	""" Trade management """

	def manage_trades(self,side,action,percentage,passive):

		process = False
		if side!=None:
			if self.data[POSITION] == side:
				process = True
		else:
			process = True

		if self.data[CURRENT_SHARE]>0 and process:
			shares = int(self.data[CURRENT_SHARE]*percentage)
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

	def flatten_cmd(self):
		
		if self.tkvars[STATUS].get()==PENDING:
			self.cancel_algo()
		else:
			# self.ppro_out.send(["Flatten",self.symbol_name])


			if self.data[POSITION]==LONG:
				self.symbol.new_request(self.name,-self.data[CURRENT_SHARE])
			elif self.data[POSITION]==SHORT:
				self.symbol.new_request(self.name,self.data[CURRENT_SHARE])
			

	"""	UI related  """
	def update_symbol_tkvar(self):
		#print("updatem",elf.symbol.get_support(),elf.symbol.get_resistence())
		self.tkvars[SUPPORT].set(self.symbol.get_support())
		self.tkvars[RESISTENCE].set(self.symbol.get_resistence())

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

		self.cancel_all_request(self.name)
		if self.tkvars[STATUS].get()==PENDING:
			self.mark_algo_status(CANCELED)

	def cancle_deployment(self):
		if self.data[POSITION] =="" and self.data[CURRENT_SHARE]==0:
			self.mark_algo_status(PENDING)
			self.stop_tradingplan()
		else:
			log_print("cannot cancel, holding positions.")

	def deploy(self,risktimer=0):

		if self.tkvars[STATUS].get() ==PENDING:

#			try:

			#self.ppro_out.send([REGISTER,self.symbol_name])

			self.symbol.register_tradingplan(self.name,self)

			entryplan=self.tkvars[ENTRYPLAN].get()

			entrytimer=int(self.tkvars[TIMER].get())
			manage_plan =self.tkvars[MANAGEMENTPLAN].get()

			if risktimer ==0:
				self.data[RISKTIMER] = int(self.tkvars[RISKTIMER].get())
			else:
				self.data[RISKTIMER] = risktimer

			self.data[RISK_PER_SHARE] = abs(self.symbol.get_resistence()-self.symbol.get_support())

			self.set_mind("",DEFAULT)
			self.entry_plan_decoder(entryplan, entrytimer)
			self.manage_plan_decoder(manage_plan)

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

		self.entry_plan.on_deploying()
		self.management_plan.on_deploying()
		self.current_running_strategy = self.entry_plan

		# if self.tkvars[RELOAD].get()==False:
		# 	#print("h",self.data[RELOAD_TIMES] )
		# 	if self.data[RELOAD_TIMES] >0:
		# 		self.tkvars[RELOAD].set(True)
		# 		self.data[RELOAD_TIMES] -= 1
		# 		if self.data[RELOAD_TIMES]== 0:
		# 			log_print(self.symbol_name," no more reload.")


	def stop_tradingplan(self):
		self.current_running_strategy = None

	""" Plan Handler """	
	def entry_plan_decoder(self,entry_plan,entrytimer):

		instant = 1 


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
		elif manage_plan == THREE_TARGETS:
			self.set_ManagementStrategy(ThreePriceTargets(self.symbol,self))
		elif manage_plan == SMARTTRAIL:
			self.set_ManagementStrategy(SmartTrail(self.symbol,self))

		elif manage_plan == ANCARTMETHOD:
			self.set_ManagementStrategy(AncartMethod(self.symbol,self))

		elif manage_plan == ONETOTWORISKREWARD:
			self.set_ManagementStrategy(OneToTWORiskReward(self.symbol,self))

		elif manage_plan == ONETOTWOWIDE:
			self.set_ManagementStrategy(OneToTwoWideStop(self.symbol,self))

		elif manage_plan == ONETOTWORISKREWARDOLD:
			self.set_ManagementStrategy(OneToTWORiskReward_OLD(self.symbol,self))
		elif manage_plan == FIBO:
			self.set_ManagementStrategy(FibonacciOnly(self.symbol,self))

		elif manage_plan == FIBONO:
			self.set_ManagementStrategy(FiboNoSoft(self.symbol,self))
			
		elif manage_plan == EM_STRATEGY:

			### NEED TO MAKE SURE IT IS WHAT IT IS. otherwise, switch. 

			valid = True
			#check if it's 0
			#check if rrr exceed 1.5.
			em = self.symbol.stats['expected_momentum']
			if em==0:
				valid = False
			sup= self.symbol.get_support()
			res= self.symbol.get_resistence()

			l = round(res-sup,2)
			rrr = round(em/l,2) 

			if rrr<1.5:
				valid = False

			if valid:
				log_print(self.symbol_name,"EM:",em,"SUP:",sup,"RES:",res,"RPS:",l,"RRR:",rrr)
				self.set_ManagementStrategy(ExpectedMomentum(self.symbol,self))
			else:
				log_print(self.symbol_name,"EM:",em,"SUP:",sup,"RES:",res,"RPS:",l,"RRR:",rrr, "RRR to low, using Fib instd.")
				self.tkvars[MANAGEMENTPLAN].set(FIBO)
				self.set_ManagementStrategy(FibonacciOnly(self.symbol,self))
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
			self.entry_strategy_done()
			# done = threading.Thread(target=self.entry_strategy_done, daemon=True)
			# done.start()
		elif plan==self.management_plan:
			self.management_strategy_done()
			log_print(self.symbol_name,"management strategy completed.")
		else:
			log_print("Trading Plan: UNKONW CALL FROM Strategy",plan)

	def entry_strategy_done(self):

		self.management_plan.on_start()
		self.current_running_strategy = self.management_plan

	def management_strategy_done(self):

		pass


# if __name__ == '__main__':

# 	#TEST CASES for trigger.
# 	root = tk.Tk() 
# 	aapl = Symbol("aapl")
# 	TP = TradingPlan(aapl)
# 	aapl.set_tradingplan(TP)
# 	aapl.set_phigh(16)
# 	aapl.set_plow(15)

# 	b = BreakUp(0,False,aapl,TP)
# 	#b = BreakUp(0)
# 	TP.set_EntryStrategy(b)
# 	TP.start_EntryStrategy()

	
# 	aapl.update_price(10,10,0)
# 	aapl.update_price(11,11,1)
# 	aapl.update_price(12,12,2)
# 	aapl.update_price(13,13,3)
# 	aapl.update_price(14,14,4)
# 	aapl.update_price(15,15,5)
# 	##### DECRESE#######
# 	aapl.update_price(5,5,6)
# 	aapl.update_price(13,13,7)

# 	aapl.update_price(10,10,8)
# 	###### INCREASE #############
# 	aapl.update_price(11,11,9)
# 	aapl.update_price(12,12,10)
# 	aapl.update_price(13,13,11)
# 	aapl.update_price(14,14,12)
# 	aapl.update_price(15,15,13)
# 	aapl.update_price(16,16,14)
# 	aapl.update_price(17,17,15)
# 	aapl.update_price(18,18,16)
# 	aapl.update_price(19,19,17)


# 	root.mainloop()
