
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

		#basics
		self.symbol_price = {}
		self.symbol_price_high = {}
		self.symbol_price_low = {}
		self.symbol_price_open = {}
		self.symbol_price_range = {}

		self.symbol_price_openhigh = {}
		self.symbol_price_openlow = {}

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

		self.symbol_update_time[i] = StringVar()

		#data
		self.symbol_data_openhigh_dis[i] = []
		self.symbol_data_openlow_dis[i] = []
		self.symbol_data_range_dis[i] = []

		self.symbol_data_openhigh_range[i] = StringVar()
		self.symbol_data_openlow_range[i] = StringVar()
		self.symbol_data_range_range[i] = StringVar()

		self.symbol_data_openhigh_val[i] = DoubleVar()
		self.symbol_data_openlow_val[i] = DoubleVar()
		self.symbol_data_range_val[i] = DoubleVar()

		self.symbol_data_openhigh_std[i] = DoubleVar()
		self.symbol_data_openlow_std[i] = DoubleVar()
		self.symbol_data_range_std[i] = DoubleVar()

		#eval
		self.symbol_data_openhigh_eval[i] = StringVar()
		self.symbol_data_openlow_eval[i] = StringVar()
		self.symbol_data_range_eval[i] = StringVar()

		#alert
		self.symbol_last_alert[i] = StringVar()
		self.symbol_last_alert_time[i] = StringVar()


	# def data_request(self,symbol):


	def change_status(self,symbol,status):
		self.symbol_status[symbol].set(status)

	def change_status_color(self,symbol,color):
		self.symbol_status_color[symbol].set(color)


	def add(self,symbol):
		self.init_symbol(symbol)
		self.symbols.append(symbol)
		self.save()

		reg = threading.Thread(target=register,args=(symbol,), daemon=True)
		reg.start()


	def delete(self,symbol):
		if symbol in self.symbols:
			self.symbols.remove(symbol)
		self.save()

		dereg = threading.Thread(target=deregister,args=(symbol,), daemon=True)
		dereg.start()

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
		t1 = threading.Thread(target=self.update_info, daemon=True)
		t1.start()
		print("Console (PT): Thread running. Continue:")

	def update_info(self):
		#fetch every 1 minute. ?
		#better do all together. 
		while True:
			#print("symbols:",self.symbols)
			self.count+=1
			for i in self.symbols:

				if i not in self.black_list:
					status = self.data.symbol_status[i]
					timestamp = self.data.symbol_update_time[i]
					price = self.data.symbol_price[i]

					open_ = self.data.symbol_price_open[i]
					high = self.data.symbol_price_high[i]
					low = self.data.symbol_price_low[i]
					range_ = self.data.symbol_price_range[i]

					oh = self.data.symbol_price_openhigh[i]
					ol = self.data.symbol_price_openlow[i]

					fetch = threading.Thread(target=self.update_symbol, args=(i,status,timestamp,price,open_,high,low,range_,oh,ol), daemon=True)
					#only start when the last one has returned. 
					fetch.start()
			time.sleep(1)

	#a single thread 
	def update_symbol(self,symbol,status,timestamp,price,open_,high,low,range_,oh,ol):

		#get the info. and, update!!!
		if symbol not in self.lock:
			 self.lock[symbol] = False

		if self.lock[symbol]==False:
			self.lock[symbol] = True

			stat,time,midprice,op,hp,lp,rg,rgoh,rgol = getinfo(symbol)

			#I need to make sure that label still exist. 
			#status["text"],timestamp["text"],price["text"]= self.count,self.count,self.count

			if stat != "Connected":
				self.black_list.append(symbol)

			if symbol in self.symbols:
				status.set(stat)
				timestamp.set(time)
				price.set(midprice)
				open_.set(op)
				high.set(hp)
				low.set(lp)
				range_.set(rg)

				oh.set(rgoh)
				ol.set(rgol)


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
			return "Unfound","","","","","","","",""
		time=find_between(r.text, "MarketTime=\"", "\"")[:-4]
		Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
		Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
		open_ = float(find_between(r.text, "OpenPrice=\"", "\""))
		high_ = float(find_between(r.text, "HighPrice=\"", "\""))
		low_ =float(find_between(r.text, "LowPrice=\"", "\""))
		range_ = round(high_-low_,4)
		rgoh = round(high_-open_,4)
		rgol = round(open_-low_,4)
		#print(time,price)
		return "Connected",\
				time,\
				round((Bidprice+Askprice)/2,4),\
				open_,\
				high_,\
				low_,\
				range_,\
				rgoh,\
				rgol


    # p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
    # r= requests.get(p,allow_redirects=False,stream=True)
	except Exception as e:
		print(e)
		return "Disconnected","","","","","","","",""

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