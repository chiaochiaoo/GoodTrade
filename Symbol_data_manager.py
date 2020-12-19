
from tkinter import *
import numpy as np
from os import path
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
		self.symbol_price_str = {}
		self.symbol_status = {}
		self.symbol_status_color = {}

		self.init_data()


	def init_data(self):

		for i in self.symbols:
			self.init_symbol(i)

	def init_symbol(self,i):
		self.symbol_status[i] = StringVar()
		self.symbol_status_color[i] = StringVar()
		self.symbol_price_str[i] = StringVar()
		self.symbol_price[i] = 0


	def change_status(self,symbol,status):
		self.symbol_status[symbol].set(status)

	def change_status_color(self,symbol,color):
		self.symbol_status_color[symbol].set(color)


	def add(self,symbol):
		self.init_symbol(symbol)
		self.symbols.append(symbol)
		self.save()


	def delete(self,symbol):
		if symbol in self.symbols:
			self.symbols.remove(symbol)
		self.save()

	def save(self):
		np.savetxt('list.txt',self.symbols, delimiter=",", fmt="%s")   
	def get_list(self):
		return self.symbols

	def get_count(self):
		return len(self.symbols)