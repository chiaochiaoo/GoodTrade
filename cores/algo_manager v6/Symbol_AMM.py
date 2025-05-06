from constant import *
import tkinter as tk
#from Triggers import *
from Util_functions import *
from datetime import datetime, timedelta
import threading
import requests
from Symbol import *



class Symbol_AMM(Symbol):

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.

	"""
	"""

	def __init__(self,manager,symbol,pproout):

		super().__init__(manager,symbol,pproout)

		self.source = "Symbol_AMM: "

		#self.standard_size = share_lot


		self.can_bid = True 
		self.can_ask = True 

		self.should_wait = False 


		self.upper_limit_lot = 10
		self.lower_limit_lot = -10
		self.upper_limit = 500
		self.lower_limit = -500

		self.standard_lot = 100

		self.upper_coefficient = 1   ### this is linear to
		self.lower_coefficient = 1   ### this is linear 

		self.interval = 5

		self.last_fill_ts = 0

		self.flatten_mode = False 

	def set_limits(self,upper_limit,lower_limit,interval):

		self.upper_limit_lot = upper_limit
		self.lower_limit_lot = lower_limit*-1
		self.interval = interval

	def update_standard_lot(self,standard_lot):
		self.standard_lot = standard_lot
		self.upper_limit = self.upper_limit_lot *standard_lot
		self.lower_limit = self.lower_limit_lot *standard_lot

	def register_tradingplan(self,name,tradingplan):

		self.tradingplan = tradingplan


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

	def holdings_update(self,price,share):

		with self.incoming_shares_lock:

			if price not in self.incoming_shares:

				self.incoming_shares[price] = share
			else:
				self.incoming_shares[price] += share

		self.holding_update = True 

		# self.tradingplan.notify_holding_change(self.symbol_name)
		# #log_print("holding update - releasing lock")
		log_print("Symbol AMM",self.symbol_name," holding update:",price,share)

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60+ now.second

		self.last_fill_ts = ts
		# self.holding_update = True 

		# hold_fill = threading.Thread(target=self.holdings_fill,daemon=True)
		# hold_fill.start()


	def holdings_fill(self):

		if not self.fill_lock.locked():
			with self.fill_lock:
				#first wait for few seconds. 
				time.sleep(0.1)

				while self.order_processing_timer>0:
					time.sleep(0.1)
					self.order_processing_timer	-=0.1




	def symbol_inspection(self):

		## check how many shares it has. is it under allowing.

		if not self.inspection_lock.locked():

			with self.inspection_lock:

				tps = list(self.tradingplans.keys())

				#####   DISTRIBUTION PHASE   #####
				now = datetime.now()
				ts = now.hour*3600 + now.minute*60+ now.second

				self.inspection_timestamp = ts

				self.inspection_complete = False 

				### Need to know one of the following states:
				### 1. No action
				### 2. Bid only
				### 3. Ask only
				### 4. Bid/Ask only

				self.orders_checking_phase()
				
				# hedging event. 
				self.tradingplan.submit_core_share(self.symbol_name,self.current_shares)


				if self.flatten_mode == True:
					self.flatten_phase()
					return 1 

				self.can_bid = True 
				self.can_ask = True 
				self.should_wait = False 

				if self.current_shares>=self.upper_limit:
					self.can_bid = False 

				if self.current_shares<=self.lower_limit:
					self.can_ask = False 

				if ts < self.last_fill_ts + self.interval:
					self.should_wait = True 

				### need to verfiy with tp if current hedging is working. 

				if self.tradingplan.get_homeo()!=True:
					self.should_wait = True 

				log_print(self.source, "Status:", "BIDDING",self.can_bid," ASKING",self.can_ask," current share",self.current_shares,self.upper_limit,self.lower_limit, ' pending:',self.should_wait,ts-self.last_fill_ts)
				

				if not self.should_wait:

					self.ordering_phase()
					return 1

				return 0


	def orders_checking_phase(self):

		"""
		OUTPUT THE TRUE self.diff. and avg prices. 
		"""

		incoming_shares,avg_price = self.incoming_shares_calculate()  #shares received.

		self.current_shares = self.manager.get_position(self.symbol_name)   #current shares 
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
				self.current_shares = self.manager.get_position(self.symbol_name)
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


	def flatten_phase(self):

		if self.current_shares!=0:
			if self.current_shares<0:
				self.action = PASSIVEBUY

				if self.bid_change==True:
					self.ppro_out.send([CANCEL,self.symbol_name]) # only cancel previous order!
					self.ppro_out.send([self.action,self.symbol_name,abs(self.current_shares),0,self.manager.gateway])

			else:
				self.action = PASSIVESELL

				if self.ask_change==True:
					self.ppro_out.send([CANCEL,self.symbol_name]) # only cancel previous order!
					self.ppro_out.send([self.action,self.symbol_name,abs(self.current_shares),0,self.manager.gateway])


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

		self.l1_update_module()

		skip= True 

		if (self.bid_change==True or self.ask_change==True) and ts<57500:
			self.ppro_out.send([CANCEL,self.symbol_name]) # only cancel previous order!
			skip = False 


		if not skip and self.can_bid and self.data[BID]!=0:
			self.ppro_out.send([PASSIVEBUY_L,self.symbol_name,self.standard_lot,round(self.data[BID],2),self.manager.gateway])
			self.ppro_out.send([PASSIVEBUY_L,self.symbol_name,self.standard_lot,round(self.data[BID]-0.01,2),self.manager.gateway])
		if not skip and self.can_ask and self.data[ASK]!=0:
			self.ppro_out.send([PASSIVESELL_L,self.symbol_name,self.standard_lot,round(self.data[ASK],2),self.manager.gateway])
			self.ppro_out.send([PASSIVESELL_L,self.symbol_name,self.standard_lot,round(self.data[ASK]+0.01,2),self.manager.gateway])

		if self.request>0:
			self.action = PASSIVEBUY
		else:
			self.action = PASSIVESELL


		# skip = True 

		# if self.aggresive_only!=True and ts<57500:
		# 	if self.action==PASSIVEBUY and (self.bid_change==True or self.data['SPREAD']>0.05):
		# 		self.ppro_out.send([CANCEL,self.symbol_name]) # only cancel previous order!
		# 		skip = False 
		# 	elif self.action==PASSIVESELL and (self.ask_change==True or self.data['SPREAD']>0.05):
		# 		self.ppro_out.send([CANCEL,self.symbol_name]) # only cancel previous order!
		# 		skip = False 

		# if self.sent_orders==False:
		# 	skip = False 

		# time.sleep(0.1)

		# ## self.fill_time_remianing
		# log_print(self.source,self.symbol_name,self.action,self.request,self.fill_timer,"fill timer:",self.fill_time_remianing)

		# if self.request!=0 : #and self.holding_update==False 

		# 	total = abs(self.request-self.expired)
		# 	if total>=500:
		# 		total = 500
		# 		log_print(self.source,self.symbol_name,self.action," adjusted to 500 instead of",self.request)

		# 	if self.expired!=0:
		# 		self.ppro_out.send([CANCEL,self.symbol_name]) 
		# 		time.sleep(0.1)
		# 		self.immediate_request(self.expired)
		# 	if self.aggresive_only==True or ts>57500: ### LAST 100 seconds market only.
		# 		self.immediate_request(self.request)
		# 		self.sent_orders = True 
		# 	else:
		# 		if not skip and total!=0:

		# 			###### ADJUST THE spread
		# 			adjustment = 0 

		# 			if self.data['SPREAD']>0.01:
		# 				adjustment = round((self.fill_time_remianing)*self.data['SPREAD'],2) # % of spread.

		# 				if adjustment <0.01:
		# 					adjustment = 0.01 

		# 			if self.action==PASSIVESELL:
		# 				adjustment = adjustment*-1
						
		# 			log_print(self.source,self.symbol_name,"orders:","fill timer:",self.fill_time_remianing," fill time limit",self.fill_timer,"spread:",self.data['SPREAD'],"adjustment:",adjustment)

		# 			self.ppro_out.send([self.action,self.symbol_name,total,adjustment,self.manager.gateway])
		# 			self.sent_orders = True 


		# 	return 1
		# 		# else:
		# 		# 	log_print(self.source,self.symbol_name,"NO CHANGE DETECTED, skipping.")

		# # handl = threading.Thread(target=self.threading_order,daemon=True)
		# # handl.start()

		# return 0