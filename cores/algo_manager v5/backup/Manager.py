from pannel import *
from tkinter import ttk
import tkinter as tk 
from Symbol import *

from TradingPlan_Basket import *
from TradingPlan_Pair import *

from UI import *
from Ppro_in import *
from Ppro_out import *
from constant import *
#from TNV_http import *	

import os

import random
# from BackTester import *

from Util_functions import *
import sys
import socket
import pickle
import time
import multiprocessing
import requests
import select
from datetime import datetime, timedelta
import json
import os,sys
import csv
import pandas as pd 
import numpy as np

import os 
import json

# from Tester import *
from httpserver import *
from psutil import process_iter
import psutil

try:
	import psutil
except ImportError:
	import pip
	pip.main(['install', 'psutil'])
	import psutil

#May this class bless by the Deus Mechanicus.

try:
	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+".txt", "x")
except:
	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+".txt", "w")
f.close()



TEST = True



def request(post):
	#print("sending ",post)
	try:
		requests.get(post)
	except:
		print(symbol, "failed")





class Manager:

	def __init__(self,root,goodtrade_pipe=None,ppro_out=None,ppro_in=None,TEST_MODE=False,processes=[]):


		self.total_difference = 0
		self.root = root

		self.termination = False

		self.pipe_ppro_in = ppro_in
		self.pipe_ppro_out = ppro_out
		self.pipe_goodtrade = goodtrade_pipe

		self.test_mode = TEST_MODE

		self.symbols = []
		self.symbols_short = {}
		self.symbol_data = {}

		self.baskets = {}

		self.bad_symbols = []

		self.processes = processes
	
		self.algo_ids = []

		self.manage_lock = 0

		self.algo_limit = 100

		""" POSITION DATA """

		# no need to use lock. everytime need to read. just obtain copy. 
		self.current_positions = {} #for 

		self.current_summary = {}
		self.current_summary['net'] = tk.DoubleVar()
		self.current_summary['fees'] = tk.DoubleVar()
		self.current_summary['trades'] = tk.DoubleVar()
		self.current_summary['sizeTraded'] = tk.DoubleVar()
		self.current_summary['unrealizedPlusNet'] = tk.DoubleVar()
		self.current_summary['timestamp'] = tk.StringVar()
		self.current_summary['unrealized'] = tk.DoubleVar()	
		self.current_summary['cur_exp'] = tk.StringVar()
		self.current_summary['max_exp'] = tk.StringVar()

		self.user = tk.StringVar(value="User:")

		""" UI """
		self.receiving_signals = tk.BooleanVar(value=True)
		self.cmd_text = tk.StringVar(value="Status:")


		self.ta_moc = tk.BooleanVar(value=1)

		self.ui = UI(root,self,self.receiving_signals,self.cmd_text)

		m=self.receiving_signals.trace('w', lambda *_: self.receiving())


		""" STATISTICS """

		self.active_trade = 0
		self.active_trade_max = 0

		self.total_u = 0
		self.total_u_max = 0
		self.total_u_min = 0
		self.total_r = 0
		self.total_r_max =0
		self.total_r_min = 0

		self.set_risk = 500


		self.net = 0
		self.net_max = 0
		self.net_min = 0

		self.max_risk = 0

		self.current_total_risk = 0
		self.current_downside = 0
		self.current_upside = 0

		self.current_downside_max = 0
		self.u_winning = 0
		self.u_winning_min = 0
		self.u_winning_max = 0

		self.u_losing = 0
		self.u_losing_min = 0
		self.u_losing_max = 0


		#### EXPOSURE ADJUSTING #####

		self.long_exposure = 0
		self.short_exposure = 0
		self.delta_spx = 0

		#############################

		now = datetime.now()
		self.file = "../../algo_records/"+now.strftime("%Y-%m-%d")+".json"

		# this is today's 

		try:
			with open(self.file) as f:
				self.record = json.load(f)
		except Exception as e:
			self.record = {}
			self.record["total"] = {}
			self.record["algos"] = {}
			self.record["detes"] = {}

		#self.init_record_writer()
		self.load_record()
		
		self.weekly_record = self.take_records(5)
		self.monthly_record = self.take_records(20)
		self.total_record = self.take_records(200)

		self.gateway = 0

		######

		self.get_price_lock = threading.Lock()
		######
		self.moo_orders = {}
		self.moo_algos = []
		self.moo_lock = threading.Lock()

		#print(self.total_record)
		self.shutdown=False
		self.symbol_inspection_lock = threading.Lock()
		self.symbol_inspection_start = False
		# handl = threading.Thread(target=self.symbols_inspection,daemon=True)
		# handl.start()

		good = threading.Thread(target=self.goodtrade_in, daemon=True)
		good.start()
		
		ppro_in = threading.Thread(target=self.ppro_in, daemon=True)
		ppro_in.start()

		timer = threading.Thread(target=self.timer, daemon=True)
		timer.start()

		self.pipe_ppro_out.send(["Register","QQQ.NQ"])
		# self.pipe_ppro_out.send(["Register","SPY.AM"])
		#self.pipe_ppro_out.send(["Register","SQQQ.NQ"])

		#self.apply_basket_cmd("OB1",{"SPY":1,},1,1)
#
	#data part, UI part

	def shutdown_all_threads(self):

		self.shutdown= True

	def submit_badsymbol(self):


		symbol = self.ui.bad_symbol.get()

		self.bad_symbols.append(symbol)


		if symbol in self.symbol_data:

			log_print("baning symbol",symbol)
			self.symbol_data[symbol].rejection_message("Long")
			self.symbol_data[symbol].rejection_message("Short")


		self.symbol_data[symbol].cancel_all()
		
	def set_risk(self,risk_):

		log_print("Manager Updating Risk:",risk_)
		self.set_risk = int(risk_)


	def check_all_pnl(self):
		tps = list(self.baskets.keys())
		for tp in tps:
			self.baskets[tp].check_pnl()


	def set_gateway(self):

		if self.ui.gateway.get()=="MEMX":
			self.gateway = 0
			self.ui.set_gateway["text"] = "Set Change:MEMX"

		elif  self.ui.gateway.get()=="ARCA":

			self.gateway = 1
			self.ui.set_gateway["text"] = "Set Change:ARCA"

		elif  self.ui.gateway.get()=="BATS":

			self.gateway = 2
			self.ui.set_gateway["text"] = "Set Change:BATS"
		elif  self.ui.gateway.get()=="EDGA":

			self.gateway = 3
			self.ui.set_gateway["text"] = "Set Change:EDGA"

	def symbols_inspection(self):

		# HERE I NEED. A. HARD LIMIT.... 40 ??? 
		if self.symbol_inspection_lock.locked()==False:

			# if self.total_difference !=0:
			# 	self.pipe_ppro_out.send([CANCELALL])

			# self.total_difference = 0
			time.sleep(0.5)
			# residue.
			# if residue is 0. no more cancel. 
			with self.symbol_inspection_lock:
				symbols = list(self.symbol_data.values())
				c= 0
				for val in symbols:

					try:
						c+=val.symbol_inspection()
						#self.total_difference+=abs(val.get_difference())
						if c>=30:
							break
							log_print("ORDERING LIMIT REACHED.")
					except Exception as e:
						PrintException(e,"inspection error")

				self.total_difference = c 

			log_print("Manager: performing symbols inspection compelte, total difference:",self.total_difference, "order counts:",c)
		else:
			log_print("Manager: previous symbols inspection not finished. skip.")




	def moo_apply_basket_cmd(self,basket_name,orders,risk,aggresive,info):

		if basket_name not in self.baskets:

			if self.ui.basket_label_count<self.algo_limit:
				self.baskets[basket_name] = TradingPlan_Basket(basket_name,risk,self,info)
				self.ui.create_new_single_entry(self.baskets[basket_name],"Basket",None)

				self.baskets[basket_name].deploy()
		
				c = 0 

				total_orders = {}

				with self.moo_lock:
					for symbol,share in orders.items():
						
						if symbol not in self.moo_orders:
							self.moo_orders[symbol] = share 
						else:
							self.moo_orders[symbol] += share 

					self.moo_algos.append([basket_name,orders,risk,aggresive,info])

				for symbol,value in orders.items():
					if symbol not in self.symbol_data:
						self.symbol_data[symbol] = Symbol(self,symbol,self.pipe_ppro_out)  #register in Symbol.
						self.symbols.append(symbol)
						self.symbols_short[symbol[:-3]] = symbol

					self.baskets[basket_name].register_symbol(symbol,self.symbol_data[symbol])


	def apply_pair_cmd(self,d):

		pair = d['pair'] 
		# d['symbol1'] 
		# d['symbol2']
		# d['amount'] 
		# d['ratio'] 
		# d['passive'] 
		log_print("Pair applying:",d)
		risk=10
	
		if pair not in self.baskets:

			if self.ui.basket_label_count<self.algo_limit:
				self.baskets[pair] = TradingPlan_Pair(pair,risk,self,d)
				self.ui.create_new_single_entry(self.baskets[pair],"Basket",None)

				self.baskets[pair].deploy()
		

		if self.baskets[pair].shut_down==False:

			if d['symbol1'] not in self.bad_symbols and d['symbol2'] not in self.bad_symbols:
			

				if d['symbol1']  not in self.symbol_data:
					self.symbol_data[d['symbol1']] = Symbol(self,d['symbol1'],self.pipe_ppro_out)  #register in Symbol.
					self.symbols.append(d['symbol1'])
					self.symbols_short[d['symbol1'][:-3]] = d['symbol1']

				self.baskets[pair].register_symbol(d['symbol1'],self.symbol_data[d['symbol1']])

				if d['symbol2']  not in self.symbol_data:
					self.symbol_data[d['symbol2']] = Symbol(self,d['symbol2'],self.pipe_ppro_out)  #register in Symbol.
					self.symbols.append(d['symbol2'])
					self.symbols_short[d['symbol2'][:-3]] = d['symbol2']

				self.baskets[pair].register_symbol(d['symbol2'],self.symbol_data[d['symbol2']])

				## now , submit the request.


				self.baskets[pair].submit_expected_pair(d['amount'],d['passive'])

				## INSTANT INSPECTION if passive.
				if d['passive']:
					self.symbol_data[d['symbol1']].symbol_inspection()

					self.total_difference+=1
			else:
				log_print("Manager: Wrong Ticker format or BANNED:",d)
		else:
			log_print(d,"already shutdown")

	def apply_basket_cmd(self,basket_name,orders,risk,aggresive,info):

		if basket_name not in self.baskets:

			if self.ui.basket_label_count<self.algo_limit:
				self.baskets[basket_name] = TradingPlan_Basket(basket_name,risk,self,info)
				self.ui.create_new_single_entry(self.baskets[basket_name],"Basket",None)

				self.baskets[basket_name].deploy()
		

		if self.baskets[basket_name].shut_down==False:
			for symbol,value in orders.items():

				if "." in symbol and symbol not in self.bad_symbols:

				
					log_print("Manager: Applying basket command",symbol,value)
					if symbol not in self.symbol_data:
						self.symbol_data[symbol] = Symbol(self,symbol,self.pipe_ppro_out)  #register in Symbol.
						self.symbols.append(symbol)
						self.symbols_short[symbol[:-3]] = symbol

					self.baskets[basket_name].register_symbol(symbol,self.symbol_data[symbol])

					## now , submit the request.

					self.baskets[basket_name].submit_expected_shares(symbol,value,aggresive)
				else:
					log_print("Manager: Wrong Ticker format or BANNED:",symbol)
		else:
			log_print(basket_name,"already shutdown")



	def timer(self):

		moo_release = False 
		pair_release = False 
		moc_release = False 
		moc_pair_release = False


		premarket_timer_start = 350*60
		premarket_timer_stop = 550 *60

		MOO_send_out_timer = 565*60
		MOO_pairing_timer = 571*60

		MOC_send_out_timer = 958*60+30 #958*60+50
		MOC_pairing_timer = 959*60+30

		c = 0 
		log_print("Timer: functional and counting")
		while True:
			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second

			if ts>premarket_timer_start and ts<premarket_timer_stop:
				self.symbol_inspection_start = True 

			if ts>=MOO_send_out_timer and moo_release==False :
				### TRIGGER. Realese the moo orders. 
				self.symbol_inspection_start = False 
				log_print("Timer: timer triggered for MOO",self.moo_orders)
				with self.moo_lock:
					for symbol,share in self.moo_orders.items():
						
						share = int(share)
						print("sending",symbol,share)
						if share<0:
							if c%2==0:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Sell->Short%20ARCX%20MOO%20OnOpen&shares="+str(abs(share))
							else:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=NSDQ Sell->Short NSDQ MOO Regular OnOpen&shares="+str(abs(share))
						else:
							if c%2==0:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Buy%20ARCX%20MOO%20OnOpen&shares="+str(share)
							else:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=NSDQ Buy NSDQ MOO Regular OnOpen&shares="+str(share)
						c+=1 


						with self.symbol_inspection_lock:
							for i in self.moo_algos:
								basket_name,orders,risk,aggresive,info = i[0],i[1],i[2],i[3],i[4]
								self.apply_basket_cmd(basket_name,orders,risk,aggresive,info)

						
						req = threading.Thread(target=request, args=(reque,),daemon=True)
						req.start()

				moo_release = True


				### PRE RELEASE. 

				for basket,item in self.baskets.items():
					if basket[:3]=="PRE":
						for symbol,share in item.current_shares.items():	
							if share<0:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Buy%20ARCX%20MOO%20OnOpen&shares="+str(share)
							else:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Sell->Short%20ARCX%20MOO%20OnOpen&shares="+str(abs(share))
								
							req = threading.Thread(target=request, args=(reque,),daemon=True)
							req.start()

						#flat and then shut down. 
						item.flatten_cmd()
						item.shutdown()

			if ts>=MOO_pairing_timer and pair_release==False :

				log_print("Timer: pair realease complelte")

				pair_release=True 
 

				self.symbol_inspection_start = True
				time.sleep(5)
				### TRIGGER. PAIR UP the algos.

			if ts>=MOC_send_out_timer and moc_release==False:

				########################################################################################################################
				############### ROSN Buy RosenblattDQuoteClose MOC DAY             #####################################################
				############### ROSN Sell->Short RosenblattDQuoteClose MOC DAY     #####################################################
				########################################################################################################################

				### DO A LAST INSPECTION 

				self.symbols_inspection()

				self.symbol_inspection_start = False

				if self.ta_moc.get()==True:

					log_print("Timer: TA-MOC begins")
					

					with self.symbol_inspection_lock: 

						for ticker in self.current_positions.keys():
							share = self.current_positions[ticker][1]

							if ticker[-2:]=="NY":
								if share<0:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ROSN Buy RosenblattDQuoteClose MOC DAY&shares="+str(abs(share))
								else:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ROSN Sell->Short RosenblattDQuoteClose MOC DAY&shares="+str(share)
							else:
								if share<0:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Buy ARCX MOC DAY&shares="+str(abs(share))
								else:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Sell->Short ARCX MOC DAY&shares="+str(share)

							log_print("Sending" ,reque)
							req = threading.Thread(target=request, args=(reque,),daemon=True)
							req.start()

					moc_release=True

				else:
					log_print("Timer: MOC begins")


					with self.symbol_inspection_lock: 

						for ticker in self.current_positions.keys():
							share = self.current_positions[ticker][1]


							if ticker[-2:]=="NY":
								if share<0:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ROSN Buy RosenblattDQuoteClose MOC DAY&shares="+str(abs(share))
								else:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ROSN Sell->Short RosenblattDQuoteClose MOC DAY&shares="+str(share)
							else:
								if share<0:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Buy ARCX MOC DAY&shares="+str(abs(share))
								else:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Sell->Short ARCX MOC DAY&shares="+str(share)

							log_print("Sending" ,reque)
							req = threading.Thread(target=request, args=(reque,),daemon=True)
							req.start()

					moc_release=True

			if ts>MOC_pairing_timer and moc_pair_release==False:

				#every tp's symbol no clear.
				log_print("last paring.")
				for name,basket in self.baskets.items():
					basket.flatten_cmd()

				moc_pair_release=True

			time.sleep(20)

		log_print("Timer: completed")

	def update_stats(self):

		self.active_trade = 0
		self.total_u = 0
		self.total_r = 0
		self.max_risk = 0
		self.current_total_risk = 0
		self.current_downside = 0
		self.current_upside = 0

		############# added ###############

		self.u_winning = 0
		self.u_losing = 0

		for trade in list(self.baskets.values()):

			if trade.data[STATUS] == RUNNING:
				self.active_trade +=1 

			self.total_u += trade.data[UNREAL]

			if trade.data[UNREAL]>0:
				self.u_winning +=  trade.data[UNREAL]
			else:
				self.u_losing +=  trade.data[UNREAL]


			self.total_r += trade.data[TOTAL_REALIZED]

			self.current_total_risk +=  trade.data[ACTRISK]

			if trade.data[ACTRISK]>0:
				self.current_downside +=  trade.data[ACTRISK]
			else:
				self.current_upside +=  trade.data[ACTRISK]




		if self.active_trade > self.active_trade_max:
			self.active_trade_max = self.active_trade


		# net 

		self.net = self.total_u + self.total_r


		if self.net > self.net_max:
			self.net_max = self.net
			
		if self.net < self.net_min:
			self.net_min = self.net	


		if self.total_u > self.total_u_max:
			self.total_u_max = self.total_u

		if self.total_u < self.total_u_min:
			self.total_u_min = self.total_u

		if self.total_r > self.total_r_max:
			self.total_r_max = self.total_r

		if self.total_r < self.total_r_min:
			self.total_r_min = self.total_r
		# winning

		if self.u_winning > self.u_winning_max:
			self.u_winning_max = self.u_winning
			
		if self.u_losing < self.u_losing_max:
			self.u_losing_max = self.u_losing	

		if self.current_downside > self.current_downside_max:
			self.current_downside_max = self.current_downside



		if self.current_downside > self.max_risk:
			self.max_risk = self.current_downside

		self.ui.active_trade.set(self.active_trade)  
		self.ui.active_trade_max.set(self.active_trade_max)  

		self.ui.net.set(round(self.net,1))
		self.ui.net_min.set(round(self.net_min,1))
		self.ui.net_max.set(round(self.net_max,1))


		self.ui.u_winning.set(round(self.u_winning,1))
		self.ui.u_winning_max.set(round(self.u_winning_max,1))

		self.ui.u_losing.set(round(self.u_losing,1))
		self.ui.u_losing_max.set(round(self.u_losing_max,1))

		self.ui.total_u.set(round(self.total_u,1))  
		self.ui.total_u_max.set(round(self.total_u_max,1))  
		self.ui.total_u_min.set(round(self.total_u_min,1))  
		self.ui.total_r.set(round(self.total_r,1))  
		self.ui.total_r_max.set(round(self.total_r_max,1))  	
		self.ui.total_r_min.set(round(self.total_r_min,1))  

		self.ui.max_risk.set(int(self.max_risk))  

		self.ui.current_total_risk.set(int(self.current_total_risk))  
		self.ui.current_downside.set(int(self.current_downside))  
		self.ui.current_upside.set(int(-self.current_upside))  

	def receiving(self):

		if self.receiving_signals.get():
			self.ui.receiving_algo["background"] = "#97FEA8"
		else:
			self.ui.receiving_algo["background"] = "red"

	def goodtrade_in(self):
		time.sleep(3)
		count = 0
		while True:
			d = self.pipe_goodtrade.recv()
			#print("GT:",d,d[0])
			if d[0] =="msg":
				try:
					self.ui.main_app_status.set(str(d[1]))
					if str(d[1])=="Connected":
						self.termination = True
						self.ui.main_status["background"] = "#97FEA8"
					else:
						self.termination = False
						self.ui.main_status["background"] = "red"
				except Exception as e:
					PrintException(e,"msg error")

			elif d[0] =="cmd":

				log_print("cmd received:",d)

			elif d[0] =="basket":

				try:
					#d[1]   => basket name 
					#d[2]   => share info. 
					#print(d[1],d[2],d[3],d[4])
					now = datetime.now()
					cur_ts = now.hour*3600+now.minute*60+now.second

					confirmation,orders,risk,aggresive,multiplier = self.ui.order_confirmation(d[1],d[2])

					info = d[3]

					if self.net > self.set_risk*-1:
						if confirmation:
							log_print("basket update:",d)
							log_print(d[1],confirmation,orders,risk,aggresive)
							if "OB" in d[1] and cur_ts<570*60:
								handl = threading.Thread(target=self.moo_apply_basket_cmd,args=(d[1],orders,risk,aggresive,info,),daemon=True)
								handl.start()
								#self.moo_apply_basket_cmd(d[1],orders,risk,aggresive)

							elif "COP" in d[1] and cur_ts<570*60:
								handl = threading.Thread(target=self.moo_apply_basket_cmd,args=(d[1],orders,risk,aggresive,info,),daemon=True)
								handl.start()
								
							elif cur_ts<=958*60+30:
								self.apply_basket_cmd(d[1],orders,risk,aggresive,info)

							else:
								log_print("Rejected :",d)
					else:
						log_print("Manager:","Risk exceeded, skip. ",self.net,self.set_risk*-1)

				except Exception as e:

					PrintException(e,"adding basket error")

			elif d[0] =="pair":

					now = datetime.now()
					cur_ts = now.hour*60+now.minute

					log_print("Deploying:",d)
					if self.net > self.set_risk*-1 and cur_ts<=957:

						self.apply_pair_cmd(d[1])

			elif d[0] =="flatten":

				try:
					if d[1] == "ALL":
						self.flatten_all()
					else:
						log_print("flattening ",d[1],list(self.baskets.keys()))
						#if d[1] in list(self.baskets.keys()):

						for basket in list(self.baskets.keys()):
							
							l = len(d[1])
							log_print("flattening checking",d[1],basket[:l])
							if d[1]==basket[:l]:
								self.baskets[basket].flatten_cmd()
							#self.baskets[d[1]].flatten_cmd()
						# l = len(d[1])
						# for d in list(self.baskets.keys()):
						# 	print("trying to flat",d[1],"checking:",d[:l])
						# 	if d[1]==d[:l]:
						# 		self.baskets[d].flatten_cmd()
				except Exception as e:
					PrintException(e,"Flatten")
			elif d[0] =="shutdown":
				break

	def ppro_in(self):

		count = 0
		while True:
			d = self.pipe_ppro_in.recv()

			#FIRST TWO CONNECTION CHECK

			if d[0] =="ppro_in":
				try:
					self.ui.ppro_status.set(str(d[1]))

					if str(d[1])=="Connected":
						self.ui.ppro_status_["background"] = "#97FEA8"
					else:
						self.ui.ppro_status_["background"] = "red"

						for symbol in self.symbols:
							self.pipe_ppro_out.send(["Register",symbol])

						self.pipe_ppro_out.send(["Register","QQQ.NQ"])


					log_print("PPRO In status update:",d[1])

				except Exception as e:
					PrintException(e,"PPRO IN ERROR")

			elif d[0] =="ppro_out":

				try:
					self.ui.ppro_out_status.set(str(d[1]))

					if str(d[1])=="Connected":
						self.ui.ppro_status_out["background"] = "#97FEA8"
					else:
						self.ui.ppro_status_out["background"] = "red"
				except Exception as e:
					PrintException(e,"PPRO OUT ERROR")

			elif d[0] =="msg":
				log_print("msg:",d[1])

			elif d[0] == POSITION_UPDATE:


				try:
					positions = d[1]
					user = d[2]

					# self.user.set("User:"+user)
					self.current_positions = positions

					self.ui.user.set(user)
					self.ui.position_count.set(len(self.current_positions))
					self.ui.account_status["background"] = "#97FEA8"
					#log_print("Position updates:",len(positions),positions)

					count +=1 

					if count%2==0:# and count%20!=0:

						req = threading.Thread(target=self.get_symbol_price, daemon=True)
						req.start()

						if self.symbol_inspection_start:
							handl = threading.Thread(target=self.symbols_inspection,daemon=True)
							handl.start()
						else:
							log_print("inspection wait one")

						rec = threading.Thread(target=self.record_update,daemon=True)
						rec.start()

				except Exception as e:
					PrintException(e, " POSITION UPDATE ERROR")

			elif d[0] == SUMMARY_UPDATE:

				now = datetime.now()
				cur_ts = now.hour*3600+now.minute*60+now.second

				data = d[1]

				try:
					for key,val in data.items():
						self.current_summary[key].set(val)

					if abs(cur_ts-data['timestamp'])>5:

						self.ui.ppro_last_update.set(str(abs(cur_ts-data['timestamp']))+" delay")

						self.ui.timersx["background"] = "red"
					else:
						self.ui.ppro_last_update.set('REALTIME')

						self.ui.timersx["background"] = "#97FEA8"

					self.ui.update_performance(data)

					self.check_all_pnl()
				except Exception as e :
					PrintException(e, " Updating Summary Problem")

			elif d[0] =="order rejected":
  
				data = d[1]

				symbol = data["symbol"]
				side = data["side"]

				log_print(symbol,"rejected on ",side)
				try:
					if symbol in self.symbol_data:
						self.symbol_data[symbol].rejection_message(side)
				except Exception as e:
					PrintException(e,"Order rejection error")
				# if symbol in self.tradingplan:
				# 	self.tradingplan[symbol].ppro_order_rejection()


			elif d[0] =="shutdown":
				break


			elif d[0] =="order confirm":  ### IN USE. 

				data = d[1]
				symbol = data["symbol"]
				price = data["price"]
				shares = data["shares"]
				side = data["side"]

				## HERE. Append it to the new symbol warehouse system. 
				log_print("Manager: Holding update:",symbol,price,shares,side)

				try:
					if symbol in self.symbols:

						if side == LONG:
							self.symbol_data[symbol].holdings_update(price,shares)

						elif side == SHORT:
							self.symbol_data[symbol].holdings_update(price,-shares)

				except	Exception	as e:
					PrintException(e,"Order confim error")

			elif d[0] =="order update": ### DEPRECATED. 
				data = d[1]
				symbol = data["symbol"]
				bid = data["bid"]
				ask = data["ask"]
				ts = data["timestamp"]

				# here I update the symbol instead. 
				# and then the symbol update each of the tradingplan bound to it. 

				#print(symbol,bid,ask,ts)

				try:
					if symbol in self.symbols:
						self.symbol_data[symbol].update_price(bid,ask,ts)
				except	Exception	as e:
					PrintException(e,"Order update error")
				# if symbol in self.tradingplan:
				# 	self.tradingplan[symbol].ppro_update_price(bid,ask,ts)

			elif d[0] =='order update_m':### DEPRECATED. 
				data = d[1]
				symbol = data["symbol"]
				bid = data["bid"]
				ask = data["ask"]
				ts = data["timestamp"]

				techindicator = d[2]
				#print("update",symbol,bid,ask,ts)
				#if symbol in self.tradingplan:

				try:
					if symbol in self.symbols:
						self.symbol_data[symbol].update_techindicators(techindicator)
						self.symbol_data[symbol].update_price(bid,ask,ts)
				except	Exception	as e:
					PrintException(e,"Order update error")
				### UPDATE THE EMAs. 

			# if d[0] =="new stoporder":

			# 	self.ppro_append_new_stoporder(d[1])

	def get_symbol_price(self):

		try:
			with self.get_price_lock:

				symbols = list(self.symbols_short.keys())

				if len(symbols)>0:
					s = ''
					for i in symbols:
						s+=i+','
					s=s[:-1]

					b = "https://financialmodelingprep.com/api/v3/quote-short/"+s+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"

					res=requests.get(b)
					d= json.loads(res.text)

					x = {}
					for i in d:
						x[i['symbol']] = i['price']

					for symbol,price in x.items():

						if symbol in self.symbols_short:
							self.symbol_data[self.symbols_short[symbol]].update_price(price,price,0)

					#log_print("Manager: price update complete.. symbols:",len(symbols),x,symbol,self.symbols_short[symbol],self.symbol_data[self.symbols_short[symbol]].get_bid())
		except	Exception	as e:
			PrintException("Updating prices error",e)

	def get_position(self,ticker):

		if ticker in self.current_positions:
			return self.current_positions[ticker]
		else:
			return (0,0)

	def set_all_tp(self):

		timer=self.ui.all_timer.get()
		ep=self.ui.all_enp.get()
		et=self.ui.all_ent.get()
		managment=self.ui.all_mana.get()
		risk = int(self.ui.all_risk.get())
		reloa = int(self.ui.all_reload.get())

		for d in self.tradingplan.values():
			if self.ui.all_timer_b.get()==1:
				d.tkvars[TIMER].set(timer)
			if self.ui.all_risk_b.get()==1:
				d.data[ESTRISK] = risk
			if self.ui.all_enplan_b.get()==1:
				d.tkvars[ENTRYPLAN].set(ep)
			if self.ui.all_entype_b.get()==1:
				d.tkvars[ENTYPE].set(et)
			if self.ui.all_manaplan_b.get()==1:
				d.tkvars[MANAGEMENTPLAN].set(managment)
			if self.ui.all_reload_b.get()==1:
				d.data[RELOAD_TIMES] = reloa
			d.adjusting_risk()
			d.update_displays()

	def deselect_all(self):
		for d in self.tradingplan.values():
			d.tkvars[SELECTED].set(False)

	def set_selected_tp(self):

		timer=self.ui.all_timer.get()
		ep=self.ui.all_enp.get()
		et=self.ui.all_ent.get()
		managment=self.ui.all_mana.get()
		reloa = int(self.ui.all_reload.get())

		for d in self.tradingplan.values():
			if d.tkvars[SELECTED].get()==True:
				d.tkvars[ENTRYPLAN].set(ep)
				d.tkvars[ENTYPE].set(et)
				d.tkvars[MANAGEMENTPLAN].set(managment)
				d.tkvars[TIMER].set(timer)
				d.data[RELOAD_TIMES] = reloa

				d.adjusting_risk()
				d.update_displays()
				
	def flatten_all(self):
		for d in list(self.baskets.values()):
			if d.in_use:
				d.flatten_cmd()

	def get_record(self,algo_name):

		w,m,r = 0,0,0

		if algo_name in self.weekly_record['total']:
			w = self.weekly_record['total'][algo_name]

		if algo_name in self.monthly_record['total']:
			m = self.monthly_record['total'][algo_name]
		if algo_name in self.total_record['total']:
			r = self.total_record['total'][algo_name]

		return w,m,r

	def load_record(self):

		self.record_files = []
		try:				
			for file in os.listdir("../../algo_records/"):
				if file[-4:]=='json':
					print(file)
					symbol = file[:-5]
					self.record_files.append(symbol)

		except	Exception	as e:
			PrintException(e,"record loading error")

	def take_records(self,x):
		
		t = {}
		ind = {}
		
		try:
			for i in self.record_files[-x:]:
				with open("../../algo_records/"+i+'.json') as f:
					data = json.load(f)
				for key,items in data["algos"].items():
					if key not in t:
						t[key]=float(items)
						ind[key]=[round(float(items),2)]
					else:
						t[key]+=float(items)
						ind[key].append(round(float(items),2))
						
			for key in t.keys():
				t[key] = round(t[key],2)

		except	Exception	as e:
			PrintException(e,"take_records error")   
		d = {}
		d['total'] = t
		d['byday'] = ind
		return d

	def record_update(self):

		# self.record["total"] = {}
		# self.record["algos"] = {}
		# self.record["detes"] = {}
		now = datetime.now()
		ts = now.hour*60 + now.minute
		idx = ts-570
		if idx<0:
			idx=0
		if idx>389:
			idx=389
		try:

			for key,item in self.current_summary.items():
				self.record['total'][key] = item.get()

			for tradingplan in list(self.baskets.values()):

				ALGO = tradingplan.algo_name
				real = tradingplan.data[REALIZED] + tradingplan.data[UNREAL]

				self.record["algos"][ALGO] = real

				if ALGO not in self.record["detes"]:
					self.record["detes"][ALGO] = [0 for i in range(390)]
					self.record["detes"][ALGO][idx] =real
				else:
					self.record["detes"][ALGO][idx] =real

				if "TOTAL" not in self.record["detes"]:
					self.record["detes"]["TOTAL"] = [0 for i in range(390)]
					self.record["detes"]["TOTAL"][idx] =self.record['total']['net']
				else:
					self.record["detes"]["TOTAL"][idx] =self.record['total']['net']
			with open(self.file, 'w') as f:
				json.dump(self.record, f)
			#print(self.record)
		except Exception as e:
			PrintException(e,"record error")
		# 	now = datetime.now()
		# 	ts = now.hour*3600 + now.minute*60 + now.second

def force_close_port(port, process_name=None):
	"""Terminate a process that is bound to a port.
	
	The process name can be set (eg. python), which will
	ignore any other process that doesn't start with it.
	"""
	for proc in psutil.process_iter():
		for conn in proc.connections():
			if conn.laddr[1] == port:
				#Don't close if it belongs to SYSTEM
				#On windows using .username() results in AccessDenied
				#TODO: Needs testing on other operating systems
				try:
					proc.username()
				except psutil.AccessDenied:
					pass
				else:
					if process_name is None or proc.name().startswith(process_name):
						try:
							proc.kill()
						except (psutil.NoSuchProcess, psutil.AccessDenied):
							pass 

if __name__ == '__main__':


	force_close_port(4440)
	multiprocessing.freeze_support()

	port =4609

	goodtrade_pipe, receive_pipe = multiprocessing.Pipe()

	# algo_voxcom = multiprocessing.Process(name="algo vox1",target=algo_manager_voxcom3, args=(receive_pipe,),daemon=True)
	# algo_voxcom.daemon=True




	algo_voxcom = multiprocessing.Process(name="http server",target=httpserver, args=(receive_pipe,),daemon=True)
	algo_voxcom.daemon=True



	ppro_in, ppro_pipe_end = multiprocessing.Pipe()

	ppro_in_manager = multiprocessing.Process(name="ppro in",target=Ppro_in, args=(port,ppro_pipe_end),daemon=True)
	ppro_in_manager.daemon=True


	ppro_out, ppro_pipe_end2 = multiprocessing.Pipe()

	ppro_out_manager = multiprocessing.Process(name="ppro out",target=Ppro_out, args=(ppro_pipe_end2,port,ppro_pipe_end,),daemon=True)
	ppro_out_manager.daemon=True


	root = tk.Tk()
	root.title("GoodTrade Algo Manager v5 b4")
	root.geometry("1280x1080")

	processes = [algo_voxcom,ppro_in_manager,ppro_out_manager]
	manager=Manager(root,goodtrade_pipe,ppro_out,ppro_in,TEST,processes)
	
	#Tester(receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	# print(len(sys.argv))
	# if len(sys.argv)==2:
	# 	BackTester(manager,receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	# elif len(sys.argv)==3:
	# 	Tester(receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	# else:
	a=1
	algo_voxcom.start()

	ppro_out_manager.start()
	ppro_in_manager.start()		


	# SWICH.  
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)

	root.mainloop()

	ppro_out.send(["shutdown"])

	ppro_pipe_end.send(["shutdown"])
	receive_pipe.send(["shutdown"])

	time.sleep(2)

	algo_voxcom.terminate()
	ppro_in_manager.terminate()
	ppro_out_manager.terminate()

	algo_voxcom.join()
	ppro_in_manager.join()
	ppro_out_manager.join()
	print("All subprocesses terminated")

	print("checking remaining processes:",multiprocessing.active_children(),threading.active_count())

		
	current_system_pid = os.getpid()

	ThisSystem = psutil.Process(current_system_pid)
	ThisSystem.terminate()
	os._exit(1)

	print("exit")