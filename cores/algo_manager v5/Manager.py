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

import psutil

try:
	import psutil
except ImportError:
	import pip
	pip.main(['install', 'psutil'])
	import psutil

from psutil import process_iter

#May this class bless by the Deus Mechanicus.

# try:
# 	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+".txt", "x")
# except:
# 	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+".txt", "w")
# f.close()



TEST = True


def request(post):
	#print("sending ",post)
	try:
		requests.get(post)
	except:
		print(post, "failed")


try:
	import smtplib
except ImportError:
	import pip
	pip.main(['install', 'smtplib'])
	import smtplib

try:
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart
	from email.mime.application import MIMEApplication
except ImportError:
	import pip
	pip.main(['install', 'email'])
	
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart
	from email.mime.application import MIMEApplication

# Email configuration

CONNECTED  ="Connected"
# DISCONNECTED = "Disconnec"

class Manager:

	def __init__(self,root,goodtrade_pipe=None,ppro_out=None,ppro_in=None,TEST_MODE=False,processes=[]):


		self.total_difference = 0
		self.root = root

		self.termination = False

		self.system_enable = False 

		self.email_error = 0

		self.pipe_ppro_in = ppro_in
		self.pipe_ppro_out = ppro_out
		self.pipe_goodtrade = goodtrade_pipe


		self.ppro_in_inspection = False
		self.ppro_out_inspection = False 
		self.ppro_realtime_inspection = False 
		self.account_inspection = False 

		self.rejection_count = 0
		self.test_mode = TEST_MODE

		self.symbols = []
		self.symbols_short = {}
		self.symbol_data = {}


		self.baskets = {}
		self.baskets_lock = threading.Lock()

		self.get_symbol_price_lock = threading.Lock()

		self.bad_symbols = []

		self.rejected_symbols = []
		self.processes = processes
	
		self.algo_ids = []

		self.manage_lock = 0

		self.algo_limit = 199

		self.spread_check = {}
		self.real_time_ts = 0
		self.last_price_ts = 0

		""" POSITION DATA """

		# no need to use lock. everytime need to read. just obtain copy. 

		self.current_positions = {} #for 

		self.current_summary = {}

		self.current_summary['unrealizedPlusNet'] = tk.DoubleVar()
		self.current_summary['unrealized'] = tk.DoubleVar()
		self.current_summary['net'] = tk.DoubleVar()
		self.current_summary['timestamp'] = tk.StringVar()
		self.current_summary['fees'] = tk.DoubleVar()
		self.current_summary['trades'] = tk.DoubleVar()
		self.current_summary['sizeTraded'] = tk.DoubleVar()
		self.current_summary['cur_exp'] = tk.StringVar()
		self.current_summary['max_exp'] = tk.StringVar()

		self.user = tk.StringVar(value="User:")

		""" UI """
		self.receiving_signals = tk.BooleanVar(value=True)
		self.cmd_text = tk.StringVar(value="Status:")


		self.disaster_mode = tk.BooleanVar(value=0)

		self.ta_moc = tk.BooleanVar(value=0)
		self.moc_1559 = tk.BooleanVar(value=0)
		self.moc_1601 = tk.BooleanVar(value=0)

		self.ui = UI(root,self,self.receiving_signals,self.cmd_text)

		self.ui_root = root

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

		self.concept_record,self.monthly,self.nets,mm,mq,cm,cq= self.take_records_concept()


		#
		print(sum(self.nets[-5:]),sum(self.nets[-21:]),self.nets[-20:])

		self.ui.weeklyTotal.set(int(sum(self.nets[-5:])))

		self.ui.monthlyTotal.set(int(sum(self.nets[-21:])))
		self.ui.quarterlyTotal.set(int(sum(self.nets[-63:])))

		self.ui.monthly_commision.set("Fees:"+str(cm))
		self.ui.quarterly_commision.set("Fees:"+str(cq))

		self.ui.monthly_manual.set("Manual:"+str(mm))
		self.ui.quarterly_manual.set("Manual:"+str(mq))

		self.gateway = 0

		######

		self.get_price_lock = threading.Lock()
		######
		self.moo_orders = {}

		self.moo_algos = {}
		self.moo_lock = threading.Lock()


		self.total_moc_nq = {}

		self.shutdown=False

		self.symbol_inspection_lock = threading.Lock()
		self.symbol_inspection_start = True

		self.close_timer = 0

		good = threading.Thread(target=self.goodtrade_in, daemon=True)
		good.start()
		
		ppro_in = threading.Thread(target=self.ppro_in, daemon=True)
		ppro_in.start()

		timer = threading.Thread(target=self.timer, daemon=True)
		timer.start()

		self.pipe_ppro_out.send(["Register","QQQ.NQ"])


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
			# if it is still running.

			if self.baskets[tp].get_flatten_order()!=True:
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

		if self.disaster_mode.get()!=1:
			self.ui_root.config(bg='light grey')
			if self.symbol_inspection_lock.locked()==False and self.symbol_inspection_start==True:

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

						#print("inspecting:",val)
						try:
							c+=val.symbol_inspection()
							#self.total_difference+=abs(val.get_difference())
							if c>=30:
								break
								log_print("ORDERING LIMIT REACHED.")
						except Exception as e:
							PrintException(e,"inspection error")

					self.total_difference = c 

				#log_print("Manager: performing symbols inspection compelte, total difference:",self.total_difference, "order counts:",c)
			else:
				log_print("Manager: previous symbols inspection not finished. skip.")
		else:
			log_print("Manager: DISASTER MODE INIT")
			self.ui_root.config(bg='red')


	def algo_as_is(self,algo_name):

		if algo_name in self.baskets:
			self.baskets[algo_name].algo_as_is()

			log_print(algo_name," AS IS.")

	def apply_pair_cmd(self,d):

		pair = d['pair'] 

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


				self.baskets[pair].submit_expected_pair(d['amount'],d['passive'],d['timer'])

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

			# print("REGISTERING")
			if self.ui.basket_label_count<self.algo_limit:

				# print("REGISTERING good")

				check = False 

				for j,i in orders.items():

					if i!=0:
						check = True 
						break

				if check:
					self.baskets[basket_name] = TradingPlan_Basket(basket_name,risk,self,info)
					self.ui.create_new_single_entry(self.baskets[basket_name],"Basket",None)

					self.baskets[basket_name].deploy()
				else:
					return 

			else:
				log_print(basket_name," exceeding algo limit.")

		if self.baskets[basket_name].shut_down==False:
			for symbol,value in orders.items():

				if "." in symbol and symbol not in self.bad_symbols and symbol not in self.total_moc_nq:
					log_print("Manager: Applying basket command",symbol,value)
					if symbol not in self.symbol_data:
						self.symbol_data[symbol] = Symbol(self,symbol,self.pipe_ppro_out)  #register in Symbol.
						self.symbols.append(symbol)
						self.symbols_short[symbol[:-3]] = symbol

					self.baskets[basket_name].register_symbol(symbol,self.symbol_data[symbol])

					## now , submit the request.

					if "TA" in info:
						if info['TA']>30:
							self.baskets[basket_name].submit_incremental_expected(symbol,value,info['TA'],aggresive)
						else:
							self.baskets[basket_name].submit_expected_shares(symbol,value,aggresive)
					else:
						self.baskets[basket_name].submit_expected_shares(symbol,value,aggresive)
				else:
					log_print("Manager: Wrong Ticker format or BANNED:",symbol)
		else:
			log_print(basket_name,"already shutdown")

	def send_moo(self,dic):
		now = datetime.now()
		ts = now.hour*60 + now.minute

		c =0

		with self.moo_lock:
			for symbol,share in dic.items():
				
				share = int(share)
				print("sending",symbol,share)

				if ts<571:
					offset = 0.5 
					if share<0:

					# 	if symbol[-2:]=="NQ":
					# 		reque =  "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+'&priceadjust='+str(offset)+'&ordername=NSDQ Sell->Short NSDQ LOO Far Regular OnOpen&shares='+str(abs(share))
					# 	else:
					# 		reque =  "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+'&priceadjust='+str(offset)+'&ordername=ARCA%20Sell->Short%20ARCX%20LOO%20Far%20OnOpen&shares='+str(abs(share))
					# else:

					# 	if symbol[-2:]=="NQ":
					# 		reque =  "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+'&priceadjust='+str(offset)+'&ordername=NSDQ Buy NSDQ LOO Far Regular OnOpen&shares='+str(abs(share))
					# 	else:
					# 		reque =  "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+'&priceadjust='+str(offset)+'&ordername=ARCA%20Buy%20ARCX%20LOO%20Far%20OnOpen&shares='+str(abs(share))
										
						if c%2==0:
							reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Sell->Short%20ARCX%20MOO%20OnOpen&shares="+str(abs(share))
						else:
							reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=NSDQ Sell->Short NSDQ MOO Regular OnOpen&shares="+str(abs(share))
					else:
						if c%2==0:
							reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Buy%20ARCX%20MOO%20OnOpen&shares="+str(share)
						else:
							reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=NSDQ Buy NSDQ MOO Regular OnOpen&shares="+str(share)
					c=2 

					### TEST BLOCK. MARKET IN AND OUT.
				else:
					if share<0:
						reque = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(abs(share))
					else:
						reque = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Buy ARCX Market DAY&shares='+str(share)


				print(symbol[-2:],reque)
				req = threading.Thread(target=request, args=(reque,),daemon=True)
				req.start() 

	def send_moc(self,dic):
		pass 

	def timer(self):

		moo_release = False 
		pair_release = False 
		moc_release = False 
		moc_pair_release = False

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		premarket_timer_start = 350*60
		premarket_timer_stop = 550 *60

		MOO_as_is = 566*60
		MOO_as_is_exit =False 


		##########################################################
		MOO_exit_timer_NQ = 567*60 #ts+19 #
		MOO_exit_NQ = False 

		MOO_exit_timer_NY = 567*60+30 #ts+19 #
		MOO_exit_NY= False 

		MOO_exit_timer_AM = 569*60+30 #ts+19 #
		MOO_exit_AM = False 


		Moo_enter_timer_NQ = 566*60+30 #569*60+10  #ts+20 558*60+10 #
		Moo_enter_NQ = False 

		Moo_enter_timer_NY = 566*60+40 #569*60+10  #ts+20558*60+15 
		Moo_enter_NY = False 

		Moo_enter_timer_AM = 569*60+45 #569*60+10  #558*60+20
		Moo_enter_AM = False

		##########################################################

		MOO_pair_timer = 570*60+20 #ts+25 # #529*60#
		MOO_pair = False 


		MOC_send_out_timer_NQ = 954*60+30 #954*60+30 

		MOC_send_out_timer = 958*60+40 #958*60+40 #958*60+50


		
		MOC_NQ = False 

		MOC_1559_timer = 959*60
		#MOC_1559_timer = MOC_send_out_timer+30
		MOC_1559 = False 

		MOC_pairing_timer = 959*60+50
		#MOC_pairing_timer = MOC_send_out_timer+60

		MOC_flat_timer = 961*60
		#MOC_flat_timer = MOC_send_out_timer+90
		MOC_flat = False 

		c = 0 
		log_print("Timer: functional and counting")
		checkmts  = 0
		mts = 0
		while True:
			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second

			mts = now.hour*60 + now.minute 

			if ts>=MOO_exit_timer_AM and MOO_exit_AM==False :

				total_moo_exit = {}

				with self.baskets_lock:
					for name,basket in self.baskets.items():
						if "IMB" in name and "AM" in name:
							self.algo_as_is(name)
				time.sleep(10)

				target = ".AM"

				out = self.symbol_data.copy()
				for symbol,data in out.items():
					if target in symbol:
						share = data.get_all_moo_exit()*-1

						if share!=0:
							total_moo_exit[symbol] = share

				log_print("Timer: timer triggered for MOO Exit:",total_moo_exit)

				self.send_moo(total_moo_exit)

				MOO_exit_AM = True 
			if ts>=MOO_exit_timer_NQ and MOO_exit_NQ==False :

				total_moo_exit = {}

				with self.baskets_lock:
						for name,basket in self.baskets.items():
							if "IMB" in name and "NQ" in name:
								self.algo_as_is(name)
				time.sleep(10)

				target = ".NQ"
				out = self.symbol_data.copy()
				for symbol,data in out.items():
					if target in symbol:
						share = data.get_all_moo_exit()*-1

						if share!=0:
							total_moo_exit[symbol] = share

				log_print("Timer: timer triggered for MOO Exit:",total_moo_exit)

				self.send_moo(total_moo_exit)

				MOO_exit_NQ = True 
			if ts>=MOO_exit_timer_NY and MOO_exit_NY==False :

				total_moo_exit = {}

				with self.baskets_lock:
					for name,basket in self.baskets.items():
						if "IMB" in name and "NY" in name:
							self.algo_as_is(name)
				time.sleep(10)

				target = ".NY"
				out = self.symbol_data.copy()
				for symbol,data in out.items():
					if target in symbol:
						share = data.get_all_moo_exit()*-1

						if share!=0:
							total_moo_exit[symbol] = share

				log_print("Timer: timer triggered for MOO Exit:",total_moo_exit)

				self.send_moo(total_moo_exit)

				MOO_exit_NY = True 
			if ts>=Moo_enter_timer_NQ and Moo_enter_NQ==False :

				total_moo_enter = {}
				target = ".NQ"
				out = self.symbol_data.copy()
				for symbol,data in out.items():

					if target in symbol:
						share = data.get_all_moo_enter()

						if share!=0:
							total_moo_enter[symbol] = share

				log_print("Timer: timer triggered for MOO Enter",target,total_moo_enter)
				self.send_moo(total_moo_enter)
				Moo_enter_NQ = True 

			if ts>=Moo_enter_timer_NY and Moo_enter_NY==False :

				total_moo_enter = {}
				target = ".NY"

				out = self.symbol_data.copy()
				for symbol,data in out.items():
					if target in symbol:
						share = data.get_all_moo_enter()

						if share!=0:
							total_moo_enter[symbol] = share

				log_print("Timer: timer triggered for MOO Enter",target,total_moo_enter)
				self.send_moo(total_moo_enter)
				Moo_enter_NY = True 

			if ts>=Moo_enter_timer_AM and Moo_enter_AM==False :

				total_moo_enter = {}
				target = ".AM"
				out = self.symbol_data.copy()
				for symbol,data in out.items():
					if target in symbol:
						share = data.get_all_moo_enter()

						if share!=0:
							total_moo_enter[symbol] = share

				log_print("Timer: timer triggered for MOO Enter",target,total_moo_enter)
				self.send_moo(total_moo_enter)
				Moo_enter_AM = True 

			if ts>=MOO_pair_timer and MOO_pair == False:

				### ALL INSPECTION NOW TURN ON.
				log_print("Timer: pair timer initiated")

				with self.baskets_lock:
					for trade in list(self.baskets.values()):
						trade.turn_on_inspection()

				MOO_pair = True 


			if ts>=MOC_send_out_timer_NQ and MOC_NQ == False:

				#total_moc_nq = {}
				self.total_moc_nq = {}
				for name,basket in self.baskets.items():
					if "NQ" in name:
						self.algo_as_is(name)

				total_moc = self.current_positions.copy()

				
				for ticker in total_moc.keys():
					share = total_moc[ticker][1]
					reque = ""
					if ticker[-2:]=="NQ":

						self.total_moc_nq[ticker] = share

						if share<0:
							reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=NSDQ Buy NSDQ MOC DAY&shares="+str(abs(share))
						elif share>0:
							reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=NSDQ Sell->Short NSDQ MOC DAY&shares="+str(share)

						if reque!="":
							try:
								log_print("Sending" ,reque)
								req = threading.Thread(target=request, args=(reque,),daemon=True)
								req.start()
							except Exception as e:
								PrintException(e)


				MOC_NQ = True 

			if ts>=MOC_send_out_timer and moc_release==False:

				########################################################################################################################
				############### ROSN Buy RosenblattDQuoteClose MOC DAY             #####################################################
				############### ROSN Sell->Short RosenblattDQuoteClose MOC DAY     #####################################################
				########################################################################################################################

				log_print("Timer: MOC begins")
				#self.symbol_inspection_start = False

				with self.symbol_inspection_lock: 
					
					total_moc = {}

					for name,basket in self.baskets.items():
						self.algo_as_is(name)

					mul = 1 

					if self.moc_1559.get():
						mul+=1

					if self.moc_1601.get():
						mul+=1 


					total_moc = self.current_positions

					log_print(mul,total_moc)

					
					for ticker in total_moc.keys():

						reque = ""
						
						share = total_moc[ticker][1]

						if ticker[-2:]=="NY":
							if share<0:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ROSN Buy RosenblattDQuoteClose MOC DAY&shares="+str(abs(share))
							elif share>0:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ROSN Sell->Short RosenblattDQuoteClose MOC DAY&shares="+str(share)
						elif ticker[-2:]=="AM":

							if share<0:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Buy ARCX MOC DAY&shares="+str(abs(share))
							elif share>0:
								reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Sell->Short ARCX MOC DAY&shares="+str(share)

						elif ticker[-2:]=="NQ":

							if ticker not in self.total_moc_nq:
								if share<0:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Buy ARCX MOC DAY&shares="+str(abs(share))
								elif share>0:
									reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+ticker+"&ordername=ARCA Sell->Short ARCX MOC DAY&shares="+str(share)

						if reque!="":
							try:
								log_print("Sending" ,reque)
								req = threading.Thread(target=request, args=(reque,),daemon=True)
								req.start()
							except Exception as e:
								PrintException(e)

				moc_release=True


			if ts>=MOC_1559_timer and MOC_1559 == False and self.moc_1559.get():

				## reduce by 1/3 

				with self.baskets_lock:
					for trade in list(self.baskets.values()):
						trade.reduce_one_third_aggresive()

				MOC_1559 = True 

			if ts>=MOC_flat_timer and MOC_flat ==False:

				## flat ### each symbol send flattening. 

				# for symbol,data in self.symbol_data.items():
				# 	data.ppro_flatten()
				
				MOC_flat= True 

			if ts>MOC_pairing_timer and moc_pair_release==False:

				#every tp's symbol no clear.
				log_print("last paring.")
				for name,basket in self.baskets.items():
					basket.flatten_cmd()

				moc_pair_release=True

			#print('current:',ts)

			if mts!=checkmts:
				checkmts = mts
				self.close_timer = mts
				log_print("Timer current: ",mts)
			time.sleep(3)

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
					if str(d[1])==CONNECTED:
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
					cur_ts = now.hour*60+now.minute

					confirmation,orders,risk,aggresive,multiplier = self.ui.order_confirmation(d[1],d[2])

						# stop,

					if self.net > self.set_risk*-1 and self.system_enable:
						if confirmation:
							#log_print("basket update:",d)
							#log_print(d[1],confirmation,orders,risk,aggresive)

							info = d[3]

							for key in info.keys():
								if type(info[key])==int  or type(info[key])==float:
									if key!="TA":
										info[key] =info[key]*multiplier

								
							if cur_ts<=958:
								log_print("Manager:","basket update:",d,info)
								self.apply_basket_cmd(d[1],orders,risk,aggresive,info)
					else:
						log_print("Manager:","Risk exceeded, skip. ",self.net,self.set_risk*-1)

				except Exception as e:

					PrintException(e,"adding basket error")

			elif d[0] =="pair":

				try:
					now = datetime.now()
					cur_ts = now.hour*60+now.minute

					log_print("Deploying:",d)
					if self.net > self.set_risk*-1 and cur_ts<=957 and self.system_enable:

						self.apply_pair_cmd(d[1])

				except Exception as e:

					PrintException(e,"pair error")
			elif d[0] =="flatten":

				try:
					if d[1] == "ALL":
						self.flatten_all()
					else:
						log_print("flattening ",d[1])
						for basket in list(self.baskets.keys()):
							l = len(d[1])

							if d[1]==basket[:l]:
								self.baskets[basket].flatten_cmd()

				except Exception as e:
					PrintException(e,"Flatten error")
			elif d[0] =="shutdown":
				break

	def system_check(self):


		#### if all green. then good to go ###

		try:
			if self.ui.user.get()!="DISCONNECTED" and self.ui.ppro_api_status.get()==CONNECTED :

				# and self.ui.file_last_update.get()==CONNECTED
				# GOOD TO GO.
				self.ui.system_status_text.set("READY")
				self.ui.system_status['bg'] = 'lightgreen'
				#log_print("System all green")

				

				if self.system_enable==False:
					self.online_alert()

					self.system_enable = True 
				
				
			else:

				self.ui.system_status_text.set("ERROR")
				self.ui.system_status['bg'] = 'red'
				self.ui.system_status.flash()

				

				if self.system_enable:
					self.disconnection_alert()
					self.system_enable = False 
				## if . send me an email.
				
		except Exception as e:
			PrintException(e,"System_check error:")


		### if not flash ### 

	def ppro_in(self):

		count = 0
		while True:
			d = self.pipe_ppro_in.recv()

			#FIRST TWO CONNECTION CHECK

			if d[0] =="ppro_in": ### DEPRECATED
				try:
					self.ui.ppro_api_status.set(str(d[1]))

					if str(d[1])!=CONNECTED:
						self.ui.ppro_api_status_label["background"] = "red"

					else:
						self.ui.ppro_api_status_label["background"] = self.ui.deployment_frame.cget("background") #"#d9d9d9" 

						for symbol in self.symbols:
							self.pipe_ppro_out.send(["Register",symbol])

						#self.pipe_ppro_out.send(["Register","QQQ.NQ"])

					log_print("PPRO In status update:",d[1])

				except Exception as e:
					PrintException(e,"PPRO IN ERROR")

			elif d[0] =="ppro_api":

				try:
					self.ui.ppro_api_status.set(str(d[1]))

					if str(d[1])!=CONNECTED:
						self.ui.ppro_api_status_label["background"] =  "red"
					else:
						self.ui.ppro_api_status_label["background"] = self.ui.deployment_frame.cget("background") #"#d9d9d9" 

					self.system_check()
				except Exception as e:
					PrintException(e,"PPRO OUT ERROR")

			elif d[0] =="msg":
				log_print("msg:",d[1])

			elif d[0] == POSITION_UPDATE:


				try:
					positions = d[1]
					user = d[2]

					now = datetime.now()
					ts = now.hour*60 + now.minute

					self.current_positions = positions

					self.ui.user.set(user)
					self.ui.position_count.set(len(self.current_positions))
					self.ui.account_status["background"] =self.ui.deployment_frame.cget("background")
					#log_print("Position updates:",len(positions),positions)

					count +=1 

					req = threading.Thread(target=self.get_symbol_price, daemon=True)
					req.start()

					if count%4==0:# and count%20!=0:

						if self.symbol_inspection_start:
							handl = threading.Thread(target=self.symbols_inspection,daemon=True)
							handl.start()
						else:
							log_print("inspection wait one")

						rec = threading.Thread(target=self.record_update,daemon=True)
						rec.start()

					if count%10==0 and ts>=959 and ts<=961:
						self.periodical_status()

					# if count%10==0 and ts==960:
					# 	self.periodical_status()

					if count%300==0:
						if ts>=500 and ts<965:

							self.periodical_status()

				except Exception as e:
					PrintException(e, " POSITION UPDATE ERROR")

			elif d[0] == SUMMARY_UPDATE:

				now = datetime.now()
				cur_ts = now.hour*3600+now.minute*60+now.second

				data = d[1]

				try:
					if len(data)==0:

						self.ui.file_last_update.set("DISCONNECTED")
						self.ui.file_link_status["background"] = "red"
					else:
						for key,val in data.items():
							self.current_summary[key].set(val)

						if abs(cur_ts-data['timestamp'])>5:

							self.ui.file_last_update.set(str(abs(cur_ts-data['timestamp']))+" delay")

							self.ui.file_link_status["background"] = "red"
						else:
							self.ui.file_last_update.set(CONNECTED)

							self.ui.file_link_status["background"] = self.ui.deployment_frame.cget("background") #"#d9d9d9" 

						self.ui.update_performance(data)


						### depends on the active. 

						if count%4==0:
							self.check_all_pnl()
					self.system_check()
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

				self.rejected_symbols.append(symbol+":"+side)

				self.rejection_count+=1
				log_print("Rejection count:",self.rejection_count)
				if self.rejection_count%5==0:
					self.rejection_alert(self.ui.user.get())

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

	def get_spread(self,symbol):

		if symbol in self.spread_check:

			return self.spread_check[symbol]

		else:
			return 0

	def get_symbol_price(self):

		### GET THE NEWEST . THEN UPDATE IT ###

		try:
			with self.get_symbol_price_lock:
				now = datetime.now()
				sts = now.hour*3600 + now.minute*60 + now.second 

				if sts>self.last_price_ts+2:
					with self.get_price_lock:
						r = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?include_otc=false&apiKey=ezY3uX1jsxve3yZIbw2IjbNi5X7uhp1H"

						r = requests.get(r)
						# print(r.text)

						d = json.loads(r.text)

						symbols = list(self.symbols_short.keys())
						cur_ts = 0 
						for i in d['tickers']:
							if i['ticker'] in symbols:
						
								last_price = i['lastTrade']['p']
								bid = i['lastQuote']['p']
								ask = i['lastQuote']['P']
								ts = int(str(i['updated'])[:10])

								if ts>cur_ts:
									cur_ts = ts
								self.symbol_data[self.symbols_short[i['ticker']]].update_price(last_price,bid,ask,ts)

							spread = i['lastQuote']['P']-i['lastQuote']['p']
							self.spread_check[i['ticker']] = spread
						self.real_time_ts

						self.real_time_ts = cur_ts
						self.last_price_ts = sts 

		except Exception	as e:
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

	def stringfy(self,dic):

		msg = "\n"

		for key,item in dic.items():

			msg +=str(key)+":"
			try:

				msg+=str(item.get()) +" "

			except:

				msg+=str(item)

		msg+="\n"

		return msg


	def output_active_tps(self):

		msg = ""
		for basket,val in self.baskets.items():
			if val.get_flatten_order()!=True:
				msg+=basket+" : " + str(val.data[UNREAL]) + " | " + str(val.data[REALIZED]) +"   "+ str(val.current_shares)+ "\n"

		return msg 

	def periodical_status(self):


			user = self.ui.user.get()
			subject = "User Status:"+user
			body = "User Status:" +str(self.close_timer) + self.stringfy(self.current_summary) + self.output_active_tps() +self.stringfy(self.current_positions)

			self.send_email_admin(subject,body)	

	def disconnection_alert(self):

		user = self.ui.user.get()
		subject = "Disconnection Alert:"+user
		body = "Disconnection."+self.stringfy(self.current_positions)  + self.stringfy(self.current_summary)

		self.send_email_admin(subject,body)

	def online_alert(self):

		user = self.ui.user.get()
		subject = "Connection:"+user
		body = "Connection.\n" +self.stringfy(self.current_positions)  + self.stringfy(self.current_summary) + "\n"+self.stringfy(self.concept_record)+"\n"+self.stringfy(self.monthly_record['total']) +"\n"+self.stringfy(self.total_record['total']) +"\n"+self.stringfy(self.monthly)

		self.send_email_admin(subject,body)

	def send_email_admin(self,subject,body):

		if self.email_error>5:
			return 

		sender = 'algomanagertnv@gmail.com'
		password = 'myvjbplswvsvktau'
		recipients = ['algomanagertnv@gmail.com']

		msg = MIMEText(body)
		msg['Subject'] = subject
		msg['From'] = sender
		msg['To'] = ', '.join(recipients)


		try:
			with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
			   smtp_server.login(sender, password)
			   smtp_server.sendmail(sender, recipients, msg.as_string())
		except Exception as e:

			self.email_error +=1
			print(e)

	def rejection_alert(self,user):

		sender = 'algomanagertnv@gmail.com'
		password = 'myvjbplswvsvktau'
		recipients = ['algomanagertnv@gmail.com','zenvoidsun@gmail.com','andrew@selectvantage.com']


		subject = "Rejection Alert:"+user +" : "+str(self.rejection_count)
		body = "Rejection: " +str(self.rejected_symbols)

		self.send_email_all(subject,body)

	def send_email_all(self,subject,body):

		if self.email_error>5:
			return 
		sender = 'algomanagertnv@gmail.com'
		password = 'myvjbplswvsvktau'
		recipients = ['algomanagertnv@gmail.com','andrew@selectvantage.com','zenvoidsun@gmail.com']


		user = self.ui.user.get()

		if "COREYKIN" in user:
			recipients.append("corey@selectvantage.com")

		 

		msg = MIMEText(body)
		msg['Subject'] = subject
		msg['From'] = sender
		msg['To'] = ', '.join(recipients)


		try:
			with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
			   smtp_server.login(sender, password)
			   smtp_server.sendmail(sender, recipients, msg.as_string())
		except Exception as e:
			self.email_error +=1
			print(e)

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
					#print(file)
					symbol = file[:-5]
					self.record_files.append(symbol)

		except	Exception	as e:
			PrintException(e,"record loading error")


	def take_records_concept(self):
		### COUNT ALL EXISTING CONCEPT ###.

		concept = self.ui.get_all_algo_names()

		monthly = {}
		### MATCHING EACH ###
		nets = []

		algo_daily = {}
		commisions = []

		try:
			for i in self.record_files[-300:]:

				month = i[:7]

				with open("../../algo_records/"+i+'.json') as f:
					data = json.load(f)
				for key,items in data["algos"].items():
					###

					if i not in algo_daily:
						algo_daily[i]=float(items)
					else:
						algo_daily[i]+=float(items)

					for k in concept.keys():
						if k == key[:len(k)]:
							concept[k] += float(items)

				if i not in algo_daily:
					algo_daily[i] = 0
				
				if month not in monthly:
					if "total" in data:
						monthly[month] = data["total"]["unrealizedPlusNet"]
						#comm_montly[month] = data['total']['fees']
				else:
					if "total" in data:
						monthly[month] += data["total"]["unrealizedPlusNet"]
						#comm_montly[month] += data['total']['fees']

				commisions.append(data['total']['fees'])
				nets.append(data['total']['unrealizedPlusNet'])#unrealizedPlusNe
						
		except	Exception	as e:
			PrintException(e,"take_records error")   

		for key in concept.keys():
			concept[key] = round(concept[key],2)


		for key in monthly.keys():
			monthly[key] = round(monthly[key],2)


		#log_print(concept)
		algo_daily = list(algo_daily.values())
		

		manual_m = int(sum(algo_daily[-21:])-sum(commisions[-21:])-sum(nets[-21:]))
		manual_q = int(sum(algo_daily[-63:])-sum(commisions[-63:])-sum(nets[-63:]))
		
		commision_m = int(sum(commisions[-21:]))
		commision_q = int(sum(commisions[-63:]))

		return concept,monthly,nets,manual_m,manual_q,commision_m,commision_q


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
	root.title("SelectTrade Algo Manager v5 b4")
	root.geometry("1350x1080")

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




# for basket,item in self.baskets.items():
# 	if basket[:3]=="PRE":
# 		for symbol,share in item.current_shares.items():	
# 			if share<0:
# 				reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Buy%20ARCX%20MOO%20OnOpen&shares="+str(share)
# 			else:
# 				reque = "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+"&ordername=ARCA%20Sell->Short%20ARCX%20MOO%20OnOpen&shares="+str(abs(share))
				
# 			req = threading.Thread(target=request, args=(reque,),daemon=True)
# 			req.start()

# 		#flat and then shut down. 
# 		item.flatten_cmd()
# 		item.shutdown()
