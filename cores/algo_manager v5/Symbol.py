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

		self.current_avgprice = 0
		self.total_expected = 0


		self.rejections = {}

		"""


		"""
		self.expected = 0
		self.difference = 0

		self.all_remaining = 0 

		self.action=""

		self.market_out = 0

		self.current_imbalance = 0

		self.fill_time_remianing = 0

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

	def turn_off_aggresive_only(self):
		self.aggresive_only = False 

	def turn_off_insepction(self):
		self.enabled_insepction = False 

	def init_data(self):

		for i in self.numeric_labels:
			self.data[i] = 0
			
		for i in self.tech_indicators:
			self.data[i] = 0

	def register_tradingplan(self,name,tradingplan):

		self.tradingplans[name] = tradingplan

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

		# self.data[ASK] = ask
		# self.data[BID] = bid

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
			#log_print(self.symbol_name,"Inspecting:")
			with self.inspection_lock:
				# timestamp = self.get_ts()
				# while (timestamp - self.last_order_timestamp<=2) or (timestamp -self.inspection_timestamp<=2):
				# 	log_print(self.symbol_name,"inspection: inspection wait:",timestamp - self.last_order_timestamp,timestamp -self.inspection_timestamp)
				# 	time.sleep(1)
				# 	timestamp = self.get_ts()

				
				tps = list(self.tradingplans.keys())
				self.update_stockprices(tps)

				# CRITICAL SECTION. 
				with self.incoming_shares_lock:


					self.check_all_incrementals(tps)

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

				if self.difference==0:
					self.sent_orders= False 

				if self.holding_update==False:
					if self.difference!=0 and ts<=57590:
						self.inspection_timestamp = ts
						self.deploy_orders(ts)
						return 1

					else:
						self.action = ""
				else:
					#log_print(self.symbol_name," holding change detected. skipping ordering. estimate difference:",self.difference)
					self.holding_update=False 

			return 0
		else:
			log_print(self.symbol_name,"Inspection LOCKED")
			return 0 


	def update_stockprices(self,tps):
		
		for tp in tps:
			self.tradingplans[tp].update_stockprices(self.symbol_name,self.get_bid())


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

		pass 


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

			PrintException(self.symbol_name,e)

		self.ask_change = True 
		self.bid_change = True 


	def calc_total_imbalances(self,tps):

		### STAGE 1. JUST UPDATE THE TPs. 
		self.current_avgprice,current_shares = self.manager.get_position(self.symbol_name)
		self.current_shares,self.expired = self.get_all_current(tps)
		self.expected = self.get_all_expected(tps)
		self.difference = self.expected - self.current_shares 


		### ISSUE: lagging imblance issue later occur. i need to reset it when it's GOOD. ###

		### OK NEW SYSTEM.

		### ONLY HANDLE IMBALNCE WHEN -> TP-EXPECT == PPRO-EXPECT. THERE IS NO IMBLANCE RESET.

		

		if self.difference==0 and self.current_imbalance!=0:

			if self.current_imbalance + self.current_shares == current_shares:
				log_print(self.source,self.symbol_name," inspection discrepancy: discrepancy matched. ",self.current_imbalance,current_shares-self.current_shares)
				self.difference += self.current_imbalance * -1

		if self.difference!=0:
			log_print(self.source,self.symbol_name,"Current:",self.current_shares,"Expected:",self.expected,"Difference:",self.difference,"Expired:",self.expired)
		######################################################################################


	def get_all_current(self,tps):

		current_shares = 0
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

		#self.fill_time_remianing = min(round((ts-self.tradingplans[tp].get_request_time(self.symbol_name))/self.fill_timer,2),1)

		cur_time = 0

		for tp in tps:
			if self.tradingplans[tp].get_inspectable():
				current_shares +=  self.tradingplans[tp].get_current_share(self.symbol_name)

				if self.tradingplans[tp].get_request_time(self.symbol_name)>cur_time:
					cur_time = self.tradingplans[tp].get_request_time(self.symbol_name)

				#log_print(self.source,self.symbol_name,tp, "fill timer",round((ts-self.tradingplans[tp].get_request_time(self.symbol_name))/self.fill_timer,2))

				if ts-self.tradingplans[tp].get_request_time(self.symbol_name)>self.fill_timer:
					expired+=self.tradingplans[tp].get_current_request(self.symbol_name)

		self.fill_time_remianing = round((ts-cur_time)/self.fill_timer,2)

		self.fill_time_remianing = min(self.fill_time_remianing,1)

		return current_shares,expired

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

	def check_all_incrementals(self,tps):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		for tp in tps:
			self.tradingplans[tp].check_incremental(self.symbol_name,ts)


	def get_difference(self):
		return self.difference

	def pair_off(self,tps):
		
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

		if long_pair_off>0:	

			#log_print(self.source,self.symbol_name	,"pair off,",want," amount", long_pair_off,short_pair_off)

			short_pair_off = -long_pair_off
			# use this amount to off set some longs and shorts. 

			# if price is 0, use impcming

			for tp in tps: 
				if self.tradingplans[tp].get_inspectable():
					long_pair_off = self.tradingplans[tp].request_fufill(self.symbol_name,long_pair_off,self.data[BID])
					if long_pair_off<=0:
						break

			for tp in tps: 
				if self.tradingplans[tp].get_inspectable():
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

				total_tp = list(self.tradingplans.keys())


				now = datetime.now()
				ts = now.hour*3600 + now.minute*60+ now.second

				tps = []

				tps = {}

				for tp in total_tp:
					if self.tradingplans[tp].get_inspectable():
						request_time = ts-self.tradingplans[tp].get_request_time(self.symbol_name)
						tps[tp] =request_time

				for tp in total_tp: #EVERYTHING ELSE.
					if tp not in tps:
						request_time = ts-self.tradingplans[tp].get_request_time(self.symbol_name)
						tps[tp] =request_time

				sorted_dict = dict(sorted(tps.items(), reverse=True))
				tps = list(sorted_dict.keys())

				if len(tps)!=len(total_tp):
					log_print(self.source,self.symbol_name,"WARNING, WARNING. TP ORDERS UNMATCH.",total_tp,sorted_dict,)


				with self.incoming_shares_lock:

					#for each piece feed it.. to the requested.

					log_print(self.source,self.symbol_name," holding processing total:",sum(self.incoming_shares.values()))

					remaining = 0
					for price,share in self.incoming_shares.items():

						share_difference = share

						### HERE I SHOULD MAKE PRIORITIZATION. NON_MANUAL, NON INSPECTABLE LAST. 
						for tp in tps:
							share_difference = self.tradingplans[tp].request_fufill(self.symbol_name,share_difference,price)

							self.tradingplans[tp].notify_holding_change(self.symbol_name)
							if share_difference==0:
								break

						if share_difference!=0:
							remaining += share_difference

					######################################SECONDARY REQUEST FILL #########################################################################


					######################################################################################################################################

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
			
	def cancel_request(self):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if self.aggresive_only!=True and ts<57500:

			### NEED TO KNOW IF. HMM .
			self.ppro_out.send([CANCEL,self.symbol_name])	

	def deploy_orders(self,ts):

		# I NEED TO ADD A MECHANISM ON THIS
		# If passive orders still don't full fill the request everything within some minutes
		# Cancel all the requests. (or market in )

		# ALL ORDERS AT ONCE. # First clear previous order. 
		# if there might be already an order: #


		if self.difference>0:
			self.action = PASSIVEBUY
		else:
			self.action = PASSIVESELL

		self.l1_update_module()

		skip = True 

		if self.aggresive_only!=True and ts<57500:
			if self.action==PASSIVEBUY and (self.bid_change==True or self.data['SPREAD']>0.05):
				self.ppro_out.send([CANCEL,self.symbol_name]) 
				skip = False 
			elif self.action==PASSIVESELL and (self.ask_change==True or self.data['SPREAD']>0.05):
				self.ppro_out.send([CANCEL,self.symbol_name])
				skip = False 

		if self.sent_orders==False:
			skip = False 

			# else:
				
			# 	skip = False ☺
		# if self.aggresive_only!=True and ts<57500:
		# 	self.ppro_out.send([CANCEL,self.symbol_name]) 


		time.sleep(0.1)

			#price = self.get_ask()
			#coefficient = 1

		#log_print(self.source,self.symbol_name,self.action,self.difference)
		# self.ppro_out.send([CANCEL,self.symbol_name])
		# time.sleep(0.3)

		## self.fill_time_remianing
		log_print(self.source,self.symbol_name,self.action,self.difference,self.fill_timer,"fill timer:",self.fill_time_remianing)

		## if 

		if self.difference!=0 and self.holding_update==False :

			total = abs(self.difference-self.expired)
			if total>=500:
				total = 500
				log_print(self.source,self.symbol_name,self.action," adjusted to 500 instead of",self.difference)

			if self.expired!=0:
				self.ppro_out.send([CANCEL,self.symbol_name]) 
				time.sleep(0.1)
				self.immediate_request(self.expired)
			if self.aggresive_only==True or ts>57500: ### LAST 100 seconds market only.
				self.immediate_request(self.difference)
				self.sent_orders = True 
			else:
				if not skip and total!=0:

					###### ADJUST THE spread
					adjustment = 0 

					if self.data['SPREAD']>0.01:

						if self.fill_time_remianing>1:
							self.fill_time_remianing=1
							
						adjustment = round((self.fill_time_remianing)*self.data['SPREAD'],2) # % of spread.

						if adjustment <0.01:
							adjustment = 0.01 

						if adjustment>3:
							adjustment = 3

					if self.action==PASSIVESELL:
						adjustment = adjustment*-1
						
					log_print(self.source,self.symbol_name,"orders:","fill timer:",self.fill_time_remianing,"spread:",self.data['SPREAD'],"adjustment:",adjustment)

					self.ppro_out.send([self.action,self.symbol_name,total,adjustment,self.manager.gateway])
					self.sent_orders = True 
				# else:
				# 	log_print(self.source,self.symbol_name,"NO CHANGE DETECTED, skipping.")

		# handl = threading.Thread(target=self.threading_order,daemon=True)
		# handl.start()

	def threading_order(self):

			#lets add a bit of delay to it. 

		log_print(self.source,self.symbol_name,action,share)


		if self.difference!=0:
			self.ppro_out.send([self.action,self.symbol_name,abs(self.difference),0])

	def get_price(self):
		return self.data[PRICE]

	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]

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


		if timestamp not in self.rejections:
			self.rejections[timestamp] = 1 
		else:
			self.rejections[timestamp] +=1

		if self.rejections[timestamp] >=2:

			### all tp as is.
			tps = list(self.tradingplans.keys())

			#### FOR THE TP TRYING TO START THE POSITION. IGNORE. 
			for tp in tps:
				if self.tradingplans[tp].having_request(self.symbol_name) and self.tradingplans[tp].get_holdings(self.symbol_name)!=0:
					self.tradingplans[tp].algo_as_is()

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


	# deprecated 
	def calc_inspection_differences(self,tps):

		share_difference = self.current_shares - self.previous_shares


		if share_difference!=0:

			avg_price = 0
			with self.incoming_shares_lock:
				total = sum(list(self.incoming_shares.values()))
				#avg = mean(list(self.incoming_shares.keys()))`

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


	def ppro_flatten(self):
		self.ppro_out.send([FLATTEN,self.symbol_name])
