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

		self.symbol_name = symbol
		self.manager = manager 

		self.ppro_out = pproout

		self.numeric_labels = [TRADE_TIMESTAMP,TIMESTAMP,BID,ASK,RESISTENCE,SUPPORT,OPEN,HIGH,LOW,PREMARKETLOW,STOP,EXIT,ENTRY,CUSTOM]
		self.tech_indicators = [EMACOUNT,EMA8H,EMA8L,EMA8C,EMA5H,EMA5L,EMA5C,EMA21H,EMA21L,EMA21C,CLOSE]

		self.data = {}
		self.tkvars = {}


		self.passive_request_ts = 0
		self.passive_price = 0

		"""
		UPGRADED PARTS

		"""

		self.previous_shares = 0
		self.previous_avgprice = 0

		self.active_tps = 0
		self.current_shares = 0
		self.current_avgprice = 0
		self.total_expected = 0


		"""

		"""
		self.expected = 0
		self.difference = 0
		self.action=""


		self.current_imbalance = 0

		# plus, minus, all the updates, all go here. 
		self.incoming_shares_lock = threading.Lock()
		self.incoming_shares = {}

		#self.tradingplan_lock = threading.Lock()
		self.tradingplans = {}

		self.init_data()
		
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

	def symbol_inspection(self):

		"""
		For both load and unload
		"""

		tps = list(self.tradingplans.keys())

		# no.1 update the current prices
		self.update_stockprices(tps)

		# no.2 pair off
		self.pair_off(tps)
		# no.3 pair orders 

		self.calc_inspection_differences(tps)

		# no.4 get all current imbalance
		self.calc_total_imbalances(tps)

		if self.difference!=0:
			self.deploy_orders()
		else:
			self.action = ""

	def update_stockprices(self,tps):
		
		for tp in tps:
			self.tradingplans[tp].update_stockprices(self.symbol_name,self.get_bid())


	def calc_total_imbalances(self,tps):

		self.current_avgprice,self.current_shares = self.manager.get_position(self.symbol_name)

		self.expected = self.get_all_expected(tps)

		self.difference = self.expected - self.current_shares

		if self.difference!=0:

			log_print(self.symbol_name," inspection complete,self.expected",self.expected," have",self.current_shares," deploying:",self.difference)
		else:
			log_print(self.symbol_name," inspection complete,self.expected",self.expected," have",self.current_shares)



	def get_all_expected(self,tps):

		"""
		Doesnt matter if the TP is running or not, having request or not. it runs through. 
		The less the parameter, the more generalizability 
		"""
		self.expected = 0
		
		for tp in tps:
			self.expected +=  self.tradingplans[tp].get_current_expected(self.symbol_name)
		

		return self.expected



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

			log_print("Symbol",self.symbol_name	,"pair off,",want," amount", long_pair_off)
			short_pair_off = -long_pair_off
			# use this amount to off set some longs and shorts. 

			for tp in tps: 
				long_pair_off = self.tradingplans[tp].request_fufill(self.symbol_name,long_pair_off,self.data[BID])
				if long_pair_off<=0:
					break

			for tp in tps: 
				short_pair_off = self.tradingplans[tp].request_fufill(self.symbol_name,short_pair_off,self.data[BID])
				if short_pair_off>=0:
					break


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
				log_print(self.symbol_name," having MORE orders than actual share difference.",share_difference," orders:",total)
			elif total<share_difference:
				log_print(self.symbol_name," having LESS orders than actual share difference.",share_difference," orders:",total)
				#? not enough?


			### Construct a share_difference with avg price. 


			# LOADING MORE
			if abs(self.current_shares) > abs(self.previous_shares):


				# if orders not enough. manually calculate it. 
				if avg_price!=0:
					share_price = avg_price
				else:
					share_price =  (abs(self.current_shares)*self.current_avgprice - abs(self.previous_shares)*self.previous_avgprice)/abs(share_difference)


				for tp in tps:
					share_difference = self.tradingplans[tp].request_fufill(self.symbol_name,share_difference,share_price)
						#feeeeed
					if share_difference	==0:
						break

			else:

				if avg_price!=0:
					share_price = avg_price
				else:
					share_price =  self.data[BID]

				for tp in tps:
					share_difference = self.tradingplans[tp].request_fufill(self.symbol_name,share_difference,share_price)
						#feeeeed
					if share_difference	==0:
						break



		self.previous_shares,self.previous_avgprice = self.current_shares, self.current_avgprice
			



	def deploy_orders(self):

		# I NEED TO ADD A MECHANISM ON THIS
		# If passive orders still don't full fill the request everything within some minutes
		# Cancel all the requests. (or market in )

		# ALL ORDERS AT ONCE. # First clear previous order. 

		if self.difference>0:
			self.action = PASSIVEBUY
			#price = self.get_bid()
			#coefficient = -1

		else:
			self.action = PASSIVESELL
			#price = self.get_ask()
			#coefficient = 1

		log_print("Symbol: ",self.symbol_name,self.action,self.difference)
		# self.ppro_out.send([CANCEL,self.symbol_name])
		# time.sleep(0.3)
		self.ppro_out.send([self.action,self.symbol_name,abs(self.difference),0])

		# handl = threading.Thread(target=self.threading_order,daemon=True)
		# handl.start()


	def threading_order(self):

			#lets add a bit of delay to it. 

		log_print("Symbol: ",self.symbol_name,action,share)
		# self.ppro_out.send([CANCEL,self.symbol_name])
		# time.sleep(0.3)
		self.ppro_out.send([self.action,self.symbol_name,abs(self.difference),0])

	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]


	def holdings_update(self,price,share):

		with self.incoming_shares_lock:

			if price not in self.incoming_shares:

				self.incoming_shares[price] = share
			else:
				self.incoming_shares[price] += share

			
		#log_print("holding update - releasing lock")
		#print("inc",self.incoming_shares)
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
	# 				self.tradingplans[tp].ppro_process_orders(price,abs(share),LONG,self.symbol_name)

	# 				self.load_confirmation(tp,share)

	# 				self.incoming_request[tp]-=share

	# 				paired.append(t)

	# 				break
	# 			elif share<0 and val<0:
	# 				self.tradingplans[tp].ppro_process_orders(price,abs(share),SHORT,self.symbol_name)

	# 				self.load_confirmation(tp,share)

	# 				## if share is negative, then minus will add to it. 
	# 				self.incoming_request[tp]-=share
	# 				paired.append(t)

	# 				break

	# 	#log_print(self.symbol_name,"incoming shares",self.incoming_shares)

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
# a={}
# a[5]=2
# a[6]=2

# c=0
# t=0
# for key,item in a.items():
# 	c+=key*item
# 	t+=item
# print(c/t)