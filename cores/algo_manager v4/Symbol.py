from constant import *
import tkinter as tk
#from Triggers import *
from Util_functions import *
from datetime import datetime, timedelta
import threading





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
		self.active_tps = 0
		self.current_shares = 0
		self.total_expected = 0

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

		difference = self.calc_total_imbalances()

		if difference!=0:
			self.deploy_orders(difference)

			log_print(self.symbol_name," inspection complete, deploying:",difference)

		else:
			log_print(self.symbol_name," inspection complete, no action needed.")

	def calc_total_imbalances(self):

		current_shares = self.manager.get_position(self.symbol_name)[1]

		expected = self.get_all_expected()

		difference = expected - current_shares


		return difference

	def get_all_expected(self):

		"""
		Doesnt matter if the TP is running or not, having request or not. it runs through. 
		The less the parameter, the more generalizability 
		"""
		expected = 0

		tps = list(self.tradingplans.keys())

		for tp in tps:
			expected +=  self.tradingplans[tp].get_current_expected(self.symbol_name)
		return expected


	def deploy_orders(self,difference):

		# I NEED TO ADD A MECHANISM ON THIS
		# If passive orders still don't full fill the request everything within some minutes
		# Cancel all the requests. (or market in )

		# ALL ORDERS AT ONCE. # First clear previous order. 

		if difference>0:
			action = PASSIVEBUY
			price = self.get_bid()
			coefficient = -1

		else:
			action = PASSIVESELL
			price = self.get_ask()
			coefficient = 1

		handl = threading.Thread(target=self.threading_order,args=(action,difference,),daemon=True)
		handl.start()


	def threading_order(self,action,share):

			#lets add a bit of delay to it. 
		self.ppro_out.send([CANCEL,self.symbol_name])
		time.sleep(0.3)
		self.ppro_out.send([action,self.symbol_name,abs(share),0])

	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]


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