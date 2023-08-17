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



		# self.algo_name = algo_name

		# self.name = algo_name
		# self.symbols = {}

		# self.in_use = True
		# self.pair_plan = False
		
		# self.shut_down = False

		# #self.symbol.set_tradingplan(self)

		# self.manager = Manager

		# self.expect_orders = ""
		# self.flatten_order = False

		# #### BANED SYMBOL

		# self.banned = []

		# # First time its expected is fullfilled. shall the management starts.
		# self.read_lock = {}
		# self.have_request = {}

		# self.expected_shares = {}
		# self.current_shares = {}
		# self.current_request = {}

		# self.current_exposure = {}
		# self.average_price = {}

		# self.stock_price ={}

		# self.recent_action_ts = {}

		# self.data = {}
		# self.tkvars = {}

		# self.tklabels= {} ##returned by UI.

		# self.holdings = {}

		# self.current_price_level = 0

		# self.price_levels = {}

		# self.algo_ui_id = 0

		# self.last_ts = 0
		
		# self.numeric_labels = [ESTRISK,UNREAL,REALIZED,UNREAL_MAX,UNREAL_MIN,WR,MR,TR]

		# self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO]

		# self.bool_labels= [SELECTED]

		# self.display_count = 0

		# self.init_data(risk)

	def submit_expected_pair(self,amount,passive,ta):

		self.symbols[self.symbol2].turn_on_aggresive_only()

		if ta==0:
			if passive:
				self.submit_expected_shares(self.symbol1,amount*self.ratio[0],False)
			else:
				self.submit_expected_shares(self.symbol1,amount*self.ratio[0],True)
		else:
			#symbol,shares,time_takes,aggresive
			self.submit_incremental_expected(self.symbol1,amount*self.ratio[0],ta,passive)

	def notify_holding_change(self,symbol):

		if symbol == self.symbol1:
			# get expected on the other side .
			self.expected_shares[self.symbol2] = ((self.current_shares[self.symbol1])//self.ratio[0])*self.ratio[1]

			self.submit_expected_shares(self.symbol2,self.expected_shares[self.symbol2],1) 
			# if self.expected_shares[self.symbol1]==0:
			# 	self.submit_expected_shares(self.symbol2,0,1) 
			# else:
			# 	self.expected_shares[self.symbol2] = ((self.current_shares[self.symbol1])//self.ratio[0])*self.ratio[1]

			# 	self.submit_expected_shares(self.symbol2,self.expected_shares[self.symbol2],1) 


