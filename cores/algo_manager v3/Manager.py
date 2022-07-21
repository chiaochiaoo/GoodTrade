from pannel import *
from tkinter import ttk
import tkinter as tk 
from Symbol import *
from TradingPlan import *
from TradingPlan_MMP1 import *
from TradingPlan_Basket import *
from Pair_TP import *
from Pair_TP_MM import *
from UI import *
from Ppro_in import *
from Ppro_out import *
from constant import *

import os

import random
from BackTester import *
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

from Tester import *
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


def algo_manager_voxcom(pipe):

	#tries to establish commuc


	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		#PORT = 65491       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					with open('../commlink.json') as json_file:
						port_file = json.load(json_file)

					if datetime.now().strftime("%m%d") not in port_file:
						time.sleep(1)
					else:
						PORT = port_file[datetime.now().strftime("%m%d")]
						s.connect((HOST, PORT))
						connected = True

					s.setblocking(0)
				except Exception as e:
					pipe.send(["msg","Disconnected"])
					log_print("Cannot connected. Try again in 2 seconds.",e)
					time.sleep(2)

			connection = True
			pipe.send(["msg","Connected"])
			k = None

			count = 0
			while connection:

				#from the socket
				ready = select.select([s], [], [], 0)
				
				if ready[0]:
					data = []
					while True:
						try:
							part = s.recv(2048)
						except:
							connection = False
							break
						#if not part: break
						data.append(part)
						if len(part) < 2048:
							#try to assemble it, if successful.jump. else, get more. 
							try:
								k = pickle.loads(b"".join(data))
								break
							except:
								pass
					#k is the confirmation from client. send it back to pipe.
					if k!=None:
						placed = []

						pipe.send(["pkg",k[1:]])
						for i in k[1:]:
							log_print("placed:",i[1])
							placed.append(i[1])
						#log_print("placed:",k[1][1])
						
						s.send(pickle.dumps(["Algo placed",placed]))

				# if pipe.poll(0):
				# 	data = pipe.recv()
				# 	if data == "Termination":
				# 		s.send(pickle.dumps(["Termination"]))
				# 		print("Terminate!")

				# 	part = s.recv(2048)
				# except:
				# 	connection = False
				# 	break
				# #if not part: break
				# data.append(part)
				# if len(part) < 2048:
				# 	#try to assemble it, if successful.jump. else, get more. 
				# 	try:
				# 		k = pickle.loads(b"".join(data))
				# 		break
				# 	except:
				# 		pass

				count+=1
				print(count)
			log_print("Main disconnected")
			pipe.send(["msg","Main disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)


def algo_manager_voxcom2(pipe):

	#tries to establish commuc
	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		PORT = 65491       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					s.connect((HOST, PORT))
					s.send(pickle.dumps(["Connection","Connected"]))
					connected = True
				except:
					pipe.send(["msg","Disconnected"])
					log_print("Cannot connected. Try again in 3 seconds.")
					time.sleep(3)

			connection = True

			pipe.send(["msg","Connected"])

			while connection:

				data = []
				k = None
				while True:
					try:
						part = s.recv(2048)
					except:
						connection = False
						break
					#if not part: break
					data.append(part)
					if len(part) < 2048:
						#try to assemble it, if successful.jump. else, get more. 
						try:
							k = pickle.loads(b"".join(data))
							break
						except Exception as e:
							log_print(e)
				#s.sendall(pickle.dumps(["ids"]))
				if k!=None:
					pipe.send(["pkg",k])
					#log_print("placed:",k[1][1])
					s.send(pickle.dumps(["Algo placed",k[1][1]]))
			log_print("Main disconnected")
			pipe.send(["msg","Disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)


def algo_manager_voxcom3(pipe):

	#tries to establish commuc


	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		#PORT = 65491       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					with open('../commlink.json') as json_file:
						port_file = json.load(json_file)

					if datetime.now().strftime("%m%d") not in port_file:
						time.sleep(1)
					else:
						PORT = port_file[datetime.now().strftime("%m%d")]
						s.connect((HOST, PORT))
						connected = True

					s.setblocking(1)
				except Exception as e:
					pipe.send(["msg","Disconnected"])
					log_print("Cannot connected. Try again in 2 seconds.",e)
					time.sleep(2)

			connection = True
			pipe.send(["msg","Connected"])
			k = None

			count = 0
			while connection:

				#from the socket
				data = []
				while True:
					try:
						part = s.recv(2048)
					except:
						connection = False
						break
					#if not part: break
					data.append(part)
					if len(part) < 2048:
						#try to assemble it, if successful.jump. else, get more. 
						try:
							k = pickle.loads(b"".join(data))
							break
						except:
							pass
				#k is the confirmation from client. send it back to pipe.
				if k!=None:
					if k!=['checking']:
						placed = []

						pipe.send(["pkg",k[1:]])
						for i in k[1:]:
							log_print("placed:",i[1])
							placed.append(i[1])
						#log_print("placed:",k[1][1])
						
						s.send(pickle.dumps(["Algo placed",placed]))

				# if pipe.poll(0):
				# 	data = pipe.recv()
				# 	if data == "Termination":
				# 		s.send(pickle.dumps(["Termination"]))
				# 		print("Terminate!")

				# 	part = s.recv(2048)
				# except:
				# 	connection = False
				# 	break
				# #if not part: break
				# data.append(part)
				# if len(part) < 2048:
				# 	#try to assemble it, if successful.jump. else, get more. 
				# 	try:
				# 		k = pickle.loads(b"".join(data))
				# 		break
				# 	except:
				# 		pass

				count+=1
				#print("algo place counts",count)
			log_print("Main disconnected")
			pipe.send(["msg","Main disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)


def logging(pipe):

	f = open(datetime.now().strftime("%d/%m")+".txt", "w")
	while True:
		string = pipe.recv()
		time_ = datetime.now().strftime("%H:%M:%S")
		log_print(string)
		f.write(time_+" :"+string)
	f.close()

class Manager:

	def __init__(self,root,goodtrade_pipe=None,ppro_out=None,ppro_in=None,TEST_MODE=False,processes=[]):

		self.root = root

		self.termination = False
		self.pipe_ppro_in = ppro_in
		self.pipe_ppro_out = ppro_out
		self.pipe_goodtrade = goodtrade_pipe

		self.test_mode = TEST_MODE

		self.symbols = []
		self.processes = processes
	
		self.algo_ids = []

		self.symbol_data = {}

		self.baskets = {}
		self.tradingplan = {}

		self.pair_plans = {}


		self.manage_lock = 0

		self.not_passvie = tk.BooleanVar(value=False)

		self.receiving_signals = tk.BooleanVar(value=True)
		self.cmd_text = tk.StringVar(value="Status:")


		self.ui = UI(root,self,self.receiving_signals,self.cmd_text)

		m=self.receiving_signals.trace('w', lambda *_: self.receiving())

		self.active_trade = 0
		self.active_trade_max = 0

		self.total_u = 0
		self.total_u_max = 0
		self.total_u_min = 0
		self.total_r = 0
		self.total_r_max =0
		self.total_r_min = 0

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
		monday = now - timedelta(days = now.weekday())
		self.file = "../../algo_records/"+monday.strftime("%Y_%m_%d")+".csv"


		self.init_record_writer()

		self.shutdown=False

		handl = threading.Thread(target=self.shares_allocation,daemon=True)
		handl.start()

		good = threading.Thread(target=self.goodtrade_in, daemon=True)
		good.start()
		
		ppro_in = threading.Thread(target=self.ppro_in, daemon=True)
		ppro_in.start()

		timer = threading.Thread(target=self.timer, daemon=True)
		timer.start()


		#if Testerx==True:
		self.pipe_ppro_out.send(["Register","QQQ.NQ"])
		self.pipe_ppro_out.send(["Register","SPY.AM"])
		#self.pipe_ppro_out.send(["Register","SQQQ.NQ"])
#
	#data part, UI part

	def init_record_writer(self):

		try:
			self.f = open(self.file, "r")
		except:
			self.f = open(self.file, "w")
			self.recordwriter = csv.writer(self.f,lineterminator = '\n')
			self.recordwriter.writerow(['DATE', 'TIME','ALGO','SYMBOL','POSITION','RISK','REALIZED'])

		self.f.close()
		log_print(("record file start"))



	def shutdown_all_threads(self):

		self.shutdown= True



	def shares_allocation(self):

		#fro each of the symbols. look at imbalance. deal with it. 

		ts = 0

		while True:
			#create a cpy.

			if self.shutdown:
				break
			register = 0
			symbols = list(self.symbol_data.values())

			for val in symbols:
				#log_print("inspecting:",val.ticker,"request:",val.get_management_request())
				
				if val.get_register()==True:
					register+=1
				if val.get_management_request()==True and val.get_market_making()==False:
					val.symbol_inspection()
					# stage 1, cancel each other out in the request book
					# stage 2, granted request from the incoming book
					# stage 3, handle imbalance request (just use market orders now.)

			now = datetime.now()
			cur_ts = now.hour*60+now.minute 

			if cur_ts!= ts:#
				log_print("Registeriing ,",register,"total",len(symbols)," ts",cur_ts)
				ts = cur_ts
			time.sleep(5)

	def new_record(self,tradingplan):

		try:
			self.f = open(self.file, "a")
			self.recordwriter = csv.writer(self.f,lineterminator = '\n')

			now = datetime.now()
			DATE = now.strftime("%Y-%m-%d")
			TIME = now.strftime("%H:%M:%S")


			ALGO = tradingplan.algo_name
			SYMBOL = tradingplan.symbol_name
			SIDE = tradingplan.tkvars[POSITION].get()
			RISK = tradingplan.data[ESTRISK]
			real = tradingplan.data[REALIZED]

			self.recordwriter.writerow([DATE, TIME,ALGO,SYMBOL,SIDE,RISK,real])
			self.f.close()
		except:

			log_print("writing record failure for",tradingplan.symbol_name)


	def apply_basket_cmd(self,basket_name,orders,risk):


		if basket_name not in self.baskets:

			if self.ui.basket_label_count<10:
				self.baskets[basket_name] = TradingPlan_Basket(basket_name,risk,self)
				self.ui.create_new_single_entry(self.baskets[basket_name],"Basket",None)

				self.baskets[basket_name].deploy(0)
		

		if self.baskets[basket_name].shut_down==False:
			for symbol,value in orders.items():

				print("processing",symbol,value)
				if symbol not in self.symbol_data:
					self.symbol_data[symbol] = Symbol(symbol,0,100,{},self.pipe_ppro_out)  #register in Symbol.
					self.symbols.append(symbol)

				self.baskets[basket_name].register_symbol(symbol,self.symbol_data[symbol])

				## now , submit the request.

				self.baskets[basket_name].submit_expected_shares(symbol,value)
		else:
			log_print(basket_name,"already shutdown")


	def add_new_tradingplan(self,data,TEST_MODE):

		#print("adding",data)

		type_name = data["type_name"]
		algo_id = data["algo_id"]


		now = datetime.now()
		ts = now.hour*60 + now.minute 
		

		if algo_id not in self.algo_ids:

			self.algo_ids.append(algo_id)

			if type_name =="Pair":

				algo_name =  data["algo_name"]

				symbol1 = data["symbol1"] 
				symbol2 = data["symbol2"]

				ratio = data["ratio"]
				share = data["share"]
				#symbol1_share = int(data["symbol1_share"])
				#symbol2_share =  int(data["symbol2_share"])
				risk = float(data["risk"])

				symbol1_stats = {}
				symbol2_stats = {}
				#symbol1_stats = data["symbol1_statistics"]
				#symbol2_stats = data["symbol2_statistics"]
				mana = data["management"]

				name = algo_id   #symbol1[:-3]+"/"+symbol2[:-3]

				# pair reversed region. 
				# self.pair_plans

				if self.ui.pair_label_count < 5:

					if symbol1 not in self.symbol_data:
						self.symbol_data[symbol1] = Symbol(symbol1,0,0,symbol1_stats,self.pipe_ppro_out)  	

						self.symbols.append(symbol1)
						if symbol1 not in self.pair_plans:
							self.pair_plans[symbol1] = name

					if symbol2 not in self.symbol_data:
						self.symbol_data[symbol2] = Symbol(symbol2,0,0,symbol2_stats,self.pipe_ppro_out)  

						if symbol2 not in self.pair_plans:
							self.pair_plans[symbol2] = name	

						self.symbols.append(symbol2)

					#def __init__(self,name:"",Symbol1,Symbol2,ratio,share,manage_plan=None,risk=None,TEST_MODE=False,algo_name="",Manager=None):
					### name:"",symbol:Symbol1,symbol:Symbol2,share1,share2,manage_plan=None,risk=None,TEST_MODE=False,algo_name="",Manager=None
					#self,name:"",Symbol1,Symbol2,ratio,sigma=0.01,manage_plan=None,risk=None,TEST_MODE=False,algo_name="",Manager=None
					if mana==MARKETMAKING:
						print("MARKETMAKING")
						self.tradingplan[name] = PairTP_MM(name,self.symbol_data[symbol1],self.symbol_data[symbol2],ratio,data["sigma"],risk,algo_name,self)
					else:
						self.tradingplan[name] = PairTP(name,self.symbol_data[symbol1],self.symbol_data[symbol2],ratio,share,mana,risk,TEST_MODE,algo_name,self)

					self.ui.create_new_single_entry(self.tradingplan[name],type_name,None)

					self.tradingplan[name].deploy(9600)
				else:

					find_ = False
					replace_id = 0

					for trade in list(self.tradingplan.values()):

						if (trade.tkvars[STATUS].get()==PENDING or trade.tkvars[STATUS].get()==DONE) and trade.pair_plan==True and trade.in_use ==False:
							replace_id = trade.algo_ui_id
							trade.deactive()
							find_ = True
							log_print("Replacing",trade.symbol_name,"replace_id",replace_id)
							break 
					if find_:

						if symbol1 not in self.symbol_data:
							self.symbol_data[symbol1] = Symbol(symbol1,0,0,symbol1_stats,self.pipe_ppro_out)  	

							self.symbols.append(symbol1)
							if symbol1 not in self.pair_plans:
								self.pair_plans[symbol1] = name

						if symbol2 not in self.symbol_data:
							self.symbol_data[symbol2] = Symbol(symbol2,0,0,symbol2_stats,self.pipe_ppro_out)  

							if symbol2 not in self.pair_plans:
								self.pair_plans[symbol2] = name	

							self.symbols.append(symbol2)

						self.tradingplan[name] = PairTP(name,self.symbol_data[symbol1],self.symbol_data[symbol2],symbol1_share,symbol2_share,mana,risk,TEST_MODE,algo_name,self)

						self.ui.create_new_single_entry(self.tradingplan[name],type_name,replace_id)

						self.tradingplan[name].deploy(9600)

					else:

						log_print("System at full capacity.")



			elif type_name == "Single":

				algo_name =  data["algo_name"]

				symbol = data["symbol"] 
				entryplan = data["entry_type"]
				
				support = round(float(data["support"]),2)
				resistence =  round(float(data["resistence"]),2)
				risk = float(data["risk"])
				stats = {} #data["statistics"]
				status = data["immediate_deployment"]
				mana = data["management"]
			
				name = algo_id #symbol+str(ts)+ str(random.randint(0, 9))
			
				#print(support,resistence,risk)
				if self.ui.algo_count_number.get()<60:
					#print(symbol,self.ui.algo_count_number.get())
					
					if symbol not in self.symbol_data:
						self.symbol_data[symbol] = Symbol(symbol,support,resistence,stats,self.pipe_ppro_out)  #register in Symbol.
						self.symbols.append(symbol)
					#self.symbol_data[symbol].set_mind("Yet Register",DEFAULT)
						

					#######################################################################

					#def __init__(self,name:"",symbol:Symbol,entry_plan=None,manage_plan=None,support=0,resistence=0,risk=None,TEST_MODE=False,algo_name="",Manager=None):

					if mana==MARKETMAKING:
						self.tradingplan[algo_id] = TradingPlan_MMP1(name,self.symbol_data[symbol],entryplan,mana,support,resistence,risk,TEST_MODE,algo_name,self)
					else:
						self.tradingplan[algo_id] = TradingPlan(name,self.symbol_data[symbol],entryplan,mana,support,resistence,risk,TEST_MODE,algo_name,self)
					self.ui.create_new_single_entry(self.tradingplan[algo_id],type_name,None)

					if status == True:
						self.tradingplan[algo_id].deploy(9600)
				else:
					#log_print("System at full capacity.")

					find_ = False
					replace_id = 0
					for trade in list(self.tradingplan.values()):

						if (trade.tkvars[STATUS].get()==PENDING or trade.tkvars[STATUS].get()==DONE) and trade.pair_plan==False and trade.in_use ==False:

							trade.tkvars[STATUS].set("EVICTED")
							replace_id = trade.algo_ui_id

							try:
								trade.deactive()
							except Exception as e:
								log_print("deactivation problem",e)
							find_ = True
							log_print("Replacing",trade.symbol_name,"replace_id")
							break 


					if find_:
						# get rid off that tradingplan. 
						if symbol not in self.symbol_data:
							self.symbol_data[symbol]=Symbol(symbol,support,resistence,stats,self.pipe_ppro_out)  #register in Symbol.
							self.symbols.append(symbol)

						#######################################################################

						self.tradingplan[algo_id] = TradingPlan(name,self.symbol_data[symbol],entryplan,mana,support,resistence,risk,TEST_MODE,algo_name,self)
						#self.tradingplan[symbol]=TradingPlan(name,self.symbol_data[symbol],entryplan,INSTANT,mana,risk,0,TEST_MODE,algo_name,self)
						self.ui.create_new_single_entry(self.tradingplan[algo_id],type_name,replace_id)
						#self.ui.create_single_entry(self.tradingplan[symbol],replace_id)

						if status == True:
							self.tradingplan[algo_id].deploy(9600)
					else:
						log_print("System at full capacity.")


	def timer(self):

		#570  34200
		#960  57600 
		time.sleep(2)
		#now = datetime.now()
		timestamp = 34200

		log_print("timer start")

		while True:
			if self.shutdown:
				break

			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second
			remain = timestamp - ts
			#log_print(timestamp,ts)
			minute = remain//60
			seconds = remain%60

			if minute>0:
				self.ui.algo_timer_string.set(str(minute)+" M : "+str(seconds)+" S")
			else:
				self.ui.algo_timer_string.set(str(seconds)+" seconds")
			if remain<0:
				log_print("Trigger")
				break

			if self.shutdown:
				break

			time.sleep(1)

		#time.sleep(5)
		self.ui.algo_timer_string.set("Deployed")
		self.deploy_all()


		timestamp = 600
		cur_ts = 0
		while True:


			if self.shutdown:
				break

			now = datetime.now()
			ts = now.hour*60 + now.minute
			remain = timestamp - ts
			#log_print(timestamp,ts)
			hour = remain//60
			minute = remain%60

			if minute>0:
				self.ui.algo_timer_close_string.set(str(hour)+" H : "+str(minute)+" M")
			else:
				self.ui.algo_timer_close_string.set(str(minute)+" minutes")
			if remain<0:
				log_print("Trigger")
				self.withdraw_all()
				break

			self.update_stats()

		
			if ts!=cur_ts:

				checking = [i.is_alive() for i in self.processes]
				log_print("Processes Checking:",checking)

				cur_ts=ts

			time.sleep(5)


		timestamp = 955
		while True:

			now = datetime.now()
			ts = now.hour*60 + now.minute
			remain = timestamp - ts
			#log_print(timestamp,ts)
			hour = remain//60
			minute = remain%60

			if minute>0:
				self.ui.algo_timer_close_string.set(str(hour)+" H : "+str(minute)+" M")
			else:
				self.ui.algo_timer_close_string.set(str(minute)+" minutes")
			if remain<0:
				log_print("Trigger")
				self.flatten_all()
				break

			self.update_stats()

			if ts!=cur_ts:

				checking = [i.is_alive() for i in self.processes]
				log_print("Processes Checking:",checking)

				cur_ts=ts

			time.sleep(5)

		try:
			log_print("Algo manager complete")
			#self.flatten_all()
			#self.root.destroy()
		except Exception as e:
			pass

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

		for trade in list(self.tradingplan.values()):

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
			print(d)
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

				if self.ui.tick_management.get()==True:
					if d[1] == "TickHigh":

						#long cover
						self.trades_aggregation(LONG,MINUS,0.1,False,self.not_passvie)


					elif d[1] == "TickLow":

						#short cover
						self.trades_aggregation(SHORT,MINUS,0.1,False,self.not_passvie)

			elif d[0] =="basket":

				log_print("basket update:",d)

				try:
					#d[1]   => basket name 
					#d[2]   => share info. 

					self.apply_basket_cmd(d[1],d[2],d[3])

				except Exception as e:

					PrintException(e,"adding algo error")
			elif d[0] =="pkg":
				log_print("new package arrived",d)


				if self.receiving_signals.get():
					for i in d[1]:

						try:
							self.add_new_tradingplan(i,self.test_mode)

						
						except Exception as e:

							PrintException(e,"adding algo error")
				else:
					log_print("Algo rejection. deployment denied.")
			elif d[0] =="shutdown":
				break
	def ppro_in(self):
		while True:
			d = self.pipe_ppro_in.recv()

			#log_print("Ppro in:",d)

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

			elif d[0] =="order confirm":

				data = d[1]
				symbol = data["symbol"]
				price = data["price"]
				shares = data["shares"]
				side = data["side"]

				## HERE. Append it to the new symbol warehouse system. 

				#print("HOLDING UPDATE",symbol,price,shares,side)

				try:
					if symbol in self.symbols:

						if side == LONG:
							self.symbol_data[symbol].holdings_update(price,shares)

						elif side == SHORT:
							self.symbol_data[symbol].holdings_update(price,-shares)

				except	Exception	as e:
					PrintException(e,"Order confim error")

					#self.tradingplan[symbol].ppro_process_orders(price,shares,side)

				#if TEST:
					#log_print(self.tradingplan[symbol].data)

			elif d[0] =="order update":
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

			elif d[0] =='order update_m':
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

			elif d[0] =="order rejected":
  
				data = d[1]

				symbol = data["symbol"]
				side = data["side"]

				try:
					if symbol in self.symbol_data:
						self.symbol_data[symbol].rejection_message(side)
				except Exception as e:
					PrintException(e,"Order rejection error")
				# if symbol in self.tradingplan:
				# 	self.tradingplan[symbol].ppro_order_rejection()


			elif d[0] =="shutdown":
				break
			# if d[0] =="new stoporder":

			# 	self.ppro_append_new_stoporder(d[1])

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
				
	# def terminateGT(self):

	# 	if self.termination:
	# 		self.pipe_goodtrade.send("Termination")
	# 		self.termination = False
	# 	else:
	# 		print("Already terminated or not connected")

	def deploy_all(self):
		for d in list(self.tradingplan.values()):
			#print(list(self.tradingplan.values()))
			if d.data[STATUS]==PENDING:
				d.deploy()

	def withdraw_all(self):
		for d in list(self.tradingplan.values()):
			if d.in_use:
				d.cancle_deployment()

	def flatten_all(self):
		for d in list(self.tradingplan.values()):
			if d.in_use and d.data[STATUS]==RUNNING:
				d.flatten_cmd()

				
	def threaded_trades_aggregation(self,side,action,percent,positive_pnl,passive):

		log_print("All",side," ",action," ",percent*100,"%"," winning?",positive_pnl)
		if side!=None:
			self.cmd_text.set("Status: "+str(side)+" "+str(action)+" "+str(percent*100)+"%")
		if positive_pnl:
			self.cmd_text.set("Status: "+"Winning"+" "+str(action)+" "+str(percent*100)+"%")
		for d in list(self.tradingplan.values()):
			if d.in_use and d.data[STATUS]==RUNNING and d.get_management_start():
				if positive_pnl==True:
					if d.data[UNREAL] >0:
						#print("CHEKCING UNREAL",d.data[UNREAL])
						d.manage_trades(side,action,percent,passive)
				else:

					d.manage_trades(side,action,percent,passive)

	def trades_aggregation(self,side,action,percent,positive_pnl,passive):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second
		diff =  ts -self.manage_lock

		if diff>2:
			reg1 = threading.Thread(target=self.threaded_trades_aggregation,args=(side,action,percent,positive_pnl,passive,), daemon=True)
			reg1.start()
			self.manage_lock = ts
		else:
			log_print("Trades aggregation under cooldown:",diff)
			self.cmd_text.set("Status: Under CoolDown:"+str(diff))



	def cancel_all(self):
		for d in list(self.tradingplan.values()):
			d.cancel_algo()

	def export_algos(self):

		try:
			export = []

			for d in self.tradingplan.values():

				if d.tkvars[STATUS].get()==PENDING:
					entryplan = d.tkvars[ENTRYPLAN].get()
					symbol =d.symbol_name
					support = d.symbol.data[SUPPORT]
					resistence =  d.symbol.data[RESISTENCE]
					risk = d.data[ESTRISK]
					stats = d.symbol.get_stats()
					export.append([entryplan,symbol,support,resistence,risk,stats])

			with open("../../algo_setups/"+"algo_setups", 'w') as outfile:
				json.dump(export, outfile)
			self.ui.set_command_text("Export successful.")
		except Exception as e:
			log_print("Export failed:",e)
			self.ui.set_command_text("Export failed.plz send log to chiao ")

	def import_algos(self):

		try:
			with open("../../algo_setups/"+"algo_setups") as outfile:
				algo_file = json.load(outfile)

			for i in algo_file:
				self.add_new_tradingplan(i,self.test_mode)
			self.ui.set_command_text("Import successful.")
		except Exception as e:
			log_print("Import failed:",e)
			self.ui.set_command_text("Import failed.plz send log to chiao ")

	

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


	force_close_port(4441)
	multiprocessing.freeze_support()

	port =4609

	goodtrade_pipe, receive_pipe = multiprocessing.Pipe()

	algo_voxcom = multiprocessing.Process(name="algo vox1",target=algo_manager_voxcom3, args=(receive_pipe,),daemon=True)
	algo_voxcom.daemon=True


	algo_voxcom2 = multiprocessing.Process(name="algo vox2",target=httpserver, args=(receive_pipe,),daemon=True)
	algo_voxcom2.daemon=True



	ppro_in, ppro_pipe_end = multiprocessing.Pipe()

	ppro_in_manager = multiprocessing.Process(name="ppro in",target=Ppro_in, args=(port,ppro_pipe_end),daemon=True)
	ppro_in_manager.daemon=True


	ppro_out, ppro_pipe_end2 = multiprocessing.Pipe()

	ppro_out_manager = multiprocessing.Process(name="ppro out",target=Ppro_out, args=(ppro_pipe_end2,port,ppro_pipe_end,),daemon=True)
	ppro_out_manager.daemon=True


	root = tk.Tk()
	root.title("GoodTrade Algo Manager v3 b2 TICK MANAGEMENT")
	root.geometry("1500x1000")

	processes = [algo_voxcom,algo_voxcom2,ppro_in_manager,ppro_out_manager]
	manager=Manager(root,goodtrade_pipe,ppro_out,ppro_in,TEST,processes)
	#Tester(receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	print(len(sys.argv))
	if len(sys.argv)==2:
		BackTester(manager,receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	elif len(sys.argv)==3:
		Tester(receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	else:
		a=1
		algo_voxcom.start()
		algo_voxcom2.start()
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

	algo_voxcom2.terminate()
	algo_voxcom.terminate()
	ppro_in_manager.terminate()
	ppro_out_manager.terminate()

	algo_voxcom2.join()
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

