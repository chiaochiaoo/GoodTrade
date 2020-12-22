
from tkinter import *
import numpy as np
from os import path
import threading
import time
import requests

class Symbol_data_manager:	

	#if file does not exist, create an empty file. 
	def __init__(self):

		if not path.exists("list.txt"):
			self.symbols = []
		else:
			self.symbols = np.array(np.loadtxt('list.txt',dtype="str")).tolist()

			if type(self.symbols) is str:
				self.symbols = [self.symbols]

		print("data initilize:",self.symbols)


		self.reg_symbols = self.symbols[:]
		#These filed need to be initilized. 

		self.symbol_init =[]

		#basics
		self.symbol_price = {}
		self.symbol_price_high = {}
		self.symbol_price_low = {}
		self.symbol_price_open = {}
		self.symbol_price_range = {}
		self.symbol_price_openhigh = {}
		self.symbol_price_openlow = {}

		### Update these upon new ticks 
		self.minute_count = {}
		self.minute_data = {}
		self.minute_timestamp = {}
		self.minute_timestamp_val = {}

		self.last_5_min_range = {}
		self.last_5_min_volume = {}


		self.first_5_list = []
		self.first_5_min_range = {}
		self.first_5_min_volume = {}
		#self.symbol_volume = {}

		self.symbol_status = {}
		self.symbol_status_color = {}
		self.symbol_update_time = {}

		#data

		self.symbol_data_openhigh_range = {}
		self.symbol_data_openlow_range = {}
		self.symbol_data_range_range = {}

		self.symbol_data_openhigh_val = {}
		self.symbol_data_openlow_val = {}
		self.symbol_data_range_val = {}

		self.symbol_data_openhigh_dis = {}
		self.symbol_data_openlow_dis = {}
		self.symbol_data_range_dis = {}

		self.symbol_data_openhigh_std = {}
		self.symbol_data_openlow_std = {}
		self.symbol_data_range_std = {}

		self.symbol_data_first5_range = {}
		self.symbol_data_first5_vol_range = {}

		self.symbol_data_first5_val = {}
		self.symbol_data_first5_vol_val = {}

		self.symbol_data_first5_std = {}
		self.symbol_data_first5_vol_std = {}

		self.symbol_data_first5_dis = {}
		self.symbol_data_first5_vol_dis = {}


		self.symbol_data_normal5_range = {}
		self.symbol_data_normal5_vol_range = {}

		self.symbol_data_normal5_val = {}
		self.symbol_data_normal5_vol_val = {}

		self.symbol_data_normal5_std = {}
		self.symbol_data_normal5_vol_std = {}

		self.symbol_data_normal5_dis = {}
		self.symbol_data_normal5_vol_dis = {}

		self.symbol_data_first5_range_eval = {}
		self.symbol_data_first5_vol_eval = {}

		self.symbol_data_normal5_range_eval = {}
		self.symbol_data_normal5_vol_eval = {}

		self.symbol_data_openhigh_eval = {}
		self.symbol_data_openlow_eval= {}
		self.symbol_data_range_eval = {}


		#alerts
		self.symbol_last_alert = {}
		self.symbol_last_alert_time ={}


		#mark this when a symbol datastructure is completely loaded. 
		self.data_ready = {}

		self.init_data()


	def init_data(self):

		for i in self.symbols:
			self.init_symbol(i)

	def init_symbol(self,i):
		#basic

		self.data_ready[i] = BooleanVar(value=False)
		self.symbol_status[i] = StringVar()
		self.symbol_status_color[i] = StringVar()
		self.symbol_price[i] = DoubleVar()

		self.symbol_price_open[i] = DoubleVar()
		self.symbol_price_range[i] = DoubleVar()
		self.symbol_price_high[i] = DoubleVar()
		self.symbol_price_low[i] = DoubleVar()
		self.symbol_price_openhigh[i] = DoubleVar()
		self.symbol_price_openlow[i] = DoubleVar()

		self.minute_count[i] = 0 
		self.minute_data[i] = {"high":[],"low":[],"vol":[]}
		self.minute_timestamp[i] = []
		self.minute_timestamp_val[i] =DoubleVar()

		self.last_5_min_range[i] = DoubleVar()
		self.last_5_min_volume[i] = DoubleVar()

		self.first_5_min_range[i] = DoubleVar()
		self.first_5_min_volume[i] = DoubleVar()

		self.symbol_update_time[i] = StringVar()

		#data
		self.symbol_data_openhigh_dis[i] = []
		self.symbol_data_openlow_dis[i] = []
		self.symbol_data_range_dis[i] = []

		self.symbol_data_normal5_dis[i]  = []
		self.symbol_data_normal5_vol_dis[i]  = []
		self.symbol_data_first5_dis[i] = []
		self.symbol_data_first5_vol_dis[i] = []

		self.symbol_data_openhigh_range[i] = StringVar()
		self.symbol_data_openlow_range[i] = StringVar()
		self.symbol_data_range_range[i] = StringVar()

		self.symbol_data_openhigh_val[i] = DoubleVar()
		self.symbol_data_openlow_val[i] = DoubleVar()
		self.symbol_data_range_val[i] = DoubleVar()

		self.symbol_data_openhigh_std[i] = DoubleVar()
		self.symbol_data_openlow_std[i] = DoubleVar()
		self.symbol_data_range_std[i] = DoubleVar()

		self.symbol_data_first5_range[i] = StringVar()
		self.symbol_data_first5_vol_range[i] = StringVar()

		self.symbol_data_first5_val[i] = DoubleVar()
		self.symbol_data_first5_vol_val[i] = DoubleVar()

		self.symbol_data_first5_std[i] = DoubleVar()
		self.symbol_data_first5_vol_std[i] = DoubleVar()

		self.symbol_data_normal5_range[i] = StringVar()
		self.symbol_data_normal5_vol_range[i] = StringVar()

		self.symbol_data_normal5_val[i] = DoubleVar()
		self.symbol_data_normal5_vol_val[i] = DoubleVar()

		self.symbol_data_normal5_std[i] = DoubleVar()
		self.symbol_data_normal5_vol_std[i] = DoubleVar()

		#eval

		self.symbol_data_first5_range_eval[i] =  StringVar()
		self.symbol_data_first5_vol_eval[i] = StringVar()

		self.symbol_data_normal5_range_eval[i] =  StringVar()
		self.symbol_data_normal5_vol_eval[i] = StringVar()

		self.symbol_data_openhigh_eval[i] = StringVar()
		self.symbol_data_openlow_eval[i] = StringVar()
		self.symbol_data_range_eval[i] = StringVar()

		#alert
		self.symbol_last_alert[i] = StringVar()
		self.symbol_last_alert_time[i] = StringVar()

		# reg = threading.Thread(target=register,args=(i,), daemon=True)
		# reg.start()

	def change_status(self,symbol,status):
		self.symbol_status[symbol].set(status)

	def change_status_color(self,symbol,color):
		self.symbol_status_color[symbol].set(color)


	def add(self,symbol):
		self.init_symbol(symbol)
		self.symbols.append(symbol)
		self.save()

		print("registering:",symbol)



	def delete(self,symbol):
		if symbol in self.symbols:
			self.symbols.remove(symbol)
		self.save()

		# dereg = threading.Thread(target=deregister,args=(symbol,), daemon=True)
		# dereg.start()

	def save(self):
		np.savetxt('list.txt',self.symbols, delimiter=",", fmt="%s")   
	def get_list(self):
		return self.symbols

	def get_count(self):
		return len(self.symbols)



class price_updater:

	#A big manager. Who has access to all the corresponding grids in the labels. 
	#update each symbols per, 39 seconds? 
	#run every ten seconds. 
	def __init__(self,s: Symbol_data_manager):
		#need to track. 1 min range/ volume. 5 min range/volume.
		#self.depositLabel['text'] = 'change the value'
		#fetch this 
		self.price_list = []
		self.volume_list = []
		self.black_list = []

		self.symbols = s.get_list()

		self.data = s
		self.lock = {}
		self.count = 0

		#Won't need these no more.
		# self.symbols_labels = v.tickers_labels
		# self.symbols_index = v.ticker_index

		#time
		# self.last_update = {}
		# self.last_price = {}

		# self.lowhigh_cur = {}
		# self.openhigh_cur = {}
		# self.openlow_cur = {}

		# self.lowhigh ={}
		# self.openlow ={}
		# self.openhigh = {}

		
		# self.open = {}
		# self.high = {}
		# self.low = {}

		# self.open_high = 0
		# self.high_low = 0
		# self.open_low = 0

		self.init_info()

		#repeat this every 5 seconds.


	def init_info(self):
		for i in self.symbols:
			self.data.change_status(i, "Connecting")

	
	#these three functions together update the prices per second. 
	def start(self):
		print("Console (PT): Thread created, ready to start")
		t1 = threading.Thread(name='Symbol Data Manager updates',target=self.update_info, daemon=True)
		t1.start()
		print("Console (PT): Thread running. Continue:")

	def update_info(self):
		#fetch every 1 minute. ?
		#better do all together. 
		while True:
			#print("symbols:",self.symbols)
			self.count+=1

			print("Current thread count:",threading.active_count())

			for thread in threading.enumerate(): 
				print(thread.name)

			# for i in self.symbols:

			# 	if i not in self.black_list:
	
			# 		fetch = threading.Thread(name='updating'+i,target=self.update_symbol, args=(i,), daemon=True)
			# 		fetch.start()
			time.sleep(5)

	#a single thread 

	def timestamp(self,s):
    
		p = s.split(":")
		try:
			x = int(p[0])*60+int(p[1])
			return x
		except Exception as e:
			print(e)
			return 0

	def update_symbol(self,symbol):

		#get the info. and, update!!!
		if symbol not in self.lock:
			 self.lock[symbol] = False

		if self.lock[symbol]==False:
			self.lock[symbol] = True

			status = self.data.symbol_status[symbol]
			timestatus = self.data.symbol_update_time[symbol]
			price = self.data.symbol_price[symbol]

			open_ = self.data.symbol_price_open[symbol]
			high = self.data.symbol_price_high[symbol]
			low = self.data.symbol_price_low[symbol]
			range_ = self.data.symbol_price_range[symbol]

			oh = self.data.symbol_price_openhigh[symbol]
			ol = self.data.symbol_price_openlow[symbol]


			last_5_range = self.data.last_5_min_range[symbol]
			last_5_vol = self.data.last_5_min_volume[symbol]

			stat,time,midprice,op,high_,low_,vol = getinfo(symbol)

			#I need to make sure that label still exist. 
			#status["text"],timestamp["text"],price["text"]= self.count,self.count,self.count

			if stat != "Connected":
				self.black_list.append(symbol)

			if symbol in self.symbols:
				status.set(stat)

				if stat == "Connected":

					timestatus.set(time)
					timestamp = self.timestamp(time[:5])
					price.set(midprice)

					self.data.minute_timestamp_val[symbol].set(timestamp)

					if timestamp <570:
						if symbol not in self.data.symbol_init:
							self.data.symbol_init.append(symbol)
							low.set(midprice)
							high.set(midprice)

						if midprice<low.get():
							low.set(midprice)

						if midprice>high.get():
							high.set(midprice)

					if timestamp == 570:
						open_.set(op)

					if timestamp >=570:
						high.set(high_)
						low.set(low_)
						rgoh = round(high_ - op,3)
						rgol = round(op - low_,3)
						oh.set(rgoh)
						ol.set(rgol)


					###GENERAL CASE ####

					rg = round(high.get() - low.get(),3)
					range_.set(rg)

					#if timestamp not registered yet.
					if timestamp not in self.data.minute_timestamp[symbol]:
						self.data.minute_timestamp[symbol].append(timestamp)
						self.data.minute_data[symbol]["high"].append(midprice)
						self.data.minute_data[symbol]["low"].append(midprice)
						self.data.minute_data[symbol]["vol"].append(vol)
						self.data.minute_count[symbol] +=1

					#if timestamp already registered. 
					else:
						#update these. 
						idx = self.data.minute_count[symbol]-1
						if midprice >= self.data.minute_data[symbol]["high"][idx]:
							self.data.minute_data[symbol]["high"][idx] = midprice
						if midprice <= self.data.minute_data[symbol]["low"][idx]:
							self.data.minute_data[symbol]["low"][idx] = midprice
						self.data.minute_data[symbol]["vol"][idx] = vol


					#perform an update. 

					#
					l5_h = max(self.data.minute_data[symbol]["high"][-5:])
					l5_l = min(self.data.minute_data[symbol]["low"][-5:])
					l5_r = round(l5_h - l5_l,3)
					index = min(self.data.minute_count[symbol]-1, 5)
					l5_v = round((self.data.minute_data[symbol]["vol"][-1] - self.data.minute_data[symbol]["vol"][-index])/1000,2)

					last_5_range.set(l5_r)
					last_5_vol.set(l5_v)

					#print(symbol,":",time,"vol:",int(vol))

					#check if time stamp is 9:35
					if timestamp <575:
						self.data.first_5_min_range[symbol].set(l5_r)
						self.data.first_5_min_volume[symbol].set(l5_v)



			self.lock[symbol] = False


#Symbol="AAPL.NQ"
# BidPrice="128.710" 
# AskPrice="128.720" 
# BidSize="3460" 
# AskSize="400" 
# Volume="60354388" 
# MinPrice="127.810" 
# MaxPrice="129.580" 
# LowPrice="127.810" 
# HighPrice="129.580" 
# FirstPrice="128.900" 
# OpenPrice="128.900" 
# ClosePrice="127.810" 

# MaxPermittedPrice="0" 
# MinPermittedPrice="0" 
# LotSize="10" 
# LastPrice="128.789"

def getinfo(symbol):
	try:
		p="http://localhost:8080/GetLv1?symbol="+symbol
		r= requests.get(p)
		if(r.text =='<Response><Content>No data available symbol</Content></Response>'):
			print("No symbol found")
			return "Unfound","","","","","",""
		time=find_between(r.text, "MarketTime=\"", "\"")[:-4]
		Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
		Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
		open_ = float(find_between(r.text, "OpenPrice=\"", "\""))
		high = float(find_between(r.text, "HighPrice=\"", "\""))
		low = float(find_between(r.text, "LowPrice=\"", "\""))
		vol = int(find_between(r.text, "Volume=\"", "\""))

		#print(time,price)
		return "Connected",\
				time,\
				round((Bidprice+Askprice)/2,4),\
				open_,\
				high,\
				low,\
				vol


    # p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
    # r= requests.get(p,allow_redirects=False,stream=True)
	except Exception as e:
		print(e)
		return "Disconnected","","","","","",""

def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return data

reg_count = 0

def register(symbol):
	global reg_count
	try:
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		reg_count+=1
		print(symbol,"registerd ","total:",reg_count)
		return True
	except Exception as e:
		print(e)
		return False

def deregister(symbol):
	global reg_count
	try:
		p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		reg_count-=1
		print(symbol,"deregister","total:",reg_count)
		return True
	except Exception as e:
		print(e)
		return False