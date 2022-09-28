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
	def __init__(self,symbol,pproout):

		self.ticker = symbol
		self.symbol_name = symbol

		self.ppro_out = pproout

		self.numeric_labels = [TRADE_TIMESTAMP,TIMESTAMP,BID,ASK,RESISTENCE,SUPPORT,OPEN,HIGH,LOW,,PREMARKETLOW,STOP,EXIT,ENTRY,CUSTOM]
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



	def register_tradingplan(self,name,tradingplan):

		#self.incoming_request[name] = 0
		#self.tradingplan_holdings[name] = 0
		self.tradingplans[name] = tradingplan

	def update_price(self,bid,ask,ts):

		#print("price",bid,ask,ts)
		if self.data[BID]!= bid and self.data[ASK]!=ask:

			self.data[BID] = bid
			self.data[ASK] = ask
			self.data[TIMESTAMP] = ts

		# tps = list(self.tradingplans.values())
		# #print("tp update",bid,ask,ts,tps)

		# for val in tps:
			
		# 	#print(bid,ask,ts)
		# 	val.ppro_update_price(symbol=self.ticker,bid=bid,ask=ask,ts=ts)



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