from constant import *
import tkinter as tk
#from Triggers import *
from Util_functions import *
from datetime import datetime, timedelta


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


		self.passive_request_ts = 0
		self.passive_price = 0
		"""
		UPGRADED PARTS

		+ for LONG. - for SHORTS

		"""
		self.current_shares = 0

		self.current_imbalance = 0

		# plus, minus, all the updates, all go here. 
		self.incoming_shares = []

		# 1. anyone wants anything, will register here. 
		# 2. System every second checks the outstanding shares and do corresponding actions. 
		# 3. For mutual canling requests - automatically granted each other. Otherwise, result in an imbalance. 

		self.share_request = False

		### NEED LOCK FOR EACH OF THESE

		self.incoming_request = {}
		self.tradingplans = {}
		self.tradingplan_holdings = {}


		self.init_data(support,resistence,stats)
		self.ppro_out.send([REGISTER,self.ticker])

	def register_tradingplan(self,name,tradingplan):

		self.incoming_request[name] = 0
		self.tradingplan_holdings[name] = 0
		self.tradingplans[name] = tradingplan

		log_print(name,"registered at",self.ticker)

	def deregister_tradingplan(self,name,tradingplans):

		del self.incoming_request[name]
		del self.tradingplans[name]


	### PASSIVE/ACTIVE REQUEST ? ####
	def new_request(self,tradingplan_name,shares,passive=""):

		self.incoming_request[tradingplan_name] += shares 

		log_print("new request",self.incoming_request)

		self.share_request = True

	def load_confirmation(self,tradingplan_name,shares):

		self.tradingplan_holdings[tradingplan_name] += shares

	def cancel_all_request(self,tradingplan_name):


		self.incoming_request[tradingplan_name] = 0


	### RUN EVERY 3 SECONDS ###
	def mutual_request_handler(self):

		#lets say I hae -100 and +100. so they cancel each other out. 

		#iterate each of the tradingplan once, starting from the smallest by magnitude. 


		# process the incoming orders.
		# deal with the remianing orders. 

		#### STAEGE 1 -> Incoming Shares Pairing #####

		#for tp,val in self.incoming_request.items():

		#first calculate all the positive, then all the negative? NO... it's by

		if len(self.incoming_shares)>0:


			### STAGE 1 -> Planed request handling 
			self.incoming_shares_pairing()


		cur_imbalance = sum(self.incoming_request.values())

		remian_shares =  0 #sum(self.incoming_shares.values())

		for i in range(len(self.incoming_shares)):
			remian_shares+=self.incoming_shares[i][1]

		### STAGE 2 -> Unplaned user event handling 
		#print(remian_shares,self.incoming_shares)

		if remian_shares!=0:
			self.unplan_shares_pairing()
		#### STAGE 3 -> MUTUAL PLANS PAIRING #####


		tps = sorted(self.incoming_request, key=lambda dict_key: abs(self.incoming_request[dict_key]))

		#print(tps)

		for i in range(len(tps)):
			if abs(self.incoming_request[tps[i]])>0:
				for j in range(i,len(tps)):
					#if j > i and is opposite sign. 
					if pair_off_test(self.incoming_request[tps[i]], self.incoming_request[tps[j]]):
						self.pair_off(tps[i], tps[j])

		log_print(("pairing sucessful, now remaining request: ",self.ticker,self.incoming_request))

		log_print(("current shares remaning:",self.ticker,sum(self.incoming_request.values())))


		#### STAGE 3 -> IMBALANCE HANDLING #####
		
		remaining_share = sum(self.incoming_request.values())
		self.current_imbalance = remaining_share

		if self.current_imbalance==0:

			self.share_request = False
			self.passive_price = 0
		

		else:

			self.passive_orders()

			# if remaining_share>0:
			# 	self.ppro_out.send([IOCBUY,self.ticker,abs(remaining_share),self.data[ASK]])
			# else:
			# 	self.ppro_out.send([IOCSELL,self.ticker,abs(remaining_share),self.data[BID]])


			## HERE USE PASSIVE ## 
	def passive_orders(self):

		# wait for at least 5 seconds since the last one 

		DELAY = 5

		coefficient = 0.01
		k = self.get_bid()//100
		if k==0: k = 1
		
		gap = (self.get_ask() -self.get_bid())
		midpoint = round((self.get_ask() +self.get_bid())/2,2)

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

	
		order_process = False

		if self.current_imbalance>0:

			action = PASSIVEBUY
			price = self.get_bid()

			if price >= self.passive_price+0.01*k or self.passive_price==0:
				order_process = True


		else:
			action = PASSIVESELL
			price = self.get_ask()

			if price <= self.passive_price -0.01*k or self.passive_price==0:
				order_process = True

		#print(order_process,ts-self.passive_request_ts)

		if order_process and ts > self.passive_request_ts + DELAY:


			total_shares = abs(self.current_imbalance)

			self.passive_request_ts = ts

			#step 1, cancel existing orders
			self.ppro_out.send([CANCEL,self.ticker])
			#step 2, placing around current.
			#time.sleep(0.2)

			if price<=10:
				self.ppro_out.send([action,self.ticker,total_shares,price])
			else:

				if total_shares<=4:
					self.ppro_out.send([action,self.ticker,total_shares,price])
				else:


					share = total_shares//2
					remaning = total_shares-share

					# when big gap, one order on bid, one order on midpoint. 
					if gap>=0.05:
						self.ppro_out.send([action,self.ticker, remaning,price])
						self.ppro_out.send([action,self.ticker,share,midpoint])

					# when tight spread. just one on bid. 
					elif gap<=0.01:
						self.ppro_out.send([action,self.ticker,total_shares,price])
					else:
						self.ppro_out.send([action,self.ticker, remaning,price])
						self.ppro_out.send([action,self.ticker,share,round(price+0.01*k,2)])

					#self.ppro_out.send([PASSIVEBUY,self.ticker,sharer,price-0.01*2*k])

		self.passive_price = price


	def incoming_shares_pairing(self):

		# two ways to go about this.. tp first.. then shares. OR, shares first, then TP. ideally they are equal.in practice ? SHARES FIRST

		paired = []
		for t in range(len(self.incoming_shares)):

			price = self.incoming_shares[t][0]
			share = self.incoming_shares[t][1]

			for tp,val in self.incoming_request.items():

				if share >0 and val>0:
					self.tradingplans[tp].ppro_process_orders(price,abs(share),LONG,self.ticker)

					self.load_confirmation(tp,share)

					self.incoming_request[tp]-=share

					paired.append(t)

					break
				elif share<0 and val<0:
					self.tradingplans[tp].ppro_process_orders(price,abs(share),SHORT,self.ticker)

					self.load_confirmation(tp,share)

					## if share is negative, then minus will add to it. 
					self.incoming_request[tp]-=share
					paired.append(t)

					break

		#log_print(self.ticker,"incoming shares",self.incoming_shares)

		c = 0
		for i in paired:
			self.incoming_shares.pop(i-c)
			c+=1
			# try:
				
			# except Exception as e:
			# 	print(e,"poping failure",e,i,self.incoming_shares)

	def unplan_shares_pairing(self):

		### only viable when there are only 1 plan that currently has holding. i.e. in running state ###
		
		count = 0
		tpname = ""
		for tp,val in self.tradingplans.items():

			if val.data[STATUS] == RUNNING:
				count+=1
				tpname=tp

		if count==1:

			for t in range(len(self.incoming_shares)):
				price = self.incoming_shares[t][0]
				share = self.incoming_shares[t][1]

				if share >0:
					self.tradingplans[tp].ppro_process_orders(price,abs(share),LONG,self.ticker)
				else:
					self.tradingplans[tp].ppro_process_orders(price,abs(share),SHORT,self.ticker)


	def holdings_update(self,price,share):

		self.incoming_shares.append((price,share))

		self.share_request = True
		#print("inc",self.incoming_shares)

	def rejection_message(self,side):

		## iterate through all the TPs request. check who is requesting. if it is not running withdraw and cancel it. 

		if side == "Long":
			coefficient = 1
		elif side =="Short":
			coefficient = -1

		for tp,val in self.incoming_request.items():

			#if val fit. if tp not started but deploy.
			if val*coefficient >0:
				self.tradingplans[tp].rejection_handling()

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

	# def set_mind_object(self):
	# 	try:
	# 		self.mind = self.tradingplan.tkvars[MIND]
	# 		self.mind_label = self.tradingplan.tklabels[MIND]
	# 	except:
	# 		pass

	# def set_tradingplan(self,tradingplan):
	# 	self.tradingplan = tradingplan

	# def set_mind(self,str,color=DEFAULT):

	# 	try:
	# 		if self.mind==None:
	# 			self.set_mind_object()
	# 		if self.mind!=None and self.mind_label !=None:
	# 			self.mind.set(str)
	# 			self.mind_label["background"]=color
	# 	except:
	# 		pass

	# def false_range_detection(self,bid,ask,ts):

	# 	#init
	# 	if self.init_ts==0:
	# 		self.init_ts = ts

	# 	if self.tradingplan.tkvars[STATUS].get()==PENDING:

	# 		if self.seen_low==0 and self.seen_high==0:
	# 			self.seen_low = bid
	# 			self.seen_high = ask
	# 			self.set_mind("FRD: InProgress",DEFAULT)

	# 		if ask>self.seen_high:
	# 			self.seen_high = ask
	# 		if bid<self.seen_low:
	# 			self.seen_low = bid 

	# 		if ts - self.init_ts >=900:
	# 			s = ((self.seen_low-self.data[SUPPORT])/self.data[SUPPORT])
	# 			r =  ((self.data[RESISTENCE]-self.seen_high)/self.seen_high)
	# 			if s>0.004:
	# 				self.set_mind("FRD: abnormal support",YELLOW)
	# 			elif r>0.004:
	# 				self.set_mind("FRD: abnormal resistence",YELLOW)
	# 			elif s>0.004 and r>0.004:
	# 				self.set_mind("FRD: abnormal both levels",YELLOW)
	# 			else:
	# 				self.set_mind("FRD: GOOD",VERYLIGHTGREEN)

	# 		self.last_ts = ts


		#descrepancy. 			


	def update_price(self,bid,ask,ts):

		#print("price",bid,ask,ts)
		if self.data[BID]!= bid and self.data[ASK]!=ask:

			self.data[BID] = bid
			self.data[ASK] = ask
			self.data[TIMESTAMP] = ts

		#update on the tradingplans. 
		#print(self.tradingplans.keys())


		tps = list(self.tradingplans.values())
		for val in tps:
			#print("tp update",tp)
			#print(bid,ask,ts)
			val.ppro_update_price(symbol=self.ticker,bid=bid,ask=ask,ts=ts)


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
# t= {}

# t['a']=0
# t['b']=-1
# t['c']=2
# t['d']=-2
# t['e']=4


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