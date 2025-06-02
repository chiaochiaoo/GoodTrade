from constant import *
import tkinter as tk
#from Triggers import *
from Util_functions import *
from datetime import datetime, timedelta
import threading
import requests



def sign_test(a,b):

	return not ((a+b == abs(a)+abs(b)) or (a+b == -(abs(a)+abs(b))))


### I NEED TO TRACK HOW MANY SYMBOLS IT IS RUNNING SIMULTANEOUSLY. ###

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

PRICE = "Price"



DEBUG_MODE = False 
class Symbol:

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.

	"""
	"""
	def __init__(self,manager,symbol,pproout):

		self.source = "Symbol: "
		self.symbol_name = symbol
		self.manager = manager 

		self.ppro_out = pproout

		# make sure only 1 process goes.
		self.fill_lock =  threading.Lock()
		self.inspection_lock = threading.Lock()

		self.banned = False 

		self.numeric_labels = [TRADE_TIMESTAMP,TIMESTAMP,PRICE,BID,ASK,'SPREAD',RESISTENCE,SUPPORT,OPEN,HIGH,LOW,PREMARKETLOW,STOP,EXIT,ENTRY,CUSTOM]
		self.tech_indicators = [EMACOUNT,EMA8H,EMA8L,EMA8C,EMA5H,EMA5L,EMA5C,EMA21H,EMA21L,EMA21C,CLOSE]

		self.data = {}
		self.tkvars = {}

		self.sent_orders = False
		self.aggresive_only = False 
		self.holding_update = False 

		self.previous_sync_share = 0

		self.inspection_timestamp = 0

		self.last_order_timestamp = 0

		self.enabled_insepction = True 

		self.last_l1_update = 0

		self.have_pending_orders = False 

		self.bid_change = False 
		self.ask_change = False

		self.fill_timer = 30
		# self.symbol_dead_line = 959 

		# if ".PA" in self.symbol_name:
		# 	self.symbol_inspection
		"""
		UPGRADED PARTS

		"""

		self.previous_shares = 0
		self.previous_avgprice = 0

		self.active_tps = 0
		self.current_shares = 0
		self.current_expired =0
		self.theoritical_shares = 0

		self.tp_current_shares = 0 
		self.tp_total_current_shares = 0
		self.current_avgprice = 0
		self.total_expected = 0


		self.regulating_shares = 0
		self.rejections = []

		"""


		"""
		self.expected = 0
		self.difference = 0
		self.request = 0


		self.tp_difference = 0



		self.distributional_shares = 0
		self.distributional_shares_prices = 0
		self.distributional_remaining_shares = 0 

		self.regulating_phase = False 


		self.rejection_counts = 0
		### INSPECTION VARIABLES

		self.inspection_complete = False 
		self.tp_homeo = True 
		self.symbol_homeo = True 

		self.action=""

		self.market_out = 0

		self.current_imbalance = 0

		self.fill_time_remianing = 0

		self.sms_ts = 0

		# plus, minus, all the updates, all go here. 
		# 1. on adding shares
		# 2. on fullfilling. 
		self.incoming_shares_lock = threading.Lock()
		self.incoming_shares = {}

		self.order_processing_timer = 0

		#self.tradingplan_lock = threading.Lock()
		self.tradingplans = {}


		self.poly_bid =0
		self.poly_ask = 0

		self.init_data()

		log_print(self.source,self.symbol_name," New symbol system init")
		


	##### DATA PART #####


	def init_data(self):

		for i in self.numeric_labels:
			self.data[i] = 0
			
		for i in self.tech_indicators:
			self.data[i] = 0

	def update_price(self,price,bid,ask,ts):

		self.data[PRICE] = price

		self.data[TIMESTAMP] = ts

		#self.data['SPREAD'] = ask-bid 
		
		# if self.data[BID]!=bid:
		# 	self.bid_change = True 
		# else:
		# 	self.bid_change = False 

		# if self.data[ASK]!=ask:
		# 	self.ask_change = True 
		# else:
		# 	self.ask_change = False 

		self.poly_ask = ask
		self.poly_bid = bid

	def get_ts(self):
		now = datetime.now()
		timestamp = now.hour*3600 + now.minute*60 + now.second

		return timestamp
	def l1_update_module(self):

		pass 

		### tell the system if there is any bid ask changes since last time.

		try:
			postbody = "http://127.0.0.1:8080/GetLv1?symbol=" + self.symbol_name 

			r= requests.get(postbody)

			stream_data = r.text

			bid = float(find_between(stream_data, "BidPrice=\"", "\""))
			ask = float(find_between(stream_data, "AskPrice=\"", "\""))
			ts = find_between(stream_data, "MarketTime=\"", "\"")


			if self.data[BID]!=bid:
				self.bid_change = True 
			else:
				self.bid_change = False 


			if self.data[ASK]!=ask:
				self.ask_change = True 
			else:
				self.ask_change = False 

			self.data[ASK] = ask
			self.data[BID] = bid

			self.data['SPREAD'] = round(ask-bid,2)
			self.data[TIMESTAMP] = ts

			log_print(self.symbol_name,"SPREAD:",self.data['SPREAD'],self.data[BID],self.bid_change,self.data[ASK],self.ask_change)

			return 
		except Exception as e:

			PrintException(self.symbol_name,"Init L1 Update")

			self.ask_change = True 
			self.bid_change = True 

	def get_price(self):
		return self.data[PRICE]

	def get_poly_bid(self):
		return self.poly_bid

	def get_poly_ask(self):
		return self.poly_ask
	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]

	def instant_inspection(self):

		self.just_had_instant_inspection= True 
		self.symbol_inspection()


	### INSPECTION MOUDULE ###
	def symbol_inspection(self):

		"""
		If an order is placed. return 1, else then 0.
		"""

		if not self.inspection_lock.locked():

			with self.inspection_lock:

				tps = list(self.tradingplans.keys())


				#####   DISTRIBUTION PHASE   #####

				now = datetime.now()
				ts = now.hour*3600 + now.minute*60+ now.second

				self.inspection_timestamp = ts

				self.inspection_complete = False 

				self.orders_checking_phase()

				if self.distributional_shares!=0:
					self.distribution_phase(tps)

				self.status_checking_phase(tps)

				if self.inspection_complete==True:
					self.market_out = 0
					self.pair_off(tps)

					return 0 

				self.request = 0
				
				if self.ppro_homeo!=True:
					self.regulating_check_phase(tps)
				else:
					self.aggregating_phase(tps)

				if self.request!=0 and self.manager.open_order_check==True and ts<=57540:
					return self.ordering_phase()

				#####   AGGRAGATING PHASE   #####


			return 0
				#####   ORDERING PHASE   #####
		else:
			log_print(self.symbol_name,"Inspection LOCKED")
			return 0 


	def orders_checking_phase(self):

		"""
		OUTPUT THE TRUE self.diff. and avg prices. 
		"""

		incoming_shares,avg_price = self.incoming_shares_calculate()  #shares received.

		self.current_avgprice,self.current_shares = self.manager.get_position(self.symbol_name)   #current shares 
		self.difference = self.current_shares - self.previous_shares

		if self.difference!=incoming_shares:

			if abs(self.difference)>abs(incoming_shares):
				log_print(self.source,self.symbol_name," DISCREPANCY : Missing OSTATS :", self.difference," incoming orders",incoming_shares, "Proceed")
			else:
				log_print(self.source,self.symbol_name," DISCREPANCY : More Fills but PPro update deplay :", self.difference," incoming orders",incoming_shares, " wait 0.1")

				"""
				Note: here i can impment a immediate managerial update. 
				"""
				time.sleep(1)
				self.current_avgprice,self.current_shares = self.manager.get_position(self.symbol_name)
				self.difference = self.current_shares - self.previous_shares
				incoming_shares,avg_price = self.incoming_shares_calculate()		

		if self.difference!=incoming_shares:
			log_print(self.source,self.symbol_name," DISCREPANCY : PPRO POSITION and OSTATS NOT MATCHING. PROCEED.")			


		with self.incoming_shares_lock:
			self.incoming_shares = {}

		self.distributional_shares = self.difference
		self.distributional_shares_prices = avg_price

		self.previous_shares = self.current_shares


		# check tp homeo.

		if DEBUG_MODE:
			log_print(self.source,self.symbol_name, "Debugging order checking", " Current ",self.current_shares, "Incoming ",self.distributional_shares)

	def distribution_phase(self,tps):


		"""
		INPUT: distributional

		>>> PAIRING? <<<
		OUTPUT: orders
		"""

		if self.distributional_shares!=0:

			## check if this is the regulating shares needned. 

			total_tp = list(self.tradingplans.keys())

			now = datetime.now()
			ts = now.hour*3600 + now.minute*60+ now.second


			tps_ = {}

			for tp in total_tp:
				if self.tradingplans[tp].get_inspectable():
					request_time = ts-self.tradingplans[tp].get_request_time(self.symbol_name)
					tps_[tp] =request_time

			for tp in total_tp: #EVERYTHING ELSE.
				if tp not in tps_:
					request_time = ts-self.tradingplans[tp].get_request_time(self.symbol_name)
					tps_[tp] =request_time

			sorted_dict = dict(sorted(tps_.items(), reverse=True))
			tps_ = list(sorted_dict.keys())

			for tp in tps_:

				log_print(self.source,self.symbol_name,"checking ",tp, self.tradingplans[tp].get_current_request(self.symbol_name))
				self.distributional_shares = self.tradingplans[tp].request_fufill(self.symbol_name,self.distributional_shares,self.distributional_shares_prices	)

				self.tradingplans[tp].notify_holding_change(self.symbol_name)
				if self.distributional_shares ==0:
					break

			## if there is any non-distributed shares left ##

			if self.distributional_shares!=0:
				log_print(self.source,self.symbol_name," unable to distribute all shares:",self.distributional_shares)


			self.distributional_remaining_shares	= self.distributional_shares

	def status_checking_phase(self,tps):

		self.tp_current_shares,self.expired,self.tp_total_current_shares = self.get_all_current(tps)

		self.expected = self.get_all_expected(tps)

		self.tp_difference = self.expected - self.tp_current_shares 


		if self.tp_difference==0:
			self.tp_homeo = True
		else:
			self.tp_homeo = False  

		if self.current_shares==self.tp_total_current_shares:
			self.ppro_homeo = True 
		else:
			self.ppro_homeo = False 

		if self.tp_difference==0 and self.tp_homeo==True and self.ppro_homeo==True:
			self.inspection_complete = True 

		log_print(self.source,self.symbol_name,f"Shares change {self.tp_difference} TP: {self.tp_total_current_shares,self.tp_current_shares} PPRO {self.current_shares} Expect: {self.expected} Tp balance: {self.tp_homeo} Ppro balance: {self.ppro_homeo}  Inspection Complete {self.inspection_complete}")

	def regulating_check_phase(self,tps):

		"""
		Must ensure self.current_shares = self.tp. 
		if not then do not continue. 

		this will only go through if self.tp == True. 
		there could be share differences. 
		"""
		proceed = True 
		if self.ppro_homeo!=True:


			if proceed:
				self.request = self.tp_total_current_shares-self.current_shares
				self.regulating_shares =self.request


				if self.regulating_shares == self.distributional_shares:
					log_print(self.source,self.symbol_name," returning normal.")
					self.regulating_shares = 0 
					self.distributional_shares = 0 


				log_print(self.source,self.symbol_name," Discrepancy on Symbol. Adjusting shares first.",self.regulating_shares)


				if DEBUG_MODE:
					log_print(self.source,self.symbol_name, "regulating phase:",self.regulating_shares)

	def pairing_phase(self):

		"""

		"""
		pass 

	def aggregating_phase(self,tps):

		"""
		find out how many orders need to go out.

		STEP 1, CHECK IF PPRO==TP.CUR , if not ,adjust that first.

		STEP 2. SEND OUT MISSING SHARES. 
		"""

		self.tp_current_shares,self.expired,self.tp_total_current_shares = self.get_all_current(tps)
		self.expected = self.get_all_expected(tps)
		self.request =  self.expected - self.tp_current_shares

		#if DEBUG_MODE:
		log_print(self.source,self.symbol_name, "have",self.tp_current_shares," want",self.expired," request",self.request)


	def ordering_phase(self):

		# I NEED TO ADD A MECHANISM ON THIS
		# If passive orders still don't full fill the request everything within some minutes
		# Cancel all the requests. (or market in )

		# ALL ORDERS AT ONCE. # First clear previous order. 
		# if there might be already an order: #


		"""
		Only deploy orders when both ----> 
		1. There is a request
		2. L1 has moved.
		3. 
		"""

		self.recent_rejection_check()

		if self.rejection_counts>=2:
			log_print(self.source,self.symbol_name," too much recent rejection detected. wait 1.")
			return 0

		if self.market_out!=0:
			self.market_out = 0
			log_print(self.source,self.symbol_name, " just marked out. wait 1")
			return 0

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if self.request>0:
			self.action = PASSIVEBUY
		else:
			self.action = PASSIVESELL

		self.l1_update_module()

		skip = True 

		if self.aggresive_only!=True and ts<57500:
			if self.action==PASSIVEBUY and (self.bid_change==True or self.data['SPREAD']>0.05):
				self.ppro_out.send([CANCEL,self.symbol_name]) # only cancel previous order!
				skip = False 
			elif self.action==PASSIVESELL and (self.ask_change==True or self.data['SPREAD']>0.05):
				self.ppro_out.send([CANCEL,self.symbol_name]) # only cancel previous order!
				skip = False 

		if self.sent_orders==False:
			skip = False 

		time.sleep(0.1)

		## self.fill_time_remianing
		log_print(self.source,self.symbol_name,self.action,self.request,self.fill_timer,"fill timer:",self.fill_time_remianing)

		if self.request!=0 : #and self.holding_update==False 

			total = abs(self.request-self.expired)
			if total>=500:
				total = 500
				log_print(self.source,self.symbol_name,self.action," adjusted to 500 instead of",self.request)

			if self.expired!=0:
				self.ppro_out.send([CANCEL,self.symbol_name]) 
				time.sleep(0.1)
				self.immediate_request(self.expired)
			if self.aggresive_only==True or ts>57500: ### LAST 100 seconds market only.
				self.immediate_request(self.request)
				self.sent_orders = True 
			else:
				if not skip and total!=0:

					###### ADJUST THE spread
					adjustment = 0 

					if self.data['SPREAD']>0.01:
						adjustment = round((self.fill_time_remianing)*self.data['SPREAD'],2) # % of spread.

						if adjustment <0.01:
							adjustment = 0.01 

					if self.action==PASSIVESELL:
						adjustment = adjustment*-1
						
					log_print(self.source,self.symbol_name,"orders:","fill timer:",self.fill_time_remianing," fill time limit",self.fill_timer,"spread:",self.data['SPREAD'],"adjustment:",adjustment)

					self.ppro_out.send([self.action,self.symbol_name,total,adjustment,self.manager.gateway])
					self.sent_orders = True 


			return 1
				# else:
				# 	log_print(self.source,self.symbol_name,"NO CHANGE DETECTED, skipping.")

		# handl = threading.Thread(target=self.threading_order,daemon=True)
		# handl.start()

		return 0
	#######################################


	### TP DATA PART ###

	def get_all_current(self,tps):

		current_shares = 0
		total_current_shares = 0
		expired =0
		now = datetime.now()

		ts = now.hour*3600 + now.minute*60 + now.second


		# if within 5 cents. below 1 $. 

		### depending on the spread. 

		if self.data['SPREAD']>0.1:
			self.fill_timer = 60 

		if self.data['SPREAD']<0.05:
			self.fill_timer = 30 

		if self.data['SPREAD']<0.03:
			self.fill_timer = 20

		if now.hour*60+now.minute<575 or now.hour*60+now.minute>950:
			self.fill_timer = 10


		#self.fill_time_remianing = min(round((ts-self.tradingplans[tp].get_request_time(self.symbol_name))/self.fill_timer,2),1)

		cur_time = 0

		for tp in tps:
			if self.tradingplans[tp].get_inspectable():
				current_shares +=  self.tradingplans[tp].get_current_share(self.symbol_name)
				
				if self.tradingplans[tp].get_request_time(self.symbol_name)>cur_time:
					cur_time = self.tradingplans[tp].get_request_time(self.symbol_name)

				if ts-self.tradingplans[tp].get_request_time(self.symbol_name)>self.fill_timer:
					expired+=self.tradingplans[tp].get_current_request(self.symbol_name)

			total_current_shares += self.tradingplans[tp].get_current_share(self.symbol_name)
		self.fill_time_remianing = round((ts-cur_time)/self.fill_timer,2)

		self.fill_time_remianing = min(self.fill_time_remianing,1)


		return current_shares,expired,total_current_shares

	def get_all_expected(self,tps):

		"""
		Doesnt matter if the TP is running or not, having request or not. it runs through. 
		The less the parameter, the more generalizability 
		"""
		self.expected = 0
		
		for tp in tps:
			### ONLY IF TP is inspectable. 

			if self.tradingplans[tp].get_inspectable():
				self.expected +=  self.tradingplans[tp].get_current_expected(self.symbol_name)

		return self.expected

	def register_tradingplan(self,name,tradingplan):

		self.tradingplans[name] = tradingplan

	def get_all_future_remaining(self):

		remaining = 0

		tps = list(self.tradingplans.keys())

		for tp in tps:
			remaining+= self.tradingplans[tp].get_future_remaining(self.symbol_name)

		log_print(self.symbol_name,"would remain:",remaining)

		return remaining

	def get_all_moo_exit(self):

		### all tps have the name of IMB_MOO
		remaining = 0

		tps = list(self.tradingplans.keys())

		for tp in tps:
			if "IMB_MOO" in  self.tradingplans[tp].get_algoname():
				remaining+= self.tradingplans[tp].get_current_share(self.symbol_name)
			if "IMB_AM" in  self.tradingplans[tp].get_algoname():
				remaining+= self.tradingplans[tp].get_current_share(self.symbol_name)
			if "MO_" in  self.tradingplans[tp].get_algoname():
				remaining+= self.tradingplans[tp].get_current_share(self.symbol_name)

		log_print(self.symbol_name,"get all moo exit :current have:",remaining)

		return remaining

	def get_all_moo_enter(self):

		remaining = 0

		tps = list(self.tradingplans.keys())

		for tp in tps:
			if "OB" ==  self.tradingplans[tp].get_algoname()[:2]:
				remaining+= self.tradingplans[tp].get_current_expected(self.symbol_name)
			if "D2D" ==  self.tradingplans[tp].get_algoname()[:3]:
				remaining+= self.tradingplans[tp].get_current_expected(self.symbol_name)

			if "AW" ==self.tradingplans[tp].get_algoname()[:2]:
				remaining+= self.tradingplans[tp].get_current_expected(self.symbol_name)

			if "AP" ==self.tradingplans[tp].get_algoname()[:2]:
				remaining+= self.tradingplans[tp].get_current_expected(self.symbol_name)
				
		log_print(self.symbol_name,"get all moo enter: expect to have:",remaining)

		return remaining

	def as_is(self):

		# tell all register trading plan the state as is. 
		tps = list(self.tradingplans.keys())

		#### FOR THE TP TRYING TO START THE POSITION. IGNORE. 
		for tp in tps:
			if self.tradingplans[tp].having_request(self.symbol_name) and self.tradingplans[tp].get_holdings(self.symbol_name)!=0:
				self.tradingplans[tp].algo_as_is() 


	def check_all_incrementals(self,tps):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		for tp in tps:
			self.tradingplans[tp].check_incremental(self.symbol_name,ts)

	def get_difference(self):
		return self.difference

	def pair_off(self,tps):

		# if DEBUG_MODE:
		# 	print(self.source,self.symbol_name	," Pairing off check")
		want = []

		for tp in tps:
			if self.tradingplans[tp].get_inspectable():
				want.append(self.tradingplans[tp].get_current_request(self.symbol_name))

		p=0
		n=0
		for i in want:
			if i>0:
				p+=abs(i)
			else:
				n+=abs(i)
		long_pair_off = min(p,n)

		pairing_price = self.distributional_shares_prices

		if pairing_price==0:
			pairing_price = self.data[PRICE]

		if long_pair_off>0:	

			#log_print(self.source,self.symbol_name	,"pair off,",want," amount", long_pair_off,short_pair_off)

			short_pair_off = -long_pair_off
			# use this amount to off set some longs and shorts. 

			# if price is 0, use impcming

			for tp in tps: 
				if self.tradingplans[tp].get_inspectable():
					long_pair_off = self.tradingplans[tp].request_fufill(self.symbol_name,long_pair_off,pairing_price)
					if long_pair_off<=0:
						break

			for tp in tps: 
				if self.tradingplans[tp].get_inspectable():
					short_pair_off = self.tradingplans[tp].request_fufill(self.symbol_name,short_pair_off,pairing_price)
					if short_pair_off>=0:
						break

			log_print(self.source,self.symbol_name	,"pair off,",want," amount", long_pair_off,short_pair_off,pairing_price)

	def holdings_update(self,price,share):

		with self.incoming_shares_lock:

			if price not in self.incoming_shares:

				self.incoming_shares[price] = share
			else:
				self.incoming_shares[price] += share

			
		#log_print("holding update - releasing lock")
		#log_print("Symbol",self.symbol_name," holding update:",price,share)
		self.holding_update = True 

	def incoming_shares_calculate(self):


		## return the shares,avg price, and clear

		with self.incoming_shares_lock:

			total_shares = sum(self.incoming_shares.values())

			if total_shares == 0:
				avg_price = 0  # Avoid division by zero
			else:
				avg_price = sum(price * shares for price, shares in self.incoming_shares.items()) / total_shares

			#self.incoming_shares = {}


			return total_shares,avg_price

	
	def cancel_request(self):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if self.aggresive_only!=True and ts<57500:

			### NEED TO KNOW IF. HMM .
			self.ppro_out.send([CANCEL,self.symbol_name])	


	def threading_order(self):

			#lets add a bit of delay to it. 

		log_print(self.source,self.symbol_name,action,share)


		if self.difference!=0:
			self.ppro_out.send([self.action,self.symbol_name,abs(self.difference),0])

	def recent_rejection_check(self):
		now = datetime.now()
		timestamp = now.hour*60 + now.minute 
		
		self.rejection_counts =  sum(1 for num in self.rejections if num > timestamp-2)

	def rejection_message(self,side):

		now = datetime.now()
		timestamp = now.hour*60 + now.minute 

		## iterate through all the TPs request. check who is requesting. if it is not running withdraw and cancel it. 
		
		if side == "Long":
			coefficient = 1
		elif side =="Short":
			coefficient = -1

		tps = list(self.tradingplans.keys())

		#### FOR THE TP TRYING TO START THE POSITION. IGNORE.  
		for tp in tps:
			if self.tradingplans[tp].having_request(self.symbol_name) and self.tradingplans[tp].get_holdings(self.symbol_name)==0:
		 		self.tradingplans[tp].rejection_handling(self.symbol_name)

		####### BUT IF IT IS DISCREPANCY? ##### ADD IT TO THE TP.  OR IGNORE? ####

		self.rejections.append(timestamp)

		self.recent_rejection_check()

		log_print(self.source,self.symbol_name," rejection detected. total:",len(self.rejections)," last 2:", self.rejection_counts)

		if self.rejection_counts >=2:

			### all tp as is.
			tps = list(self.tradingplans.keys())

			#### FOR THE TP TRYING TO START THE POSITION. IGNORE. 
			log_print(self.source,self.symbol_name,'setting request tp as is')

			affected = []
			for tp in tps:
				if self.tradingplans[tp].having_request(self.symbol_name) and self.tradingplans[tp].get_holdings(self.symbol_name)!=0:
					self.tradingplans[tp].algo_as_is()
					affected.append(tp)

			if timestamp != self.sms_ts and self.rejection_counts >=3:

				self.manager.sms_alert(f'{self.symbol_name} \n Affected strategies: {str(affected)} \n Holdings: {str(self.current_shares)}')
				self.sms_ts = timestamp
			### discrepancy added. 



	def cancel_all(self):

		tps = list(self.tradingplans.keys())

		for tp in tps:
			self.tradingplans[tp].submit_expected_shares(self.symbol_name,0,0)

	def immediate_request(self,shares):

		# I may need to cancel existing order first. for a 0.1 second delay.

		if shares!=0:
			if shares<0:
				self.ppro_out.send([IOCSELL,self.symbol_name,abs(shares),self.get_bid()])
			else:
				self.ppro_out.send([IOCBUY,self.symbol_name,abs(shares),self.get_ask()])


			self.market_out = shares
			self.holding_update = True

	def ppro_flatten(self):
		self.ppro_out.send([FLATTEN,self.symbol_name])

	def turn_on_aggresive_only(self):
		self.aggresive_only = True 