from pannel import *
from tkinter import ttk
from Symbol import *
from TradingPlan import *
from UI import *
from Ppro_in import *
from Ppro_out import *
from constant import *

from BackTester import *
from Util_functions import *
import sys
import socket
import pickle
import time
import multiprocessing
import requests
import select
from datetime import datetime
import json
import os
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

def logging(pipe):

	f = open(datetime.now().strftime("%d/%m")+".txt", "w")
	while True:
		string = pipe.recv()
		time_ = datetime.now().strftime("%H:%M:%S")
		log_print(string)
		f.write(time_+" :"+string)
	f.close()

class Manager:

	def __init__(self,root,goodtrade_pipe=None,ppro_out=None,ppro_in=None,TEST_MODE=False):

		self.root = root

		self.termination = False
		self.pipe_ppro_in = ppro_in
		self.pipe_ppro_out = ppro_out
		self.pipe_goodtrade = goodtrade_pipe

		self.test_mode = TEST_MODE

		self.symbols = []

		self.symbol_data = {}
		self.tradingplan = {}


		self.manage_lock = 0

		self.ui = UI(root,self)

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

		good = threading.Thread(target=self.goodtrade_in, daemon=True)
		good.start()
		
		ppro_in = threading.Thread(target=self.ppro_in, daemon=True)
		ppro_in.start()

		timer = threading.Thread(target=self.timer, daemon=True)
		timer.start()

		#if Testerx==True:
		
		self.pipe_ppro_out.send(["Register","QQQ.NQ"])

	#data part, UI part
	def add_new_tradingplan(self,data,TEST_MODE):

		#['Any level', 'TEST.AM', 1.0, 2.0, 5.0, {'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445}]

		entryplan = data[0]
		symbol = data[1]
		support = data[2]
		resistence =  data[3]
		risk = data[4]
		stats = data[5]

		try:
			if symbol not in self.symbols:

				if self.ui.algo_count_number.get()<50:
					#print(symbol,self.ui.algo_count_number.get())
					self.symbol_data[symbol]=Symbol(symbol,support,resistence,stats)  #register in Symbol.

					self.symbol_data[symbol].set_mind("Yet Register",DEFAULT)
					#self.tradingplan[symbol]=TradingPlan(self.symbol_data[symbol],entryplan,INCREMENTAL2,NONE,risk,self.pipe_ppro_out,TEST_MODE)

					#register in ppro
					self.pipe_ppro_out.send(["Register",symbol])
					self.symbols.append(symbol)

					#append it to, UI.

					if len(data)>6:
						status = data[6]
						mana = data[7]
						self.tradingplan[symbol]=TradingPlan(self.symbol_data[symbol],entryplan,INSTANT,NONE,risk,self.pipe_ppro_out,0,TEST_MODE)

						self.tradingplan[symbol].tkvars[MANAGEMENTPLAN].set(mana)
						self.tradingplan[symbol].tkvars[ENTYPE].set(INSTANT)

						self.ui.create_new_entry(self.tradingplan[symbol])

						if status =="deploy":
							self.tradingplan[symbol].deploy(960)
					else:
						self.tradingplan[symbol]=TradingPlan(self.symbol_data[symbol],entryplan,INSTANT,NONE,risk,self.pipe_ppro_out,1,TEST_MODE)
						self.ui.create_new_entry(self.tradingplan[symbol])

				else:
					log_print("System at full capacity.")
			else:
				log_print("symbols already exists, modifying current parameter.")
		except Exception as e:
			log_print("adding new tradingplan problem",data)
			PrintException("adding new tradingplan problem")

	def timer(self):

		#570  34200
		#960  57600 
		time.sleep(2)
		#now = datetime.now()
		timestamp = 34200

		log_print("timer start")

		while True:
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

			time.sleep(1)

		self.ui.algo_timer_string.set("Deployed")
		self.deploy_all()

		timestamp = 965
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
				break

			## UPPDAtes


			self.update_stats()


			time.sleep(5)

		self.root.destroy()


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




		for trade in self.tradingplan.values():

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


	def goodtrade_in(self):
		time.sleep(3)
		count = 0
		while True:
			d = self.pipe_goodtrade.recv()
			#print(d)
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
					log_print(e)
			if d[0] =="pkg":
				log_print("new package arrived",d)

				try:
					for i in d[1]:
						self.add_new_tradingplan(i,self.test_mode)
				except Exception as e:
					log_print("adding algo errors:",e,i)

	def ppro_order_confirmation(self,data):

		symbol = data["symbol"]
		price = data["price"]
		shares = data["shares"]
		side = data["side"]

		if symbol in self.tradingplan:
			log_print("order",symbol,"side:",side,"shares",shares,"price",price)

			self.tradingplan[symbol].ppro_process_orders(price,shares,side)
		else:
			log_print("irrelavant orders detected,",symbol,shares,side)

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
						# re-register the symbols
				except Exception as e:
					log_print(e)

			elif d[0] =="ppro_out":

				try:
					self.ui.ppro_out_status.set(str(d[1]))

					if str(d[1])=="Connected":
						self.ui.ppro_status_out["background"] = "#97FEA8"
					else:
						self.ui.ppro_status_out["background"] = "red"
				except Exception as e:
					log_print(e)

			elif d[0] =="msg":
				log_print(d[1])

			elif d[0] =="order confirm":

				data = d[1]
				symbol = data["symbol"]
				price = data["price"]
				shares = data["shares"]
				side = data["side"]

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_process_orders(price,shares,side)

				#if TEST:
					#log_print(self.tradingplan[symbol].data)

			elif d[0] =="order update":
				data = d[1]
				symbol = data["symbol"]
				bid = data["bid"]
				ask = data["ask"]
				ts = data["timestamp"]

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_update_price(bid,ask,ts)

			elif d[0] =='order update_m':
				data = d[1]
				symbol = data["symbol"]
				bid = data["bid"]
				ask = data["ask"]
				ts = data["timestamp"]

				techindicator = d[2]

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_update_price(bid,ask,ts)
					self.tradingplan[symbol].symbol.update_techindicators(techindicator)
				### UPDATE THE EMAs. 

			elif d[0] =="order rejected":

				if symbol in self.tradingplan:
					self.tradingplan[symbol].ppro_order_rejection()

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
		for d in self.tradingplan.values():
			d.deploy()

	def withdraw_all(self):
		for d in self.tradingplan.values():
			d.cancle_deployment()

	def flatten_all(self):
		for d in self.tradingplan.values():
			d.flatten_cmd()

	def trades_aggregation(self,side,action,percent,positive_pnl):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		diff =  ts -self.manage_lock
		if diff>5:

			log_print("All",side," ",action," ",percent*100,"%")
			for d in self.tradingplan.values():
				if positive_pnl==True:
					if d.data[UNREAL] >0:
						print(d.data[UNREAL])
						d.manage_trades(side,action,percent)
				else:
					d.manage_trades(side,action,percent)

			self.manage_lock = ts
		log_print("Trades aggregation under cooldown:",diff)

	def cancel_all(self):
		for d in self.tradingplan.values():
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

	
class Tester:

	def __init__(self,receive_pipe,ppro_in,ppro_out):

		now = datetime.now()

		self.sec =  now.hour*3600 + now.minute*60 + now.second
		print(self.sec)
		self.bid=0
		self.ask=0
		self.data = {}
		self.root = tk.Toplevel(width=780,height=250)
		self.gt = receive_pipe
		self.ppro = ppro_in

		self.ppro_out = ppro_out

		self.pos  = ""
		self.share = 0
		self.change_sum = 0

		self.wait_time = 1

		self.buy_book = {}
		self.sell_book = {}

		self.price_stay = True
		self.price_flip = True

		# self.init= tk.Button(self.root ,text="Register",width=10,bg="#5BFF80",command=self.start_test)
		# self.init.grid(column=1,row=1) m

		self.price = tk.DoubleVar(value=412.55)

		tk.Entry(self.root ,textvariable=self.price,width=10).grid(column=1,row=2)	

		tk.Button(self.root ,text="up",command=self.price_up).grid(column=1,row=4)	
		tk.Button(self.root ,text="stay",command=self.price_stayx).grid(column=2,row=4)	
		tk.Button(self.root ,text="down",command=self.price_down).grid(column=3,row=4)	

		tk.Button(self.root ,text="TimeX1",command=self.time_facotr_1).grid(column=1,row=3)
		tk.Button(self.root ,text="TimeX10",command=self.time_factor_10).grid(column=2,row=3)	

		tk.Button(self.root ,text="up 0.1",command=self.price_up_little).grid(column=1,row=5)
		tk.Button(self.root ,text="down 0.1",command=self.price_down_little).grid(column=2,row=5)	

		tk.Button(self.root ,text="up 1",command=self.price_upx).grid(column=1,row=6)	
		tk.Button(self.root ,text="down 1",command=self.price_downx).grid(column=2,row=6)	

		tk.Button(self.root ,text="add 1 share",command=self.add1).grid(column=1,row=7)	
		tk.Button(self.root ,text="sub 1 share",command=self.sub1).grid(column=2,row=7)	
		self.gt.send(["pkg",[[BREAKFIRST, 'SPY.AM', 412, 413, 50.0, {'ATR': 3.69, 'OHavg': 1.574, 'OHstd': 1.545, 'OLavg': 1.634, 'OLstd': 1.441,"expected_momentum":2}]]])

		time.sleep(1)
		wish_granter = threading.Thread(target=self.wish, daemon=True)
		wish_granter.start()

		price_changer = threading.Thread(target=self.price_changer, daemon=True)
		price_changer.start()

	def wish(self): #a sperate process. GLOBALLY. 
		while True:
			try:
				d = self.ppro_out.recv()
				log_print("PPRO order:",d)
				type_ = d[0]

				#time.sleep(1)
				if type_ == "Buy" or type_ == IOCBUY:

					symbol = d[1]
					share = d[2]
					rationale = d[3]

					if self.share ==0:
						self.pos = LONG

					if self.pos ==LONG or self.pos=="":
						self.share +=share
					elif self.pos ==SHORT:
						self.share -=share

					data ={}
					data["symbol"]= symbol
					data["side"]= LONG
					data["price"]= float(self.ask)
					data["shares"]= int(share)
					data["timestamp"]= self.sec
					self.ppro.send(["order confirm",data])

				elif type_ =="Sell" or type_ == IOCSELL:

					symbol = d[1]
					share = d[2]
					rationale = d[3]

					if self.share ==0:
						self.pos = SHORT

					if self.pos ==SHORT or self.pos=="":
						self.share +=share
					elif self.pos ==LONG:
						self.share -=share

					data ={}
					data["symbol"]= symbol
					data["side"]= SHORT
					data["price"]= float(self.bid)
					data["shares"]= int(share)
					data["timestamp"]= self.sec
					self.ppro.send(["order confirm",data])


				elif type_ == LIMITBUY:
					symbol = d[1]
					price = d[2]
					share = d[3]

					self.buy_book[price] = share
				elif type_ == LIMITSELL:
					symbol = d[1]
					price = d[2]
					share = d[3]

					self.sell_book[price] = share
				elif type_ == "Flatten":

					symbol = d[1]
					if self.pos ==LONG:
						data ={}
						data["symbol"]= symbol
						data["side"]= SHORT
						data["price"]= float(self.bid)
						data["shares"]= int(self.share)
						data["timestamp"]= self.sec
						self.ppro.send(["order confirm",data])
					else:
						data ={}
						data["symbol"]= symbol
						data["side"]= LONG
						data["price"]= float(self.bid)
						data["shares"]= int(self.share)
						data["timestamp"]= self.sec
						self.ppro.send(["order confirm",data])
					self.share = 0
					self.pos =""
			except Exception as e:
				log_print(e)

	def add1(self):
		data = {}
		data["symbol"]= "SPY.AM"
		data["side"]= LONG
		data["price"]= float(self.ask)
		data["shares"]= int(1)
		data["timestamp"]= self.sec
		self.ppro.send(["order confirm",data])

	def sub1(self):
		data = {}
		data["symbol"]= "SPY.AM"
		data["side"]= SHORT
		data["price"]= float(self.ask)
		data["shares"]= int(1)
		data["timestamp"]= self.sec
		self.ppro.send(["order confirm",data])

	def price_changer(self):
		while True:
			self.price.set(round(self.price.get()+self.change_sum,2))
			self.change()
			time.sleep(self.wait_time)

	def price_stayx(self):
		#print("stay")
		self.price_stay = True
		self.change_sum = 0
		

	def time_facotr_1(self):
		self.wait_time=1

	def time_factor_10(self):
		self.wait_time=0.02

	def time_factor_50(self):
		self.wait_time=0.1

	def price_up(self):
		self.price_stay = False
		self.change_sum = 0.01
		# self.price.set(round(self.price.get()+0.1,2))
		# self.change()
	def price_down(self):
		self.price_stay = False
		self.change_sum = -0.01

		# self.price.set(round(self.price.get()-0.1,2))
		# self.change()

	def price_up_little(self):
		self.price.set(round(self.price.get()+0.1,2))
		self.change()

	def price_down_little(self):
		self.price.set(round(self.price.get()-0.1,2))
		self.change()

	def price_upx(self):
		self.price.set(round(self.price.get()+1,2))
		self.change()

	def price_downx(self):
		self.price.set(round(self.price.get()-1,2))
		self.change()

	def change(self):
		self.sec+=1
		#print(self.sec)

		

		if self.price_stay:
			if self.price_flip:
				self.price.set(round(self.price.get()+0.01,2))
				self.price_flip = False
			else:
				self.price.set(round(self.price.get()-0.01,2))
				self.price_flip = True
			#print("hello")

		self.bid = round(float(self.price.get()-0.01),2)
		self.ask = round(float(self.price.get()+0.01),2)

		# data["symbol"]= "SPY.AM"
		# data["bid"]= round(float(self.price.get()-0.01),2)
		# data["ask"]= round(float(self.price.get()+0.01),2)
		# data["timestamp"]= self.sec

		#self.ppro.send(["order update",data])

		self.decode_l1("SPY.AM",self.bid,self.ask,self.sec,self.ppro,self.data)
		self.limit_buy_sell()

	def decode_l1(self,symbol,bid,ask,ts,pipe,l1data):

		#ts= timestamp_seconds(find_between(stream_data, "MarketTime=", ",")[:-4])

		ms = ts//60

		send = False

		if symbol in l1data:
			#if either level has changed. register. 
			if l1data[symbol]["bid"]!=bid or l1data[symbol]["ask"]!=ask:
				send = True
			elif ts-l1data[symbol]["timestamp"] >1:
				send = True

			#if has been more then 2 leconds. registered.

		else:
			l1data[symbol] = {}

			l1data[symbol]["symbol"] = symbol
			l1data[symbol]["bid"] = bid
			l1data[symbol]["ask"] = ask
			l1data[symbol]["timestamp"] = ts

			l1data[symbol]["internal"] = {}
			l1data[symbol]["internal"]["timestamp"] = ms
			l1data[symbol]["internal"]["current_minute_bins"] = [bid,ask]
			l1data[symbol]["internal"]["EMA_count"] = 0

			#Realizing - I won't need to track these values no more.
			l1data[symbol]["internal"]["high"] = ask
			l1data[symbol]["internal"]["low"] = bid
			l1data[symbol]["internal"]["open"] = ask
			l1data[symbol]["internal"]["close"] = bid

			l1data[symbol]["internal"]["EMA_count"] = 0

			l1data[symbol]["internal"]["EMA5H"] = 0
			l1data[symbol]["internal"]["EMA5L"] = 0
			l1data[symbol]["internal"]["EMA5C"] = 0

			l1data[symbol]["internal"]["EMA8H"] = 0
			l1data[symbol]["internal"]["EMA8L"] = 0
			l1data[symbol]["internal"]["EMA8C"] = 0


			l1data[symbol]["internal"]["EMA21H"] = 0
			l1data[symbol]["internal"]["EMA21L"] = 0
			l1data[symbol]["internal"]["EMA21C"] = 0

			send = True

		#process the informations. process internal only. 

		#two kinds of update. normal second; and new second. 
		if send:

			update = process_l1(l1data[symbol]["internal"],bid,ask,ms)
			"""two cases. small, and big."""
			l1data[symbol]["symbol"] = symbol
			l1data[symbol]["bid"] = bid
			l1data[symbol]["ask"] = ask
			l1data[symbol]["timestamp"] = ts

			if update:
				update_ = {}
				update_["EMA5H"]=l1data[symbol]["internal"]["EMA5H"]
				update_["EMA5L"]=l1data[symbol]["internal"]["EMA5L"]
				update_["EMA5C"]=l1data[symbol]["internal"]["EMA5C"]
				update_["EMA8H"]=l1data[symbol]["internal"]["EMA8H"]
				update_["EMA8L"]=l1data[symbol]["internal"]["EMA8L"]
				update_["EMA8C"]=l1data[symbol]["internal"]["EMA8C"]

				update_["EMA21H"]=l1data[symbol]["internal"]["EMA21H"]
				update_["EMA21L"]=l1data[symbol]["internal"]["EMA21L"]
				update_["EMA21C"]=l1data[symbol]["internal"]["EMA21C"]

				update_["EMAcount"]=l1data[symbol]["internal"]["EMA_count"]
				pipe.send(["order update_m",l1data[symbol],update_])

				#print(l1data[symbol])
				# writer.writerow([symbol,mili_ts,bid,ask,\
				# 	l1data[symbol]["internal"]["EMA5H"],\
				# 	l1data[symbol]["internal"]["EMA5L"],\
				# 	l1data[symbol]["internal"]["EMA5C"],\
				# 	l1data[symbol]["internal"]["EMA8H"],\
				# 	l1data[symbol]["internal"]["EMA8L"],\
				# 	l1data[symbol]["internal"]["EMA8C"]])
				#print(symbol,l1data[symbol],update_)
			else:

				#print(l1data[symbol])
				#add time
				pipe.send(["order update",l1data[symbol]])
				#writer.writerow([symbol,mili_ts,bid,ask])


	def process_l1(dic,bid,ask,ms):

		"""two senarios. within current timestamp, and out. """

		if dic["timestamp"]  != ms: #a new minute. 

			dic["timestamp"] = ms
			if len(dic["current_minute_bins"])>1:
				dic["high"]=max(dic["current_minute_bins"])
				dic["low"]=min(dic["current_minute_bins"])
				dic["open"]=dic["current_minute_bins"][0]
				dic["close"]=dic["current_minute_bins"][-1]

				dic["current_minute_bins"] = []

				if dic["EMA_count"]==0: #first time setting up.
					### HERE. What i need to do is have the GT&server also track the EMA values of these. 
					dic["EMA5H"] = dic["high"]
					dic["EMA5L"] = dic["low"]
					dic["EMA5C"] = dic["close"]

					dic["EMA8H"] = dic["high"]
					dic["EMA8L"] = dic["low"]
					dic["EMA8C"] = dic["close"]

				else: #induction! 
					dic["EMA5H"] = self.new_ema(dic["high"],dic["EMA5H"],5)
					dic["EMA5L"] = self.new_ema(dic["low"],dic["EMA5L"],5)
					dic["EMA5C"] = self.new_ema(dic["close"],dic["EMA5C"],5)

					dic["EMA8H"] = self.new_ema(dic["high"],dic["EMA8H"],8)
					dic["EMA8L"] = self.new_ema(dic["low"],dic["EMA8L"],8)
					dic["EMA8C"] = self.new_ema(dic["close"],dic["EMA8C"],8)

					dic["EMA21H"] = new_ema(dic["high"],dic["EMA21H"],21)
					dic["EMA21L"] = new_ema(dic["low"],dic["EMA21L"],21)
					dic["EMA21C"] = new_ema(dic["close"],dic["EMA21C"],21)
					
				dic["EMA_count"]+=1
				return True
			else:
				return False
		else: #same minute 
			dic["current_minute_bins"].append(bid)
			dic["current_minute_bins"].append(ask)
			return False
			
	def new_ema(self,current,last_EMA,n):
	    
	    return round((current - last_EMA)*(2/(n+1)) + last_EMA,2)

	def limit_buy_sell(self):

		used = []
		for key,item in self.buy_book.items():
			if self.bid <= key:
				data={}
				data["symbol"]= "SPY.AM"
				data["side"]= LONG
				data["price"]= float(self.ask)
				data["shares"]= self.buy_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share -= data["shares"]

				used.append(key)

		for i in used:
			del self.buy_book[i]

		used = []
		for key,item in self.sell_book.items():
			if self.ask >= key:
				data={}
				data["symbol"]= "SPY.AM"
				data["side"]= SHORT
				data["price"]= float(self.bid)
				data["shares"]= self.sell_book[key]
				data["timestamp"]= self.sec
				self.ppro.send(["order confirm",data])
				self.share-= data["shares"]
				used.append(key)

		for i in used:
			del self.sell_book[i]
	

if __name__ == '__main__':


	multiprocessing.freeze_support()

	port =4609

	goodtrade_pipe, receive_pipe = multiprocessing.Pipe()

	algo_voxcom = multiprocessing.Process(target=algo_manager_voxcom, args=(receive_pipe,),daemon=True)
	algo_voxcom.daemon=True


	ppro_in, ppro_pipe_end = multiprocessing.Pipe()

	ppro_in_manager = multiprocessing.Process(target=Ppro_in, args=(port,ppro_pipe_end),daemon=True)
	ppro_in_manager.daemon=True


	ppro_out, ppro_pipe_end2 = multiprocessing.Pipe()

	ppro_out_manager = multiprocessing.Process(target=Ppro_out, args=(ppro_pipe_end2,port,ppro_pipe_end,),daemon=True)
	ppro_out_manager.daemon=True


	root = tk.Tk()
	root.title("GoodTrade Algo Manager v2 b11 Pampa")
	root.geometry("1920x800")

	manager=Manager(root,goodtrade_pipe,ppro_out,ppro_in,TEST)
	print(len(sys.argv))
	if len(sys.argv)==2:
		BackTester(manager,receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	elif len(sys.argv)==3:
		Tester(receive_pipe,ppro_pipe_end,ppro_pipe_end2)
	else:
		algo_voxcom.start()
		ppro_out_manager.start()
		ppro_in_manager.start()		


	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()


	algo_voxcom.terminate()
	ppro_in_manager.terminate()
	ppro_out_manager.terminate()


	algo_voxcom.join()
	ppro_in_manager.join()
	ppro_out_manager.join()
	print("All subprocesses terminated")
	
	os._exit(1) 
	print("exit")