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

class TradingPlan_Pair(TradingPlan_Basket):

	#symbols:Symbols,risk=None

	def __init__(self,algo_name="",risk=5,Manager=None,infos=None):

		super().__init__(algo_name,risk,Manager)

		log_print("TP working?")
		self.source = "TP Pair: "

		self.symbol1 = infos['symbol1']
		self.symbol2 = infos['symbol2']

		self.ratio = infos['ratio']

		self.clone_able = False


	def submit_expected_pair(self,amount,passive,ta):

		self.symbols[self.symbol2].turn_on_aggresive_only()

		if ta<=30:
			if passive:
				self.submit_expected_shares(self.symbol1,amount*self.ratio[0],False)
			else:
				self.submit_expected_shares(self.symbol1,amount*self.ratio[0],True)
		else:
			#symbol,shares,time_takes,aggresive
			self.submit_incremental_expected(self.symbol1,amount*self.ratio[0],ta,passive)

	def notify_holding_change(self,symbol):

		if symbol == self.symbol1 and self.flatten_order!=True:
			# get expected on the other side .
			self.expected_shares[self.symbol2] = ((self.current_shares[self.symbol1])//self.ratio[0])*self.ratio[1]

			self.submit_expected_shares(self.symbol2,self.expected_shares[self.symbol2],1) 
