
from tkinter import *
import numpy as np
from os import path
import threading
import time
import requests
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


		#These filed need to be initilized. 
		self.symbol_price = {}
		self.symbol_status = {}
		self.symbol_status_color = {}

		self.symbol_update_time = {}

		self.init_data()


	def init_data(self):

		for i in self.symbols:
			self.init_symbol(i)

	def init_symbol(self,i):
		self.symbol_status[i] = StringVar()
		self.symbol_status_color[i] = StringVar()
		self.symbol_price[i] = DoubleVar()
		self.symbol_update_time[i] = StringVar()


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

def getinfo(symbol):
	try:
		p="http://localhost:8080/GetLv1?symbol="+symbol
		r= requests.get(p)
		if(r.text =='<Response><Content>No data available symbol</Content></Response>'):
			print("No symbol found")
			return "Unfound","",""
		time=find_between(r.text, "MarketTime=\"", "\"")[:-4]
		Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
		Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
		#print(time,price)
		return "Connected",time,round((Bidprice+Askprice)/2,4)
    # p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
    # r= requests.get(p,allow_redirects=False,stream=True)
	except Exception as e:
		print(e)
		return "Disconnected","",""


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
					status = self.data.symbol_status[i]
					timestamp = self.data.symbol_update_time[i]
					price = self.data.symbol_price[i]
					fetch = threading.Thread(target=self.update_symbol, args=(i,status,timestamp,price,), daemon=True)
					#only start when the last one has returned. 
					fetch.start()
			time.sleep(1)

	#a single thread 
	def update_symbol(self,symbol,status,timestamp,price):

		#get the info. and, update!!!
		if symbol not in self.lock:
			 self.lock[symbol] = False

		if self.lock[symbol]==False:
			self.lock[symbol] = True

			stat,time,midprice = getinfo(symbol)

			#I need to make sure that label still exist. 
			#status["text"],timestamp["text"],price["text"]= self.count,self.count,self.count

			if symbol in self.symbols:
				status.set(stat)
				timestamp.set(time)
				price.set(midprice)


			self.lock[symbol] = False

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