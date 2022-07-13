from constant import *
import tkinter as tk
#from Triggers import *
from Util_functions import *
from datetime import datetime, timedelta
import threading

def sign_test(a,b):

	return not ((a+b == abs(a)+abs(b)) or (a+b == -(abs(a)+abs(b))))

def abs_test(a,b):

	return abs(b)>abs(a)

def pair_off_test(a,b):

	return sign_test(a,b) and abs_test(a,b)


class Symbol:

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.

	"""
	'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445
	"""
	def __init__(self,symbol,support,resistence,stats,pproout):

		self.ticker = symbol
		self.symbol_name = symbol


		self.init_open = False
		self.init_high_low = False

		self.ppro_out = pproout

		self.numeric_labels = [TRADE_TIMESTAMP,TIMESTAMP,BID,ASK,RESISTENCE,SUPPORT,OPEN,HIGH,LOW,PREMARKETHIGH,PREMARKETLOW,STOP,EXIT,ENTRY,CUSTOM]

		self.tech_indicators = [EMACOUNT,EMA8H,EMA8L,EMA8C,EMA5H,EMA5L,EMA5C,EMA21H,EMA21L,EMA21C,CLOSE]

		self.data = {}
		self.tkvars = {}

		#for false range detection

		self.seen_high =0
		self.seen_low =0
		self.count = 0
		self.last_ts = 0
		self.init_ts = 0
		self.stats = stats
		self.mind = None
		self.mind_label = None


		self.market_making = False


		self.passive_request_ts = 0
		self.passive_price = 0
		"""
		UPGRADED PARTS

		+ for LONG. - for SHORTS

		"""
		self.active_tps = 0
		self.current_shares = 0
		self.total_expected = 0

		self.current_imbalance = 0

		# plus, minus, all the updates, all go here. 
		self.incoming_shares_lock = threading.Lock()
		self.incoming_shares = {}

		# 1. anyone wants anything, will register here. 
		# 2. System every second checks the outstanding shares and do corresponding actions. 
		# 3. For mutual canling requests - automatically granted each other. Otherwise, result in an imbalance. 

		self.management_request = False

		self.expecting_market_order = False

		### NEED LOCK FOR EACH OF THESE

		#self.incoming_request = {}

		self.tradingplan_lock = threading.Lock()
		self.tradingplans = {}
		#self.tradingplan_holdings = {}


		self.init_data(support,resistence,stats)
		self.ppro_out.send([REGISTER,self.ticker])

	def register_tradingplan(self,name,tradingplan):

		#self.incoming_request[name] = 0
		#self.tradingplan_holdings[name] = 0

		if self.get_market_making()==False:
			with self.tradingplan_lock:
				self.tradingplans[name] = tradingplan

			log_print(name,"registered at",self.ticker)

	def deregister_tradingplan(self,name,tradingplans):

		#del self.incoming_request[name]
		with self.tradingplan_lock:
			del self.tradingplans[name]

		log_print("name","deleted",self.ticker)

	def expecting_marketorder(self):
		self.expecting_market_order = True


	def get_management_request(self):
		return self.management_request

	def request_notified(self):
		self.management_request = True

	def immediate_request(self,shares):

		# I may need to cancel existing order first. for a 0.1 second delay.

		if shares<0:
			self.ppro_out.send([IOCSELL,self.ticker,abs(shares),self.get_bid()])
		else:
			self.ppro_out.send([IOCBUY,self.ticker,abs(shares),self.get_ask()])

	def turn_market_making(self,tp):

		self.market_making = True

		self.market_making_tp = tp

	def get_market_making(self):
		return self.market_making

	def clear_all_orders(self):
		self.ppro_out.send([CANCEL,self.ticker])

		#what if... hmm. there's a split second difference? 

	def load_confirmation(self,tradingplan_name,shares):

		self.tradingplan_holdings[tradingplan_name] += shares

	### RUN EVERY 3 SECONDS ###
	def symbol_inspection(self):

		#lets say I hae -100 and +100. so they cancel each other out. 

		#iterate each of the tradingplan once, starting from the smallest by magnitude. 


		# process the incoming orders.
		# deal with the remianing orders. 

		#### STAEGE 1 -> Incoming Shares Pairing #####

		#for tp,val in self.incoming_request.items():

		#first calculate all the positive, then all the negative? NO... it's by

		#log_print(self.ticker,"Inspection, holdings",self.incoming_shares)

		if len(self.incoming_shares)>0:

			### STAGE 1 -> Planed request handling 
			self.incoming_shares_pairing()

		#cur_imbalance = sum(self.incoming_request.values())

		# remian_shares =  0 #sum(self.incoming_shares.values())

		# for i in range(len(self.incoming_shares)):
		# 	remian_shares+=self.incoming_shares[i][1]

		### STAGE 2 -> Unplaned user event handling 
		#print(remian_shares,self.incoming_shares)

		#log_print(self.ticker,"UNPLANED SHARES PAIRING")

		remian_shares = sum(list(self.incoming_shares.values()))

		if remian_shares!=0:
			log_print(self.ticker,"unmatched shares:",remian_shares)

			self.unplan_shares_pairing()


		#log_print(self.ticker,"PASSIVE ORDERS")
			
		#### STAGE 3 -> MUTUAL PLANS PAIRING #####

		### CURRENTLY DISABLE ###

		# tps = sorted(self.incoming_request, key=lambda dict_key: abs(self.incoming_request[dict_key]))

		# #print(tps)

		# for i in range(len(tps)):
		# 	if abs(self.incoming_request[tps[i]])>0:
		# 		for j in range(i,len(tps)):
		# 			#if j > i and is opposite sign. 
		# 			if pair_off_test(self.incoming_request[tps[i]], self.incoming_request[tps[j]]):
		# 				self.pair_off(tps[i], tps[j])

		# log_print((self.ticker,"pairing sucessful, now remaining request: ",self.incoming_request))

		# log_print((self.ticker,"current shares remaning:",sum(self.incoming_request.values())))



		#### STAGE 2.5 CHecking if any flattened order is succesfully executed.


		# #### STAGE 3 -> IMBALANCE HANDLING  (NOT COUNTING THE FLATTENED ORDER) #####
		
		# remaining_share = sum(self.incoming_request.values())

		self.current_imbalance = self.get_all_imbalance()

		log_print(self.ticker,"current imbalance:",self.current_imbalance)

		if self.current_imbalance==0:

			self.management_request = False
			self.passive_price = 0

		else:

			if self.expecting_market_order!=True:
				self.passive_orders()
				

			# if remaining_share>0:
			# 	self.ppro_out.send([IOCBUY,self.ticker,abs(remaining_share),self.data[ASK]])
			# else:
			# 	self.ppro_out.send([IOCSELL,self.ticker,abs(remaining_share),self.data[BID]])

			## HERE USE PASSIVE ## 

		self.expecting_market_order = False

	def get_all_imbalance(self):

		total = 0

		tps = list(self.tradingplans.keys())

		for tp in tps:

			log_print(self.ticker,"checking",self.tradingplans[tp].name,"activated:",self.tradingplans[tp].if_activated(),"requested:",self.tradingplans[tp].having_request(self.symbol_name),\
				"flattening:",self.tradingplans[tp].get_flatten_order())
			if self.tradingplans[tp].if_activated() and self.tradingplans[tp].having_request(self.symbol_name) and not self.tradingplans[tp].get_flatten_order():

				total += self.tradingplans[tp].read_current_request(self.symbol_name)

		return total

	def incoming_shares_pairing(self):

		# two ways to go about this.. tp first.. then shares. OR, shares first, then TP. ideally they are equal.in practice ? SHARES FIRST


		with self.incoming_shares_lock:


			for price in self.incoming_shares.keys():

				tps = list(self.tradingplans.keys())

				for tp in tps:

					if self.tradingplans[tp].if_activated() and self.tradingplans[tp].having_request(self.symbol_name):

						val = self.tradingplans[tp].read_current_request(self.symbol_name)

						share = self.incoming_shares[price]

						if share >0 and val>0:


							paired = min(share,val)

							
							self.tradingplans[tp].ppro_process_orders(price,abs(paired),LONG,self.ticker)

							self.incoming_shares[price] -= paired

							#self.load_confirmation(tp,share)
							#self.incoming_request[tp]-=share


						elif share<0 and val<0:


							paired = max(share,val)
							
							self.tradingplans[tp].ppro_process_orders(price,abs(paired),SHORT,self.ticker)

							self.incoming_shares[price] -= paired
							#self.load_confirmation(tp,share)

							## if share is negative, then minus will add to it. 
							#self.incoming_request[tp]-=share

						if self.incoming_shares[price]==0:
							break


		## I MAY Have left overs. 

		self.cleanup_incoming_shares()

	def cleanup_incoming_shares(self):

		terms = []
		with self.incoming_shares_lock:
			for key,val in self.incoming_shares.items():
				if val==0:
					terms.append(key)

			for k in terms:
				del self.incoming_shares[k]

	def unplan_shares_pairing(self):

		### First see if you can kill some TPS

		### Then arbitarily add to some that risk is no full. 

		### OPPOSITE SIDE TEST ### THEN POSITIVE SIDE GIVE ####

		with self.incoming_shares_lock:

			## NOW KILL IT 

			for price in self.incoming_shares.keys():

				tps = list(self.tradingplans.keys())

				share =  self.incoming_shares[price]

				
				for tp in tps:
					#print("processing",tps,share,self.tradingplans[tp].having_request())
					if self.tradingplans[tp].if_activated():

						holding = self.tradingplans[tp].get_holdings(self.symbol_name)


						if  holding>0 and share*holding <0:

							paired = min(abs(share),abs(holding))

							self.tradingplans[tp].ppro_process_orders(price,abs(paired),SHORT,self.ticker)
							self.incoming_shares[price] -= -paired



						elif holding<0 and share*holding <0:

							paired = min(abs(share),abs(holding))


							self.tradingplans[tp].ppro_process_orders(price,abs(paired),LONG,self.ticker)
							self.incoming_shares[price] -= paired


						if self.incoming_shares[price]==0:
							break

			#self.cleanup_incoming_shares()
			## NOW ADD TO IT. 
			for price in self.incoming_shares.keys():

				tps = list(self.tradingplans.keys())

				share =  self.incoming_shares[price]

				for tp in tps:

					if self.tradingplans[tp].if_activated():

						holding = self.tradingplans[tp].get_holdings(self.symbol_name)

						if  holding>0 and share*holding >0:

							paired = min(share,holding)

							self.tradingplans[tp].ppro_process_orders(price,abs(paired),LONG,self.ticker)
							self.incoming_shares[price] -= paired

						elif holding<0 and share*holding >0:

							paired = max(share,holding)
							#self.tradingplans[tp].request_granted(paired)
							self.tradingplans[tp].ppro_process_orders(price,abs(paired),SHORT,self.ticker)

							self.incoming_shares[price] -= paired
							#self.load_confirmation(tp,share)

							## if share is negative, then minus will add to it. 
							#self.incoming_request[tp]-=share
							#paired.append(t)

						if self.incoming_shares[price]==0:
							break

			


			## whatever it is now. it is none of my business.
			if len(self.incoming_shares)>=1:
				log_print("discarding:",self.incoming_shares)
				self.incoming_shares = {}

		self.cleanup_incoming_shares()

	def passive_orders(self):

		DELAY = 3

		coefficient = 0.01
		k = self.get_bid()//100
		if k==0: k = 1
		
		spread = (self.get_ask() -self.get_bid())
		midpoint = round((self.get_ask() +self.get_bid())/2,2)

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

	
		order_process = False

		# PRICE IS NOW THE OFFSET.
		# LONG: use - if 0.01, if gap, can be slightly aggresive.
		# SHORT: use + to lift it. 

		if self.current_imbalance>0:

			action = PASSIVEBUY
			price = self.get_bid()
			coefficient = -1
			if (price >= self.passive_price+0.01) or (self.passive_price==0) or (price<= self.passive_price-0.02):
				order_process = True

		else:
			action = PASSIVESELL
			price = self.get_ask()
			coefficient = 1
			if price <= self.passive_price -0.01 or (price>= self.passive_price+0.02) or (self.passive_price==0) :
				order_process = True

			if ts > self.passive_request_ts + 15:
				order_process = True

		log_print(self.ticker,"order:",price,order_process,"delayed:",ts > self.passive_request_ts + DELAY)

		if order_process and ts > self.passive_request_ts + DELAY:



			total_shares = abs(self.current_imbalance)
			self.passive_request_ts = ts

			#step 1, cancel existing orders
			self.ppro_out.send([CANCEL,self.ticker])
			#step 2, placing around current.
			#time.sleep(0.2)

			#case 1. tight spread. no midpoint possibility.

			if total_shares<=5:

				self.ppro_out.send([action,self.ticker,total_shares,0])

			elif spread <= 0.02:

				share = total_shares//2
				remaning = total_shares-share

				self.ppro_out.send([action,self.ticker,share,0])
				self.ppro_out.send([action,self.ticker,remaning,0.01*coefficient])


			elif spread >= 0.03:

				share = total_shares//2
				remaning = total_shares-share

				self.ppro_out.send([action,self.ticker,share,0])
				#mid point. 
				self.ppro_out.send([action,self.ticker,remaning,round((spread/2)*coefficient*-1,2)])



			self.passive_price = price


	def check_holdings(self):

		with self.incoming_shares_lock:

			return sum(list(self.incoming_shares.values()))

			
	def holdings_update(self,price,share):

		#log_print("holding update - optaning lock")


		if self.get_market_making()==False:
			with self.incoming_shares_lock:

				if price not in self.incoming_shares:

					self.incoming_shares[price] = share
				else:
					self.incoming_shares[price] += share
					#self.incoming_shares.append((price,share))

				self.management_request = True

		else:
			if share>0:
				self.market_making_tp.ppro_process_orders(price,abs(share),LONG,self.ticker)
			else:
				self.market_making_tp.ppro_process_orders(price,abs(share),SHORT,self.ticker)
			
		#log_print("holding update - releasing lock")
		#print("inc",self.incoming_shares)

	def rejection_message(self,side):

		## iterate through all the TPs request. check who is requesting. if it is not running withdraw and cancel it. 

		if side == "Long":
			coefficient = 1
		elif side =="Short":
			coefficient = -1

		tps = list(self.tradingplans.keys())

		for tp in tps:

			if self.tradingplans[tp].if_activated() and self.tradingplans[tp].having_request(self.symbol_name) and not self.tradingplans[tp].get_flatten_order():

				val = self.tradingplans[tp].read_current_request(self.symbol_name)

				if val*coefficient >0:
		 			self.tradingplans[tp].rejection_handling(self.ticker)
	

	def pair_off(self,tp1,tp2):

		#granted tp1 whatever it wants
		#granted tp2 the share tp1 wants. 

		#price,shares,side

		if self.incoming_request[tp1]>0:
			self.tradingplans[tp1].ppro_process_orders(self.get_bid(),self.incoming_request[tp1],LONG,self.ticker)
			self.tradingplans[tp2].ppro_process_orders(self.get_bid(),abs(self.incoming_request[tp1]),SHORT,self.ticker)

			self.load_confirmation(tp1,abs(self.incoming_request[tp1]))
			self.load_confirmation(tp2,-abs(self.incoming_request[tp1]))
		else:
			self.tradingplans[tp1].ppro_process_orders(self.get_bid(),abs(self.incoming_request[tp1]),SHORT,self.ticker)
			self.tradingplans[tp2].ppro_process_orders(self.get_bid(),self.incoming_request[tp1],LONG,self.ticker)

			self.load_confirmation(tp1,-abs(self.incoming_request[tp1]))
			self.load_confirmation(tp2,abs(self.incoming_request[tp1]))

		self.incoming_request[tp2] += self.incoming_request[tp1]
		self.incoming_request[tp1] = 0


	def set_data(self,support,resistence,stats):
		for key,value in stats.items():
			self.data[key] = value

		self.data[RESISTENCE] = resistence
		self.data[SUPPORT] = support

		# self.tkvars[RESISTENCE].set(resistence)
		# self.tkvars[SUPPORT].set(support)

	def init_data(self,support,resistence,stats):

		for i in self.numeric_labels:
			self.data[i] = 0
			
		for i in self.tech_indicators:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar()

		for key,value in stats.items():
			self.data[key] = value

		self.data[RESISTENCE] = resistence
		self.data[SUPPORT] = support

		
	def flatten_cmd(self,tp):

		#if i only have 1 tp actived. just flatten.
		#print(self.tradingplans)
		if len(list(self.tradingplans.keys())) ==1:
			self.ppro_out.send(["Flatten",self.ticker])
		else:

			tp = self.tradingplans[tp]
			if tp.get_holdings()>0:
				self.ppro_out.send([IOCSELL,self.ticker,abs(tp.get_holdings()),self.get_bid()])
			else:
				self.ppro_out.send([IOCBUY,self.ticker,abs(tp.get_holdings()),self.get_ask()])
		#else get out the corresponding shares. 

	def update_techindicators(self,dic):
		for key,value in dic.items():
			if key in self.data:
				self.data[key]=value
				self.tkvars[key].set(value)
				
		#print(self.data)
		#print(dic)
#
	def toggle_autorange(self,Bool):
		self.data[AUTORANGE] = Bool

	def get_name(self):
		return self.ticker


	def update_price(self,bid,ask,ts):

		#print("price",bid,ask,ts)
		if self.data[BID]!= bid and self.data[ASK]!=ask:

			self.data[BID] = bid
			self.data[ASK] = ask
			self.data[TIMESTAMP] = ts

		#update on the tradingplans. 
		#print(self.tradingplans.keys())

		if self.get_market_making()==False:



			tps = list(self.tradingplans.values())
			#print("tp update",bid,ask,ts,tps)

			for val in tps:
				
				#print(bid,ask,ts)
				val.ppro_update_price(symbol=self.ticker,bid=bid,ask=ask,ts=ts)
		else:
			
			self.market_making_tp.ppro_update_price(symbol=self.ticker,bid=bid,ask=ask,ts=ts)
	def update_price_old(self,bid,ask,ts,AR,pos):

		try:
			if self.data[BID]!= bid and self.data[ASK]!=ask:
				

				#print(ts,self.data[BID],self.data[ASK],self.data[RESISTENCE],self.data[SUPPORT],self.data[HIGH],self.data[LOW])
				if pos ==PENDING:
					self.set_mind("REGISTERED",VERYLIGHTGREEN)

				if AR==True and pos==PENDING and ts<34200:
					if ask>self.data[RESISTENCE]:
						self.data[RESISTENCE]=ask
					if self.data[SUPPORT] == 0:
						self.data[SUPPORT] = bid
					if bid<self.data[SUPPORT]:
						self.data[SUPPORT] = bid
					self.tradingplan.update_symbol_tkvar()

				#print(self.data)
				#34200 openning.

				if ts>=34200:
					if self.data[HIGH]==0:
						self.data[HIGH] = ask
					if self.data[LOW] ==0:
						self.data[LOW] = bid 

					if self.data[ASK]>self.data[HIGH]:
						self.data[HIGH] = self.data[ASK]
					if self.data[BID]<self.data[LOW]:
						self.data[LOW]= self.data[BID]

				#print("sy",self.ask,self.high,self.output)

				self.data[BID] = bid
				self.data[ASK] = ask
				self.data[TIMESTAMP] = ts

				#self.false_range_detection(bid,ask,ts)

				#print(self.data)
				#notify trading plan that price has changed. 

		except:
			PrintException(self.get_name()+" Updating price error :")

	def set_phigh(self,v):
		self.data[PREMARKETHIGH]=v

	def set_plow(self,v):
		self.data[PREMARKETLOW]=v

	def set_high(self,v):
		self.data[HIGH]=v
		
	def set_low(self,v):
		self.data[LOW]=v

	def set_support(self,v):
		self.data[SUPPORT]=v

	def set_resistence(self,v):
		self.data[RESISTENCE]=v


	def get_stats(self):
		return self.stats
	def get_data(self):
		return self.data

	def get_support(self):
		return self.data[SUPPORT]

	def get_resistence(self):
		return self.data[RESISTENCE]

	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]

	def get_time(self):
		return self.data[TIMESTAMP]
	# def add_trigger(self,info,type_,trigger_price,timer):
	# 	self.triggers.append(trigger(self,info,type_,trigger_price,timer))

	def get_close(self):

		return self.data[CLOSE]



# print('inital',t)


def sign_test(a,b):

	return not ((a+b == abs(a)+abs(b)) or (a+b == -(abs(a)+abs(b))))

def abs_test(a,b):

	return abs(b)>abs(a)

def pair_off_test(a,b):

	return sign_test(a,b) and abs_test(a,b)


# total_imbalance = sum(t.values())




# cur_imbalance = sum(t.values())

# tps = sorted(t, key=lambda dict_key: abs(t[dict_key]))

# for i in range(len(tps)):
# 	if abs(t[tps[i]])>0:
# 		for j in range(i,len(tps)):
# 			#if j > i and is opposite sign. 
# 			if pair_off_test(t[tps[i]], t[tps[j]]):
# 				pair_off(t, tps[i], tps[j])



# 	if cur_imbalance <= total_imbalance:
# 		break


# a = {}
# a["a"] = 1
# a["b"] = 0
# a["c"] = 1

# print(list(a.values()))

	# def incoming_shares_pairingB(self):

	# 	# two ways to go about this.. tp first.. then shares. OR, shares first, then TP. ideally they are equal.in practice ? SHARES FIRST

	# 	paired = []
	# 	for t in range(len(self.incoming_shares)):

	# 		price = self.incoming_shares[t][0]
	# 		share = self.incoming_shares[t][1]

	# 		for tp,val in self.incoming_request.items():

	# 			if share >0 and val>0:
	# 				self.tradingplans[tp].ppro_process_orders(price,abs(share),LONG,self.ticker)

	# 				self.load_confirmation(tp,share)

	# 				self.incoming_request[tp]-=share

	# 				paired.append(t)

	# 				break
	# 			elif share<0 and val<0:
	# 				self.tradingplans[tp].ppro_process_orders(price,abs(share),SHORT,self.ticker)

	# 				self.load_confirmation(tp,share)

	# 				## if share is negative, then minus will add to it. 
	# 				self.incoming_request[tp]-=share
	# 				paired.append(t)

	# 				break

	# 	#log_print(self.ticker,"incoming shares",self.incoming_shares)

	# 	c = 0
	# 	for i in paired:
	# 		self.incoming_shares.pop(i-c)
	# 		c+=1
	# 		# try:
				
	# 		# except Exception as e:
	# 		# 	print(e,"poping failure",e,i,self.incoming_shares)

# a = {}

# a['a']=2
# a['b']=3
# a['c']=4

# for key,v in a.items():

# 	for i in range(5):
# 		a[key]-=1
# 		if a[key]==0:
# 			break

# print(a)