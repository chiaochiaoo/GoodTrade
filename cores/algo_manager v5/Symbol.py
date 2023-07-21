from constant import *
import tkinter as tk
#from Triggers import *
from Util_functions import *
from datetime import datetime, timedelta
import threading




def sign_test(a,b):

	return not ((a+b == abs(a)+abs(b)) or (a+b == -(abs(a)+abs(b))))


### I NEED TO TRACK HOW MANY SYMBOLS IT IS RUNNING SIMULTANEOUSLY. ###

class Symbol:

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.

	"""
	'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445
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

		self.numeric_labels = [TRADE_TIMESTAMP,TIMESTAMP,BID,ASK,RESISTENCE,SUPPORT,OPEN,HIGH,LOW,PREMARKETLOW,STOP,EXIT,ENTRY,CUSTOM]
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

		"""
		UPGRADED PARTS

		"""

		self.previous_shares = 0
		self.previous_avgprice = 0

		self.active_tps = 0
		self.current_shares = 0
		self.theoritical_shares = 0

		self.current_avgprice = 0
		self.total_expected = 0


		"""

		"""
		self.expected = 0
		self.difference = 0
		self.action=""

		self.market_out = 0

		self.current_imbalance = 0

		# plus, minus, all the updates, all go here. 
		# 1. on adding shares
		# 2. on fullfilling. 
		self.incoming_shares_lock = threading.Lock()
		self.incoming_shares = {}

		self.order_processing_timer = 0

		#self.tradingplan_lock = threading.Lock()
		self.tradingplans = {}

		self.init_data()
		
	def turn_on_aggresive_only(self):
		self.aggresive_only = True 

	def turn_off_insepction(self):
		self.enabled_insepction = False 


	def init_data(self):

		for i in self.numeric_labels:
			self.data[i] = 0
			
		for i in self.tech_indicators:
			self.data[i] = 0

	def register_tradingplan(self,name,tradingplan):

		self.tradingplans[name] = tradingplan

	def update_price(self,bid,ask,ts):

		#print("price",bid,ask,ts)
		if self.data[BID]!= bid and self.data[ASK]!=ask:

			self.data[BID] = bid
			self.data[ASK] = ask
			self.data[TIMESTAMP] = ts

	def instant_inspection(self):

		self.just_had_instant_inspection= True 
		self.symbol_inspection()

	def get_ts(self):
		now = datetime.now()
		timestamp = now.hour*3600 + now.minute*60 + now.second

		return timestamp

	def symbol_inspection(self):

		"""
		For both load and unload
		"""

		

		if not self.inspection_lock.locked():
			log_print(self.symbol_name,"Inspecting:")
			with self.inspection_lock:
				timestamp = self.get_ts()
				while (timestamp - self.last_order_timestamp<=2) or (timestamp -self.inspection_timestamp<=2):
					log_print(self.symbol_name,"inspection: inspection wait:",timestamp - self.last_order_timestamp,timestamp -self.inspection_timestamp)
					time.sleep(1)
					timestamp = self.get_ts()


				
				tps = list(self.tradingplans.keys())
				self.update_stockprices(tps)

				# CRITICAL SECTION. 
				with self.incoming_shares_lock:
					if self.get_bid()!=0:
						# no.2 pair off diff side. need.. hmm price .....!!!
						self.pair_off(tps)


					# no.3 pair orders. fill it in. 
					#self.calc_inspection_differences(tps)


					# no.4 get all current imbalance
					self.calc_total_imbalances(tps)

				now = datetime.now()
				ts = now.hour*3600 + now.minute*60 + now.second

				# Check again if there is any update. if there is, call it off. 


				if self.holding_update==False:
					if self.difference!=0 and ts<=57510:
						self.inspection_timestamp = timestamp
						self.deploy_orders()
						return 1

					else:
						self.action = ""
				else:
					log_print(self.symbol_name," holding change detected. skipping ordering. estimate difference:",self.difference)
					self.holding_update=False 

			return 0
		else:
			log_print(self.symbol_name,"Inspection LOCKED")
			return 0 


	def update_stockprices(self,tps):
		
		for tp in tps:
			self.tradingplans[tp].update_stockprices(self.symbol_name,self.get_bid())

	def as_is(self):

		pass 


	def calc_total_imbalances(self,tps):

		### STAGE 1. JUST UPDATE THE TPs. 
		self.current_avgprice,current_shares = self.manager.get_position(self.symbol_name)
		self.current_shares = self.get_all_current(tps)
		self.expected = self.get_all_expected(tps)
		self.difference = self.expected - self.current_shares


		### STAGE 2. ONLY if TPs are taken care off.

		### FOUR cases. 
		### 1. ppro indicate over fill and holdings not detected. -> potential MISSING orders notification. -> ppro_true then recalibrate. 
		### 2. holding detect there is a problem, but ppro side and tps are all ok. -> sync error? RESET if ppro_true. 
		### 3. ppro indicate over fill, and holdings also detect over fill, they match. -> update self.difference 
		###	4. 																They don't match.  -> wait for ppro_true then recalibrate. 
		### 

		ppro_true = False 
		if current_shares == self.previous_shares:
			ppro_true = True 
		self.previous_shares = current_shares

		recalibrate = False 
		shares_matched = False 

		if current_shares==self.current_shares:
			shares_matched = True 

		
		if self.difference!=0:
			log_print(self.source,self.symbol_name," inspection complete, expected",self.expected,\
				" have",self.current_shares,\
				" deploying:",self.difference,\
				"holding imbalance,",self.current_imbalance,\
				"ppro shares matchd:",shares_matched)


		if self.difference==0 and ppro_true: # i now know i can trust the ppro share is true.. ? NO!!!???/


			# IF THERE IS A PROBLEM. 
			if shares_matched!=True or self.current_imbalance!=0:

				log_print(self.source,self.symbol_name," inspection discrepancy:"," PPRO:",current_shares," TPs:",self.current_shares, " account imbalance:",self.current_imbalance)

				if shares_matched==True and self.current_imbalance!=0:
					self.current_imbalance = 0 
					log_print(self.source,self.symbol_name," inspection discrepancy: ppro matched but holding says imbalance. delusional? reset.")

				if shares_matched!=True: # I CAN SAFELY ASSUME THERE IS A PROBLEM. 

					#only 2 cases. matched, or not matched. 


					if self.current_imbalance == current_shares-self.current_shares:
						log_print(self.source,self.symbol_name," inspection discrepancy: discrepancy matched. ",self.current_imbalance,current_shares-self.current_shares)
						self.difference += self.current_imbalance * -1
					else:
						pass 
						### IF it's a actively manged, bypass this?    ###
						###                                            ###
						##################################################
						self.difference += (current_shares-self.current_shares) * -1
						log_print(self.source,self.symbol_name," inspection discrepancy: discrepancy UNMATCHED potential missing order fills. ",self.current_imbalance,current_shares-self.current_shares)
						self.current_imbalance = current_shares-self.current_shares


	def get_all_current(self,tps):

		current_shares = 0
		
		for tp in tps:
			current_shares +=  self.tradingplans[tp].get_current_share(self.symbol_name)

		return current_shares

	def get_all_expected(self,tps):

		"""
		Doesnt matter if the TP is running or not, having request or not. it runs through. 
		The less the parameter, the more generalizability 
		"""
		self.expected = 0
		
		for tp in tps:
			self.expected +=  self.tradingplans[tp].get_current_expected(self.symbol_name)

		return self.expected

	def get_difference(self):
		return self.difference

	def pair_off(self,tps):
		
		want = []

		for tp in tps:
			want.append(self.tradingplans[tp].get_current_request(self.symbol_name))

		p=0
		n=0
		for i in want:
			if i>0:
				p+=abs(i)
			else:
				n+=abs(i)
		long_pair_off = min(p,n)

		if long_pair_off>0:	

			#log_print(self.source,self.symbol_name	,"pair off,",want," amount", long_pair_off,short_pair_off)

			short_pair_off = -long_pair_off
			# use this amount to off set some longs and shorts. 

			# if price is 0, use impcming

			for tp in tps: 
				long_pair_off = self.tradingplans[tp].request_fufill(self.symbol_name,long_pair_off,self.data[BID])
				if long_pair_off<=0:
					break

			for tp in tps: 
				short_pair_off = self.tradingplans[tp].request_fufill(self.symbol_name,short_pair_off,self.data[BID])
				if short_pair_off>=0:
					break

			log_print(self.source,self.symbol_name	,"pair off,",want," amount", long_pair_off,short_pair_off)

	def holdings_update(self,price,share):

		with self.incoming_shares_lock:

			if price not in self.incoming_shares:

				self.incoming_shares[price] = share
			else:
				self.incoming_shares[price] += share

			
		#log_print("holding update - releasing lock")
		log_print("Symbol",self.symbol_name," holding update:",price,share)
		self.holding_update = True 

		hold_fill = threading.Thread(target=self.holdings_fill,daemon=True)
		hold_fill.start()

	def holdings_fill(self):

		if not self.fill_lock.locked():
			with self.fill_lock:

				#first wait for few seconds. 
				time.sleep(0.2)

				while self.order_processing_timer>0:
					time.sleep(0.1)
					self.order_processing_timer	-=0.1

				tps = list(self.tradingplans.keys())
				with self.incoming_shares_lock:

					#for each piece feed it.. to the requested.

					log_print(self.source,self.symbol_name," holding processing total:",sum(self.incoming_shares.values()))

					remaining = 0
					for price,share in self.incoming_shares.items():

						share_difference = share
						for tp in tps:
							share_difference = self.tradingplans[tp].request_fufill(self.symbol_name,share_difference,price)

							self.tradingplans[tp].notify_holding_change(self.symbol_name)
							if share_difference==0:
								break

						if share_difference!=0:
							remaining += share_difference


					self.incoming_shares = {}

					if remaining!=0:
						
						self.current_imbalance += remaining

						if self.current_imbalance!=0:
							log_print(self.source,self.symbol_name," Unmatched incoming shares: ",remaining, "total imblance:",self.current_imbalance ," USER INTERVENTION? SYSTEM VIOLATION!")
						else:
							log_print(self.source,self.symbol_name," account holding restored.")


				now = datetime.now()
				self.last_order_timestamp = now.hour*3600 + now.minute*60 + now.second
				self.order_processing_timer = 0
				self.symbol_inspection()
		else:
			if self.order_processing_timer<0.2:
				self.order_processing_timer=0.2

			
	def deploy_orders(self):

		# I NEED TO ADD A MECHANISM ON THIS
		# If passive orders still don't full fill the request everything within some minutes
		# Cancel all the requests. (or market in )

		# ALL ORDERS AT ONCE. # First clear previous order. 




		# if there might be already an order: #



		#if self.sent_orders==True:
		self.ppro_out.send([CANCEL,self.symbol_name]) 

		time.sleep(0.1)

		if self.difference>0:
			self.action = PASSIVEBUY
			#price = self.get_bid()
			#coefficient = -1

		else:
			self.action = PASSIVESELL
			#price = self.get_ask()
			#coefficient = 1

		log_print(self.source,self.symbol_name,self.action,self.difference)
		# self.ppro_out.send([CANCEL,self.symbol_name])
		# time.sleep(0.3)


		if self.difference!=0 and self.holding_update==False :

			total = abs(self.difference)
			if total>=500:
				total = 500
				log_print(self.source,self.symbol_name,self.action," adjusted to 200 instead of",self.difference)



			if self.aggresive_only==True:
				self.immediate_request(self.difference)
			else:
				self.ppro_out.send([self.action,self.symbol_name,total,0,self.manager.gateway])


			self.sent_orders = True 

		# handl = threading.Thread(target=self.threading_order,daemon=True)
		# handl.start()

	def threading_order(self):

			#lets add a bit of delay to it. 

		log_print(self.source,self.symbol_name,action,share)
		# self.ppro_out.send([CANCEL,self.symbol_name])
		# time.sleep(0.3)

		if self.difference!=0:
			self.ppro_out.send([self.action,self.symbol_name,abs(self.difference),0])

	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]

	def rejection_message(self,side):

		## iterate through all the TPs request. check who is requesting. if it is not running withdraw and cancel it. 
		
		if side == "Long":
			coefficient = 1
		elif side =="Short":
			coefficient = -1

		tps = list(self.tradingplans.keys())

		for tp in tps:
			if self.tradingplans[tp].having_request(self.symbol_name) and self.tradingplans[tp].get_holdings(self.symbol_name)==0:
		 		self.tradingplans[tp].rejection_handling(self.symbol_name)

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


	# deprecated 
	def calc_inspection_differences(self,tps):

		share_difference = self.current_shares - self.previous_shares


		if share_difference!=0:

			avg_price = 0
			with self.incoming_shares_lock:
				total = sum(list(self.incoming_shares.values()))
				#avg = mean(list(self.incoming_shares.keys()))

				if total!=0:

					c=0
					for key,item in self.incoming_shares.items():
						c+=key*item

					avg_price = c/total

				self.incoming_shares = {}

			if total>share_difference:
				log_print(self.source,self.symbol_name," having MORE orders than actual share difference.",share_difference," orders:",total)
			elif total<share_difference:
				log_print(self.source,self.symbol_name," having LESS orders than actual share difference.",share_difference," orders:",total)
				#? not enough?
			else:
				log_print(self.source,self.symbol_name," having share differences:",share_difference, " total:",total)


			### Construct a share_difference with avg price. 


			# LOADING MORE
			if abs(self.current_shares) > abs(self.previous_shares):

				# if orders not enough. manually calculate it. 
				if avg_price!=0:
					share_price = avg_price
				else:
					#### DONT USE THIS. DEPRECATED. ### NO MORE AVG PRICE BECAUSE INACCURACY. 
					share_price =  self.get_bid() #(abs(self.current_shares)*self.current_avgprice - abs(self.previous_shares)*self.previous_avgprice)/abs(share_difference)

				for tp in tps:
					share_difference = self.tradingplans[tp].request_fufill(self.symbol_name,share_difference,share_price)
						#feeeeed
					if share_difference	==0:
						break
			else:

				if avg_price!=0:
					share_price = avg_price
				else:
					share_price = self.get_bid()

				for tp in tps:
					share_difference = self.tradingplans[tp].request_fufill(self.symbol_name,share_difference,share_price)
						#feeeeed
					if share_difference	==0:
						break


		self.previous_shares,self.previous_avgprice = self.current_shares, self.current_avgprice


# def holdings_update(self,price,share):

# 	with self.incoming_shares_lock:

# 		if price not in self.incoming_shares:

# 			self.incoming_shares[price] = share
# 		else:
# 			self.incoming_shares[price] += share

		
# 	#log_print("holding update - releasing lock")
# 	log_print("Symbol",self.symbol_name," holding update:",price,share)
# 	self.holding_update = True 

# 	hold_fill = threading.Thread(target=self.holdings_fill,daemon=True)
# 	hold_fill.start()

# def holdings_fill(self):

# 	if not self.fill_lock.locked():
# 		with self.fill_lock:
# global wait_timer
# global d 
# wait_timer = 0
# incoming_shares_lock = threading.Lock()
# d = []

# def incoming(x):

# 	d.append(x)
# 	hold_fill = threading.Thread(target=holdings_fill,daemon=True)
# 	hold_fill.start()

# def holdings_fill():

# 	global wait_timer	
# 	global d
# 	if not incoming_shares_lock.locked():
# 		with incoming_shares_lock:

# 			time.sleep(0.1)# wait default time.

# 			while wait_timer>0:
# 				time.sleep(0.1)
# 				wait_timer-=0.1
# 			#goal: end needs to be printed.

# 			print(d)
# 			d=[]
# 	else:
# 		wait_timer+=0.1

# for i in range(5):

# 	incoming(i)
# 	time.sleep(0.08)

# time.sleep(5)