from Symbol import *

#from Triggers import *
# from Strategy import *
# from Strategy_Management import *
from constant import*
from Util_functions import *
import tkinter as tkvars
import time
import threading
import random
from datetime import datetime, timedelta
from TradingPlan_Basket import *
# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan_AMM(TradingPlan_Basket):

	#symbols:Symbols,risk=None

	# This does one thing.
	# On CORE SYMBOL FILL,
	# ALL SUBSEQUET SYMBOLS MATCH UP TO IT.
	# THAT IT. 

	def __init__(self,algo_name="",risk=5,Manager=None,info=None):

		super().__init__(algo_name,risk,Manager)

		log_print("TP working AMM",info)
		self.source = "TP AMM: "

		self.ratio = {}

		self.current_coefficient = 1
		self.core_symbol = ''

		self.info = info


		self.aggresive= False 
		if 'AGGRESIVE' in info:
			self.aggresive = True

	def register_core_symbol(self,symbol):

		self.core_symbol = symbol

		try:
			maxlot = int(abs(self.info["MAX"]))

			minlot = int(abs(self.info["MIN"]))

			interval = int(self.info['INTERVAL'])

			self.symbols[self.core_symbol].set_limits(maxlot,minlot,interval)

			if self.aggresive ==True:
				self.symbols[self.core_symbol].flop_mode = False 
		except Exception as e:
			PrintException(e," AMM fail")


	def submit_core_share(self,symbol,share):

		self.current_shares[symbol] = share
		self.expected_shares[symbol] = share
		### calc if all other are correct. 

		self.current_coefficient = share/self.ratio[self.core_symbol]

		# use the ratio to update all else. 

		log_print(self.source," core share update:",share, " current pair:",self.current_coefficient,self.ratio)
		for symbol,share in self.ratio.items():

			if symbol != self.core_symbol:

				if self.current_coefficient==0:
					self.submit_expected_shares(symbol,0,False)
				else:
					self.submit_expected_shares(symbol,int(share*self.current_coefficient),self.aggresive)

		log_print(self.source,"core share update:",self.current_shares[self.core_symbol],self.current_coefficient,'expect: ',self.expected_shares,' current:',self.current_shares)

	def get_homeo(self):

		for symbol,share in self.current_shares.items():

			self.recalculate_current_request(symbol)

			if self.current_request[symbol]!=0:
				log_print(self.source	," homeo: false",symbol,self.current_request[symbol])
				return False 


		return True 
	def update_ratio(self,symbol,share):

		self.ratio[symbol] = share

		if symbol == self.core_symbol:
			self.symbols[self.core_symbol].update_standard_lot(share)


	def notify_holding_change(self,symbol):

		if symbol == self.core_symbol and self.flatten_order!=True:
			# get expected on the other side .
			for symbol,share in self.ratio.items():

				if symbol != self.core_symbol:
					self.submit_expected_shares(symbol,int(share*self.current_coefficient),True)

			log_print(self.source,"Update:",self.source,self.expected_shares)

	def flatten_cmd(self):
		
		# turn the core 


		self.symbols[self.core_symbol].flatten_mode = True 
		self.flatten_order=True
		log_print(self.source,self.algo_name,self.core_symbol," flattening, aggresive:",self.aggresive_exit)

		# for symbol,item in self.symbols.items():
		# 	self.submit_expected_shares(symbol,0,self.aggresive_exit)
		# 	self.expected_shares[symbol] = 0
		# 	self.recalculate_current_request(symbol)
		# self.tkvars[ALGO_MULTIPLIER].set(0)
		# self.flatten_order=True