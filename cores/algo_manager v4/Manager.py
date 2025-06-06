from pannel import *
from tkinter import ttk
import tkinter as tk 
from Symbol import *

from TradingPlan_Basket import *


from UI import *
from Ppro_in import *
from Ppro_out import *
from constant import *

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
		self.symbol_data = {}

		self.baskets = {}

		self.processes = processes
	
		self.algo_ids = []

		self.manage_lock = 0



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
		self.current_summary['cur_exp'] = tk.DoubleVar()
		self.current_summary['max_exp'] = tk.DoubleVar()

		self.user = tk.StringVar(value="User:")

		""" UI """
		self.receiving_signals = tk.BooleanVar(value=True)
		self.cmd_text = tk.StringVar(value="Status:")

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
		self.file = "../../algo_records/"+now.strftime("%Y_%m")+".csv"

		self.init_record_writer()

		self.shutdown=False

		self.symbol_inspection_lock = threading.Lock()

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
#
	#data part, UI part

	def shutdown_all_threads(self):

		self.shutdown= True


	def check_all_pnl(self):
		tps = list(self.baskets.keys())
		for tp in tps:
			self.baskets[tp].check_pnl()

	def symbols_inspection(self):

		if self.symbol_inspection_lock.locked()==False:

			if self.total_difference !=0:
				self.pipe_ppro_out.send([CANCELALL])

			self.total_difference = 0
			
			# residue.
			# if residue is 0. no more cancel. 
			with self.symbol_inspection_lock:
				symbols = list(self.symbol_data.values())

				for val in symbols:

					try:
						val.symbol_inspection()
						self.total_difference+=abs(val.get_difference())
					except Exception as e:
						PrintException(e,"inspection error")

			log_print("Manager: performing symbols inspection compelte, total difference:",self.total_difference)
		else:
			log_print("Manager: previous symbols inspection not finished. skip.")


	def apply_basket_cmd(self,basket_name,orders,risk,aggresive):


		if basket_name not in self.baskets:

			if self.ui.basket_label_count<40:
				self.baskets[basket_name] = TradingPlan_Basket(basket_name,risk,self)
				self.ui.create_new_single_entry(self.baskets[basket_name],"Basket",None)

				self.baskets[basket_name].deploy()
		

		if self.baskets[basket_name].shut_down==False:
			for symbol,value in orders.items():

				if "." in symbol:

					print("Manager: Applying basket command",symbol,value)
					if symbol not in self.symbol_data:
						self.symbol_data[symbol] = Symbol(self,symbol,self.pipe_ppro_out)  #register in Symbol.
						self.symbols.append(symbol)

					self.baskets[basket_name].register_symbol(symbol,self.symbol_data[symbol])

					## now , submit the request.

					self.baskets[basket_name].submit_expected_shares(symbol,value,aggresive)
				else:
					log_print("Manager: Wrong Ticker format:",symbol)
		else:
			log_print(basket_name,"already shutdown")



	def timer(self):

		# #570  34200
		# #960  57600 
		# time.sleep(2)
		# #now = datetime.now()
		# timestamp = 34200

		# log_print("timer start")

		# while True:
		# 	if self.shutdown:
		# 		break

		# 	now = datetime.now()
		# 	ts = now.hour*3600 + now.minute*60 + now.second
		# 	remain = timestamp - ts
		# 	#log_print(timestamp,ts)
		# 	minute = remain//60
		# 	seconds = remain%60

		# 	if minute>0:
		# 		self.ui.algo_timer_string.set(str(minute)+" M : "+str(seconds)+" S")
		# 	else:
		# 		self.ui.algo_timer_string.set(str(seconds)+" seconds")
		# 	if remain<0:
		# 		log_print("Trigger")
		# 		break

		# 	if self.shutdown:
		# 		break

		# 	time.sleep(1)

		#time.sleep(5)
		# self.ui.algo_timer_string.set("Deployed")
		# self.deploy_all()


		# timestamp = 600
		# cur_ts = 0
		# while True:
		# 	if self.shutdown:
		# 		break

		# 	now = datetime.now()
		# 	ts = now.hour*60 + now.minute
		# 	remain = timestamp - ts
		# 	#log_print(timestamp,ts)
		# 	hour = remain//60
		# 	minute = remain%60

		# 	if minute>0:
		# 		self.ui.algo_timer_close_string.set(str(hour)+" H : "+str(minute)+" M")
		# 	else:
		# 		self.ui.algo_timer_close_string.set(str(minute)+" minutes")
		# 	if remain<0:
		# 		log_print("Trigger")
		# 		self.withdraw_all()
		# 		break

		# 	self.update_stats()

		
		# 	if ts!=cur_ts:

		# 		checking = [i.is_alive() for i in self.processes]
		# 		log_print("Processes Checking:",checking)

		# 		cur_ts=ts

		# 	time.sleep(5)


		# timestamp = 955

		# while True:

		# 	now = datetime.now()
		# 	ts = now.hour*60 + now.minute
		# 	remain = timestamp - ts
		# 	#log_print(timestamp,ts)
		# 	hour = remain//60
		# 	minute = remain%60

		# 	if minute>0:
		# 		self.ui.algo_timer_close_string.set(str(hour)+" H : "+str(minute)+" M")
		# 	else:
		# 		self.ui.algo_timer_close_string.set(str(minute)+" minutes")
		# 	if remain<0:
		# 		log_print("Trigger")
		# 		self.flatten_all()
		# 		break

		# 	self.update_stats()

		# 	if ts!=cur_ts:

		# 		checking = [i.is_alive() for i in self.processes]
		# 		log_print("Processes Checking:",checking)

		# 		cur_ts=ts

		# 	time.sleep(5)

		# try:
		# 	log_print("Algo manager complete")
		# 	#self.flatten_all()
		# 	#self.root.destroy()
		# except Exception as e:
		# 	pass
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

			elif d[0] =="basket":

				log_print("basket update:",d)

				try:
					#d[1]   => basket name 
					#d[2]   => share info. 
					print(d[1],d[2],d[3],d[4])
					self.apply_basket_cmd(d[1],d[2],d[3],d[4])

				except Exception as e:

					PrintException(e,"adding basket error")

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

					if count%3==0:
						handl = threading.Thread(target=self.symbols_inspection,daemon=True)
						handl.start()
				except Exception as e:
					PrintException(e, " POSITION UPDATE ERROR")

			elif d[0] == SYMBOL_UPDATE:
				# d= {}
				# d['time'] = time_
				# d['symbol'] = symbol
				# d['lastPrice'] = lastPrice
				# d['l1AskPrice'] = l1AskPrice
				# d['l1BidPrice'] = l1BidPrice


				# here I update the symbol instead. 
				# and then the symbol update each of the tradingplan bound to it. 

				#print(symbol,bid,ask,ts)

				try:

					data = d[1]
					symbol = data["symbol"]
					bid = data["l1BidPrice"]
					ask = data["l1AskPrice"]
					ts = data["timestamp"]

					if symbol in self.symbols:
						self.symbol_data[symbol].update_price(bid,ask,ts)

					#self.ui.ppro_last_update.set(ts)
				except	Exception	as e:
					PrintException(e,"Order update error")

			elif d[0] == SUMMARY_UPDATE:

				now = datetime.now()
				cur_ts = now.hour*3600+now.minute*60+now.second

				data = d[1]

				# d['net'] = net
				# d['fees'] = fees
				# d['trades'] = trades
				# d['sizeTraded'] = sizeTraded
				# d['unrealizedPlusNet'] = unrealizedPlusNet
				# d['timestamp'] = ts
				# d['unrealized'] = unrealized	

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

				try:
					if symbol in self.symbol_data:
						self.symbol_data[symbol].rejection_message(side)
				except Exception as e:
					PrintException(e,"Order rejection error")
				# if symbol in self.tradingplan:
				# 	self.tradingplan[symbol].ppro_order_rejection()


			elif d[0] =="shutdown":
				break


			elif d[0] =="order confirm":  ### DEPRECATED. 

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

	def init_record_writer(self):

		try:
			self.f = open(self.file, "r")
		except:
			self.f = open(self.file, "w")
			self.recordwriter = csv.writer(self.f,lineterminator = '\n')
			self.recordwriter.writerow(['DATE', 'TIME','ALGO','REALIZED'])

		self.f.close()
		log_print(("record file start"))

	def new_record(self,tradingplan):

		try:
			self.f = open(self.file, "a")
			self.recordwriter = csv.writer(self.f,lineterminator = '\n')

			now = datetime.now()
			DATE = now.strftime("%Y-%m-%d")
			TIME = now.strftime("%H:%M:%S")


			ALGO = tradingplan.algo_name
			real = tradingplan.data[REALIZED]

			self.recordwriter.writerow([DATE, TIME,ALGO,real])
			self.f.close()
		except:

			log_print("writing record failure for",tradingplan.symbol_name)
		

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
	root.title("GoodTrade Algo Manager v4 b6 ")
	root.geometry("950x800")

	processes = [algo_voxcom,algo_voxcom2,ppro_in_manager,ppro_out_manager]
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

