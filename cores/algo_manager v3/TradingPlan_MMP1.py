from Symbol import *
from Triggers import *
from Strategy import *
from Strategy_Management import *
from constant import*
from Util_functions import *
import tkinter as tkvars
import time
import threading
import random
from TradingPlan import *
# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan_MMP1(TradingPlan):

	def __init__(self,name:"",symbol:Symbol,entry_plan=None,manage_plan=None,support=0,resistence=0,risk=None,TEST_MODE=False,algo_name="",Manager=None):


		super().__init__("MMP1"+name,symbol,entry_plan,manage_plan,support,resistence,risk,TEST_MODE,algo_name,Manager)

		self.ppro_out = symbol.ppro_out
		self.imbalance = 0
		self.market_making_go = True

	def ppro_update_price(self,symbol="",bid=0,ask=0,ts=0):

		#if self.data[POSITION]!="":
			#self.check_pnl(bid,ask,ts)
		# if overall down risk $. get out.

		if self.market_making_go:
			self.ppro_out.send([CANCEL,self.symbol_name])
			self.ppro_out.send([PASSIVESELL,self.symbol_name,5,0])
			self.ppro_out.send([PASSIVEBUY,self.symbol_name,5,0])


			if abs(self.current_shares)!=0:

				if self.current_shares>0:
					self.ppro_out.send([IOCSELL,self.symbol_name,self.imbalance,0])
				else:
					self.ppro_out.send([IOCBUY,self.symbol_name,self.imbalance,0])

	def orders_out(self):
		pass

	def ppro_process_orders(self,price,shares,side,symbol):

		for i in range(shares):
			self.holdings.append(price)


		if side == LONG:
			self.current_shares += shares
		else:
			self.current_shares -= shares

		# count realized

		diff = len(self.holdings) - self.current_shares


		if diff!=0:

			self.data[REALIZED]+= sum(self.holdings[self.current_shares:])
			self.data[REALIZED]= round(self.data[REALIZED],3)

			self.holdings = self.holdings[:self.current_shares]

		else:

			self.imbalance = abs(self.current_shares)


		if self.data[REALIZED] <= -self.data[ESTRISK]:

			self.market_making_go = False
			self.manager.new_record(self)

			self.clear_trade()
			log_print(self.symbol_name,"Trade completed."," this trade:",self.data[REALIZED]," total:",self.data[TOTAL_REALIZED])



		self.update_displays()

	def deploy(self,risktimer=0):

		if self.tkvars[STATUS].get() ==PENDING:


			self.tkvars[STATUS].set(RUNNING)
			self.symbol.register_tradingplan(self.name,self)
			self.symbol.turn_market_making(self)

			self.activate()
			self.flatten_order	 = False

			# entryplan=self.tkvars[ENTRYPLAN].get()

			# entrytimer=int(self.tkvars[TIMER].get())
			# manage_plan =self.tkvars[MANAGEMENTPLAN].get()

			# if risktimer ==0:
			# 	self.data[RISKTIMER] = int(self.tkvars[RISKTIMER].get())
			# else:
			# 	self.data[RISKTIMER] = risktimer

			# self.data[RISK_PER_SHARE] = abs(self.symbol.get_resistence()-self.symbol.get_support())

			# self.set_mind("",DEFAULT)
			# self.entry_plan_decoder(entryplan, entrytimer)
			# self.manage_plan_decoder(manage_plan)

			# self.start_tradingplan()

			# if self.AR_toggle_check():
			# 	try:
			# 		log_print("Deploying:",self.symbol_name,self.entry_plan.get_name(),self.symbol.get_support(),self.symbol.get_resistence(),entry_type,entrytimer,self.management_plan.get_name(),"risk:",self.data[ESTRISK],"risk timer:",self.data[RISKTIMER],"reload:",self.data[RELOAD_TIMES],"rps",self.data[RISK_PER_SHARE])
			# 	except:
			# 		pass
			# 	self.start_tradingplan()

			# except Exception as e:

			# 	log_print("Deplying Error:",self.symbol_name,e)


	def flatten_cmd(self):
		
		if self.tkvars[STATUS].get()==PENDING:
			self.cancel_algo()
		else:
			self.market_making_go = False
			self.flatten_order=True
			self.symbol.flatten_cmd(self.name)