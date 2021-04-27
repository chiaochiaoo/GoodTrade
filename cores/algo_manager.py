import tkinter as tk
from tkinter import ttk

import socket
import pickle
import pandas as pd
import time
import multiprocessing
import threading
from pannel import *
import time
from queue import Queue
import requests
from datetime import datetime
import os

from algo_ppro_manager import *
from hex_functions import *


GREEN = "#97FEA8"
DEFAULT = "#d9d9d9"
LIGHTYELLOW = "#fef0b8"
YELLOW =  "#ECF57C"
STRONGGREEN = "#3DFC68"
STRONGRED = "#FC433D"
DEEPGREEN = "#059a12"

global coecoefficient
coefficient = 1


#Thoughts:
#Combine PPRO sutff with VOXCOM into one process.

#Create subclass for the algo manager.

#Entry strategy 

#Manage strategy

#How to get the machine to read chart?


def algo_manager_voxcom(pipe):

	#tries to establish commuc
	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		PORT = 65499       # The port used by the server

		try:
			print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					s.connect((HOST, PORT))
					connected = True
				except:
					pipe.send(["msg","Disconnected"])
					print("Cannot connected. Try again in 2 seconds.")
					time.sleep(2)

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
						except:
							pass
				#s.sendall(pickle.dumps(["ids"]))

				pipe.send(["pkg",k])
				s.send(pickle.dumps(["Algo placed",k[2]]))
			print("Server disconnected")
			pipe.send(["msg","Server disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			print(e)

class algo_manager(pannel):

	def __init__(self,root,port,gt_pipe,order_pipe,order_send_pipe):  #send stuff via recv and take from order_pipe.


		self.status={"Canceled":"Canceled","Done":"Done","Running":"Running","Pending":"Pending","Deployed":"Deployed","Rejected":"Rejected","Deploying":"Deploying"}

		self.stoporder_book = []
		self.stoporder_book_lock = threading.Lock()
		self.stoporder_to_id ={}
		self.id_to_stoporder = {}

		self.used_stoporder = {}

		self.pipe = gt_pipe
		self.order_pipe = order_pipe

		self.order_send_pipe = order_send_pipe

		self.port = port
		self.symbols = []  #all registered symbols
		self.symbols_orders = {} #all the orders which a symbols contain

		#a list of all id.
		self.orders_registry = []
		self.orders_symbol = {}   # ID -> Symbol

		# Symbol+Side = id. 
		self.order_book = {}

		self.stoporder = {}
		# SYMBOL ATTRIBUTE. Getting symbol -> ID 
		self.running_order = {} #one symbol -> just 1 order.

		self.activated_order = {} #one symbol -> at most 2 orders. 

		#self.algo_status = {} #Pending, Running,Cancled,Complete.
		#self.order_status = {}

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=["symbol","algo_status","description","AR","break_at","stoplevel","position","act_r/est_r","average_price","shares","AM","pxtgt1","pxtgt2","pxtgt3","unrealized_pshr","unrealized","realized"]

		self.order_tkstring = {}
		self.order_tklabels = {}

		self.data_list = {}

		#needed. 

		self.break_at = {}
		self.stoplevel = {}

		self.realized = {}
		self.current_share = {}
		self.target_share = {}
		self.unrealized = {}
		self.unrealized_pshr ={}
		self.average_price = {}

		self.auto_manage = {}
		self.price_levels = {}
		self.price_current_level = {}

		self.id_lock = {}

		self.act_risk= {}
		self.est_risk = {}

		self.position = {}


		self.holdings= {}  ###literally have that many shares. 

		self.order_info = {}


		self.current_ask = {}
		self.current_bid = {}

		self.flatten_lock = {}
		
		super().__init__(root)

		self.init_pannel()

		receiver = threading.Thread(target=self.receive, daemon=True)
		receiver.start()

		receiver2 = threading.Thread(target=self.order_pipe_listener, daemon=True)
		receiver2.start()

		self.in_progress = False

		timer = threading.Thread(target=self.timer, daemon=True)
		timer.start()

	#UI COMPONENT


	def timer(self):

		#570  34200
		#960  57600 
		time.sleep(2)
		#now = datetime.now()
		timestamp = 34185

		print("timer start")
		while True:
			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second
			remain = timestamp - ts

			minute = remain//60
			seconds = remain%60

			print(minute,seconds)
			if minute>0:
				self.algo_timer_string.set(str(minute)+" minutes and "+str(seconds)+" seconds")
			else:
				self.algo_timer_string.set(str(seconds)+" seconds")
			if remain<0:
				print("Trigger")
				break

			time.sleep(1)

		self.algo_timer_string.set("Deployed")
		self.deploy_all_stoporders()

	def init_pannel(self):

		# self.width = [10,10,30,8,8,8,8,8,8,8,6]
		# self.labels = []

		self.labels = {"Symbol":10,\
						"Algo status":10,\
						"description":25,\
						"AR":4,\
						"Break at":8,\
						"Stop level":8,\
						"Position":8,\
						"Act R/Est R":8,\
						"AvgPx":10,\
						"SzIn":8,\
						"AM":4,\
						"PxTgt 1":8,\
						"PxTgt 2":8,\
						"PxTgt 3":8,\
						"UPshr":8,\
						"U":8,\
						"R":8,\
						"flatten":10}

		self.width = list(self.labels.values())

		self.setting = ttk.LabelFrame(root,text="Algo Manager v1") 
		self.setting.place(x=10,y=10,height=250,width=180)


		self.main_app_status = tk.StringVar()
		self.main_app_status.set("Main :")

		self.ppro_status = tk.StringVar()
		self.ppro_status.set("Ppro :")



		self.algo_count_number = 0
		# self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))

		# self.algo_count_ = ttk.Label(self.setting, textvariable=self.algo_count_string)
		# self.algo_count_.grid(column=1,row=5,padx=10)

		self.main_status = ttk.Label(self.setting, textvariable=self.main_app_status)
		self.main_status.grid(column=1,row=1,padx=10)
		#self.main_status.place(x = 20, y =12)

		self.ppro_status_ = ttk.Label(self.setting, textvariable=self.ppro_status)
		self.ppro_status_.grid(column=1,row=2,padx=10)
		#self.ppro_status_.place(x = 20, y =32)

		self.algo_count_string = tk.StringVar()

		self.algo_timer_string = tk.StringVar()

		self.timerc = ttk.Label(self.setting, text="Opening Algos deploy in:")
		self.timerc.grid(column=1,row=3,padx=10)
		self.timersx = ttk.Label(self.setting,  textvariable=self.algo_timer_string)
		self.timersx.grid(column=1,row=4,padx=10)



		self.algo_deploy = ttk.Button(self.setting, text="Deploy all algo",command=self.deploy_all_stoporders)
		self.algo_deploy.grid(column=1,row=6)

		self.algo_cancel = ttk.Button(self.setting, text="Unmount all algo",command=self.cancel_all_stoporders)
		self.algo_cancel.grid(column=1,row=7)

		# self.algo_cancel = ttk.Button(self.setting, text="Flatten all algo",command=self.cancel_all_stoporders)
		# self.algo_cancel.grid(column=1,row=6)

		# self.algo_cancel = ttk.Button(self.setting, text="Cancel all algo",command=self.cancel_all_stoporders)
		# self.algo_cancel.grid(column=1,row=7)

		self.total_u = tk.StringVar()
		self.total_r = tk.StringVar()

		self.log_panel = ttk.LabelFrame(root,text="Logs") 
		self.log_panel.place(x=10,y=250,relheight=0.8,width=180)

		self.deployment_panel = ttk.LabelFrame(root,text="Algo deployment") 
		self.deployment_panel.place(x=200,y=10,relheight=0.8,width=1400)

		self.dev_canvas = tk.Canvas(self.deployment_panel)
		self.dev_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.deployment_panel)
		self.scroll.config(orient=tk.VERTICAL, command=self.dev_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.dev_canvas.configure(yscrollcommand=self.scroll.set)

		self.deployment_frame = tk.Frame(self.dev_canvas)
		self.deployment_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.dev_canvas.create_window(0, 0, window=self.deployment_frame, anchor=tk.NW)


		self.rebind(self.dev_canvas,self.deployment_frame)
		self.recreate_labels()
		#test
		# for i in range(40):
		# 	self.order_creation(['id', str(i), str(i), 20, 20.0,"Long",1,1,1,1,1,1,[1,1,1,1,1,1,1,1,1,1,1,1,1]])

	def cancel_all(self):

		for i in self.orders_registry:
				print(i)

	def flatten_symbol(self,symbol,id_=None,status_text=None):

		#check if this order is running.
		running = self.check_order_running(id_,symbol)

		#send once is good enough. 
		if running:
			flatten = threading.Thread(target=flatten_symbol,args=(symbol,), daemon=True)
			flatten.start()
			#self.current_share_data[id_]=0

		else:
			if id_!= None and status_text!= None:
				if id_ in self.orders_registry:
					self.orders_registry.remove(id_)

					#if current order is not running. 
					self.mark_off_algo(id_,self.status["Canceled"])
					# current_status = status_text.get()
					# if current_status=="Pending":
					# 	status_text.set("Canceled")
					# 	self.modify_algo_count(-1)
					# else:
					# 	status_text.set("Done.")

	def order_creation(self,d):

		#['New order', 'Break up2268503', 'Break up', 'QQQ.NQ', 'Pending', 'Breakout on Resistance on 338.85 for 0 sec', 'Long', 'Market', '338.85', '2104', 5050.0]

		#need stop level. 
		id_,symbol,type_,status,des,pos,order_type,order_price,share,risk,stoplevel,data_list = d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10],d[11],d[12]

		if pos =="Long": side ="B"
		elif pos =="Short": side ="S"
	
		print(id_,"added to new order")
		
		if id_ not in self.orders_registry and symbol+side not in self.order_book:

			self.orders_registry.append(id_)

			side = ""
			if pos =="Long": side ="B"
			elif pos =="Short": side ="S"

			self.order_book[symbol+side] = id_
			self.orders_symbol[id_] = symbol
			#create the tkstring.

			self.id_lock[id_] = threading.Lock()

			self.flatten_lock[id_] = threading.Lock()

			self.used_stoporder[id_] = False

			self.order_tkstring[id_] = {}

			self.order_tkstring[id_]["algo_status"] = tk.StringVar()
			self.order_tkstring[id_]["algo_status"].set(status)

			self.order_tkstring[id_]["current_share"] = tk.StringVar()
			self.order_tkstring[id_]["current_share"].set("0/"+str(share))

			self.order_tkstring[id_]["realized"] = tk.StringVar()
			self.order_tkstring[id_]["realized"].set("0")

			self.order_tkstring[id_]["unrealized"] = tk.StringVar()
			self.order_tkstring[id_]["unrealized"].set("0")

			self.order_tkstring[id_]["unrealized_pshr"] = tk.StringVar()
			self.order_tkstring[id_]["unrealized_pshr"].set("0")

			self.order_tkstring[id_]["average_price"] = tk.StringVar()
			self.order_tkstring[id_]["average_price"].set("N/A")

			self.order_tkstring[id_]["risk_ratio"] = tk.StringVar()
			self.order_tkstring[id_]["risk_ratio"].set("0/"+str(risk))
			#Initilize the data values. 

			self.order_tkstring[id_]["auto_range"] = tk.BooleanVar(value=True)

			self.order_tkstring[id_]["auto_manage"] = tk.BooleanVar(value=True)

			self.break_at[id_] = order_price
			self.stoplevel[id_] = stoplevel

			self.order_tkstring[id_]["break_at"] = tk.DoubleVar()
			self.order_tkstring[id_]["break_at"].set(self.break_at[id_])

			self.order_tkstring[id_]["stoplevel"] = tk.DoubleVar()
			self.order_tkstring[id_]["stoplevel"].set(self.stoplevel[id_])


			self.order_tkstring[id_]["tgtpx1"] = tk.DoubleVar()
			self.order_tkstring[id_]["tgtpx2"] = tk.DoubleVar()
			self.order_tkstring[id_]["tgtpx3"] = tk.DoubleVar()

			self.realized[id_] = 0
			self.current_share[id_] = 0
			self.target_share[id_] = share
			self.unrealized[id_] = 0
			self.unrealized_pshr[id_] = 0
			self.average_price[id_] = 0
			self.est_risk[id_] =  risk
			
			self.position[id_] = pos
			self.holdings[id_] = []

			self.order_info[id_] = [order_type,pos,order_price,share,symbol]

			self.data_list[id_] = data_list
			#print(self.data_list[id_])
			#turns the order. 

			self.price_current_level[id_] = 1
			self.price_levels[id_] = {}
			self.update_target_price(id_)

			l = [(symbol,id_),\
			self.order_tkstring[id_]["algo_status"],\
			des,\
			self.order_tkstring[id_]["auto_range"],\
			self.order_tkstring[id_]["break_at"],
			self.order_tkstring[id_]["stoplevel"],\
			pos,\
			self.order_tkstring[id_]["risk_ratio"],\
			self.order_tkstring[id_]["average_price"],\
			self.order_tkstring[id_]["current_share"],\
			self.order_tkstring[id_]["auto_manage"],\
			self.order_tkstring[id_]["tgtpx1"],\
			self.order_tkstring[id_]["tgtpx2"],\
			self.order_tkstring[id_]["tgtpx3"],\
			self.order_tkstring[id_]["unrealized_pshr"],\
			self.order_tkstring[id_]["unrealized"],\
			self.order_tkstring[id_]["realized"]]


			if symbol not in self.symbols_orders:
				self.symbols_orders[symbol] = [id_]
			else:
				self.symbols_orders[symbol].append(id_)

			self.modify_algo_count(1)
			self.order_ui_creation(l)
			self.register(symbol)
		else:
			print("adding order failed")

	def order_ui_creation(self,info):

		#if they already exisit, just repace the old ones.
		i = info[0][0]
		id_ = info[0][1]
		status = info[1]
		l = self.label_count

		#self.tickers_labels[i]=[]
		self.tickers_tracers[i] = []
		self.order_tklabels[id_] = {}

		#add in tickers.
		#print("LENGTH",len(info))
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = self.tk_labels[j]

			if label_name == "symbol":
				self.order_tklabels[id_][label_name] =tk.Button(self.deployment_frame ,text=info[j][0],width=self.width[j],command = lambda s=id_: self.deploy_stop_order(id_))	
			elif label_name =="AR" or  label_name =="AM":
				self.order_tklabels[id_][label_name] =tk.Checkbutton(self.deployment_frame,variable=info[j])
			elif label_name =="algo_status":
				self.order_tklabels[id_][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command = lambda s=id_: self.cancel_deployed(id_))
			elif label_name == "break_at" or label_name == "stoplevel" or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.order_tklabels[id_][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j])	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.order_tklabels[id_][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					self.order_tklabels[id_][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

			try:
				self.label_default_configure(self.order_tklabels[id_][label_name])
			except:
				pass
			self.order_tklabels[id_][label_name].grid(row= l+2, column=j,padx=0)

			#else: #command = lambda s=symbol: self.delete_symbol_reg_list(s))

		j+=1
		flatten=tk.Button(self.deployment_frame ,text="flatten",width=self.width[j],command= lambda k=i:self.flatten_symbol(k,id_,status))
		self.label_default_configure(flatten)
		flatten.grid(row= l+2, column=j,padx=0)

		self.label_count +=1

		self.rebind(self.dev_canvas,self.deployment_frame)

	def lock_entrys(self,id_,lock_or_not):

		##Pending : Unlock.
		if lock_or_not: 
			state = "disabled"
		else: 
			state = "normal"
		##Deployed: Lock.

		self.order_tklabels[id_]["break_at"]["state"]=state
		self.order_tklabels[id_]["stoplevel"]["state"]=state
		# self.order_tklabels[id_]["pxtgt1"]["state"]=state
		# self.order_tklabels[id_]["pxtgt2"]["state"]=state
		# self.order_tklabels[id_]["pxtgt3"]["state"]=state

	def modify_algo_count(self,num):
		self.algo_count_number+=num
		self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))

	def check_running_order(self,symbol):

		if symbol in self.running_order:
			#ust be ""
			if self.running_order[symbol] =="":
				return False
			else:
				return True

		else:
			return False

	#return true if current order is running.
	def check_order_running(self,id_,symbol):

		if symbol in self.running_order:
			return self.running_order[symbol] ==id_
		else:
			return False

	def order_confirmation(self,d):
		id_ = d[1]
		print(id_,"confirmed and is a go")

		return True
		if id_ not in self.orders_registry:
			print("Cannot find order",id_)
		else:
			order = self.order_info[id_] 

			type_ = order[0]
			pos = order[1]
			order_price = order[2]
			share = order[3]
			symbol = order[4]


			self.holdings[id_] = []
			#initilize a trade on a symbol. 

			#check : if a position already on a symbol. cancle the previous order? 
			#has to be on the opposite side.
			#Not current order is running. 

			if not self.check_running_order(symbol):
				if self.order_tkstring[id_]["algo_status"].get()=="Pending":
					self.order_execution(id_,type_,symbol,share,pos,order_price)
			else:

				####check what is going on? #### THINK THINK THINK. 
				current_order = self.order_info[self.running_order[symbol]]
				pos_ = current_order[1]
				
				if pos_!= pos and self.order_tkstring[id_]["algo_status"].get()=="Pending":
					conflicting_order = threading.Thread(target=self.conflicting_order,args=(id_,type_,pos,order_price,share,symbol), daemon=True)
					conflicting_order.start()	
				else:
					print("Already containning one running order.")		
				#should be a thread.


	def order_execution(self,id_,type_,symbol,share,pos,order_price):

		self.running_order[symbol] = id_

		if type_ == "Market":

			if pos=="Long":
				buy_market_order(symbol,share)
				
				self.running_order[symbol] = id_
			elif pos =="Short":
				sell_market_order(symbol,share)

			self.order_tkstring[id_]["algo_status"].set("Running")

			self.order_tklabels[id_]["algo_status"]["background"] = "#97FEA8" #set the label to be, green.
				
		elif type_ =="Limit":
			if pos=="Long":
				buy_limit_order(symbol,order_price,share)
				
			elif pos =="Short":
				sell_market_order(symbol,order_price,share)

			self.order_tkstring[id_]["algo_status"].set("Placed")

			#self.order_tkstring[id_].set("Placed")

			self.order_tklabels[id_]["algo_status"]["background"] = "yellow" #set the label to be yellow


		#I should register the symbol the moment it comes in.
		self.register(symbol)

	def conflicting_order(self,id_,type_, pos,price,share,symbol):

		flatten_symbol(symbol)

		previous_order = self.running_order[symbol]

		while True:
			if self.current_share[previous_order]==0:
				break
			else:
				time.sleep(0.1)

		self.running_order[symbol] = id_

		if type_ == "Market":

			if pos=="Long":
				buy_market_order(symbol,share)
				
				self.running_order[symbol] = id_
			elif pos =="Short":
				sell_market_order(symbol,share)

			self.order_tkstring[id_]["algo_status"].set("Running")

			self.order_tklabels[id_]["algo_status"]["background"] = "#97FEA8" #set the label to be, green.
				
		elif type_ =="Limit":
			if pos=="Long":
				buy_limit_order(symbol,order_price,share)
				
			elif pos =="Short":
				sell_market_order(symbol,order_price,share)

			self.order_tkstring[id_]["algo_status"].set("Placed")

			#self.order_tkstring[id_].set("Placed")

			self.order_tklabels[id_]["algo_status"]["background"] = "yellow" #set the label to be yellow
		self.register(symbol)
			
	def order_pipe_listener(self):
		while True:
			d = self.order_pipe.recv()


			if d[0] =="status":
				try:
					self.ppro_status.set("Ppro : "+str(d[1]))

					if str(d[1])=="Connected":
						self.ppro_status_["background"] = "#97FEA8"
					else:
						self.ppro_status_["background"] = "red"
				except Exception as e:
					print(e)

			if d[0] =="msg":
				print(d[1])

			if d[0] =="order confirm":
				#get symbol,price, shares.
				# maybe filled. maybe partial filled.
				self.ppro_order_confirmation(d[1])

			if d[0] =="order update":

				#update the quote, unrealized. 
				self.ppro_order_update(d[1])

			if d[0] =="order rejected":

				self.ppro_order_rejection(d[1])

			if d[0] =="new stoporder":

				#print("stop order received:",d[1])
				self.ppro_append_new_stoporder(d[1])
			
	#when there is a change of quantity of an order. 

	def ppro_order_confirmation(self,data):

		symbol = data["symbol"]
		price = data["price"]
		shares = data["shares"]
		side = data["side"]
		code = symbol+side

		print(symbol,price,shares,side)

		#check if this activates an hidden order.
		#######filter out irrelavant orders.


		#breaks when handling an already finished order.
		check_order_book = True


		if symbol in self.running_order:
			if self.running_order[symbol]!="":
				print(self.running_order[symbol],"order update")
				self.order_process(symbol,price,shares,side)
				check_order_book = False

		if check_order_book:
			if code in self.order_book:
				id_=self.order_book[code]
				status = self.order_tkstring[id_]["algo_status"].get()

				if status=="Deployed" or status=="Deploying":
					act = threading.Thread(target=self.order_activation,args=(id_,symbol,price,shares,side), daemon=True)
					act.start()
			else:
				print("irrelavant orders from:",symbol)



		# if symbol in self.running_order or code in self.order_book: 
		# 	#establish id for the ones not seet up.
		# 	if symbol not in self.running_order:  #i dont understand this part anymore.
		# 		init = True
		# 	else:
		# 		if self.running_order[symbol] =="":
		# 			init = True

		# 	id_=self.order_book[code]
		# 	status = self.order_tkstring[id_]["algo_status"].get()

			# if init:   #send a chekcing procedure. check if the stoporder is done. 
			# 	if status=="Deployed" or status=="Deploying":
			# 		act = threading.Thread(target=self.order_activation,args=(id_,symbol,price,shares,side), daemon=True)
			# 		act.start()
					# id_ = self.order_book[code]
					# self.running_order[symbol] = id_
					# self.order_tkstring[id_]["algo_status"].set("Running")
					# self.order_tklabels[id_]["algo_status"]["background"] = "#97FEA8" #set the label to be, green.	
		# 	else:
		# 		self.order_process(symbol,price,shares,side)


	def order_process(self,symbol,price,shares,side):
		id_ = self.running_order[symbol]
		#it's an order already got flattened...? fk. then id_ is nothing.

		if id_ != "":
			current = self.current_share[id_]
			print("order",symbol,"side:",side,"shares",shares,"price",price)


			if (self.position[id_]=="Long" and side =="B") or (self.position[id_]=="Short" and (side =="S" or side=="T")):
				self.ppro_order_loadup(id_,symbol,price,current,shares,side)

			else:
				self.ppro_order_loadoff(id_,symbol,price,current,shares,side)

			#print(self.holdings[id_])
			self.update_display(id_)
		else:
			print("Unidentified orders:","symbol",symbol,"side:",side,"shares",shares,"price",price)

		#this should be a thread. 

	def order_activation(self,id_,symbol,price,shares,side):

		#wait until deployed.

		#HOLD THE ID lock. 
		with self.id_lock[id_]: #lock
			#print(shares,"start")
			while self.order_tkstring[id_]["algo_status"].get()=="Deploying":
				time.sleep(0.5)

			if self.order_tkstring[id_]["algo_status"].get()=="Running":
				self.order_process(symbol,price,shares,side)

			else:
				stop_id = self.id_to_stoporder[id_]
				status = get_stoporder_status(stop_id)

				if status =="Done":
					print(id_,"activated and is a go.")
					id_ = self.order_book[symbol+side]
					self.running_order[symbol] = id_
					self.order_tkstring[id_]["algo_status"].set("Running")
					self.order_tklabels[id_]["algo_status"]["background"] = "#97FEA8" #set the label to be, green.

					self.update_target_price(id_,price)
					self.order_process(symbol,price,shares,side)
		#print(shares,"done")

	def ppro_order_loadup(self,id_,symbol,price,current,shares,side):

		self.current_share[id_] = current+shares

		if current ==0:
			self.average_price[id_] = round(price,3)
		else:
			self.average_price[id_] = round(((self.average_price[id_]*current)+(price*shares))/self.current_share[id_],3)

		for i in range(shares):
			self.holdings[id_].append(price)

		self.adjusting_risk(id_)

	def ppro_order_loadoff(self,id_,symbol,price,current,shares,side):

		self.current_share[id_] = current-shares	
		
		gain = 0
		if self.position[id_]=="Long":
			for i in range(shares):
				try:
					gain += price-self.holdings[id_].pop()
				except:
					print("Holding calculation error,holdings are empty.")
		elif self.position[id_]=="Short":
			for i in range(shares):
				try:
					gain += self.holdings[id_].pop() - price	
				except:
					print("Holding calculation error,holdings are empty.")	

		self.realized[id_]+=gain
		self.realized[id_]= round(self.realized[id_],2)

		self.adjusting_risk(id_)

		print(symbol," sold:",shares," current shares:",self.current_share[id_],"realized:",self.realized[id_])

		#finish a trade if current share is 0.

		if self.current_share[id_] <= 0:
			self.unrealized[id_] = 0
			self.unrealized_pshr[id_] = 0

			#mark it done.
			self.mark_off_algo(id_,self.status["Done"])

			# current_status = self.order_tkstring[id_]["algo_status"].get()
			# if current_status=="Running":
			# 	self.order_tkstring[id_]["algo_status"].set("Done")
			# 	self.modify_algo_count(-1)

			# #dont support multiple symbol on the same trade yet.
			# # dereg = threading.Thread(target=self.deregister,args=(symbol,), daemon=True)
			# # dereg.start()

			# #deactive the order.
			# self.running_order[symbol]= ""

	def ppro_append_new_stoporder(self,pkg):

		stopid,symbol,side = pkg[0],pkg[1],pkg[2]

		
		if symbol+side in self.order_book:
			id_=self.order_book[symbol+side]

			with self.stoporder_book_lock:
				self.stoporder_book.append(stopid)

			self.stoporder_to_id[stopid] = id_
			self.id_to_stoporder[id_] = stopid

			print(symbol,stopid)
			if self.order_tkstring[id_]["algo_status"].get()==self.status["Deploying"]:
				self.order_tkstring[id_]["algo_status"].set(self.status["Deployed"])
				self.order_tklabels[id_]["algo_status"]["background"] = YELLOW
			else:
				print(symbol,"WHY NOT????", id_,self.order_tkstring[id_]["algo_status"].get())
			self.stoporder[id_] = stopid

			#change label into placed.
		else:
			print("Cannot find new order,",symbol+side)



		#assign this id to symbol+side? How can i trace the status of this stoporder???  

	def deploy_stop_order(self,id_):

		#can only deploy if the status is pending.

		current_status= self.order_tkstring[id_]["algo_status"].get()
		if current_status == self.status["Pending"]:

			#refresh the datas.
			self.update_target_entry(id_)
			self.lock_entrys(id_,True)

			self.break_at[id_] = self.order_tkstring[id_]["break_at"].get()
			self.stoplevel[id_] = self.order_tkstring[id_]["stoplevel"].get()
			self.price_levels[id_][1] = self.order_tkstring[id_]["tgtpx1"].get()
			self.price_levels[id_][2] = self.order_tkstring[id_]["tgtpx2"].get()
			self.price_levels[id_][3] = self.order_tkstring[id_]["tgtpx3"].get()

			self.order_tkstring[id_]["algo_status"].set(self.status["Deploying"])
			self.order_tklabels[id_]["algo_status"]["background"] = LIGHTYELLOW

			break_price = self.break_at[id_]
			share = self.target_share[id_]
			pos = self.position[id_]
			symbol = self.orders_symbol[id_]

			if pos=="Long":
				stoporder_to_market_buy(symbol,break_price,share,self.order_send_pipe)  #send back id via pipe.
				
				# self.running_order[symbol] = id_
			elif pos =="Short":
				stoporder_to_market_sell(symbol,break_price,share,self.order_send_pipe)
		else:
			print("Cannot deploy ",id_," Current status:",current_status)


	def deploy_all_stoporders(self):

		print("Deploying all algos:",len(self.orders_registry))
		for i in self.orders_registry:
			self.deploy_stop_order(i)

	def cancel_deployed(self,id_):
		#if there is an order deployed. 

		if id_ in self.id_to_stoporder:
			self.cancel_stoporder(self.id_to_stoporder[id_])

	def cancel_stoporder(self,stopid):
		# id_ -> stopid. .  
		id_ = self.stoporder_to_id[stopid]
		if self.order_tkstring[id_]["algo_status"].get()==self.status["Deployed"]:
			cancel_stoporder(stopid)
			self.order_tkstring[id_]["algo_status"].set(self.status["Pending"])
			self.order_tklabels[id_]["algo_status"]["background"] = DEFAULT
			self.lock_entrys(id_,False)
			with self.stoporder_book_lock:
				self.stoporder_book.remove(stopid)

	def cancel_all_stoporders(self):
		###just look through all placed orders

		print("Cancel:",len(self.stoporder_book))
		cur = self.stoporder_book[:]
		for i in cur:
			self.cancel_stoporder(i)

	#RISK, Size. 
	def adjusting_risk(self,id_):
		#calculate the actual risk.

		if self.position[id_] =="Long":
			self.act_risk[id_] = round(((self.average_price[id_]-self.stoplevel[id_])*self.current_share[id_]),2)
		else:
			self.act_risk[id_] = round((( self.stoplevel[id_]-self.average_price[id_])*self.current_share[id_]),2)

		diff = self.act_risk[id_]-self.est_risk[id_]
		ratio = diff/self.est_risk[id_]

		self.order_tklabels[id_]["act_r/est_r"]["background"] = hexcolor_green_to_red(ratio)
		self.order_tkstring[id_]["risk_ratio"].set(str(self.act_risk[id_])+"/"+str(self.est_risk[id_]))

		if self.current_share[id_] == 0:
			self.order_tklabels[id_]["act_r/est_r"]["background"] = DEFAULT

	#update the current status of a current order. 
	def ppro_order_update(self,data):

		symbol = data["symbol"]
		bid = data["bid"]
		ask = data["ask"]

		
		#print(data)
		####update the support and resistence here....

		#iterate through all the orders attached to this symbol
		# find the ones that are pending. 
		# update necessary support and resistence levels. 

		self.refresh_support_resistence(symbol,ask,bid)

		if symbol in self.running_order:

			if self.running_order[symbol]!= "":

				id_ = self.running_order[symbol]
				self.refresh_target_price_on_input(id_)
				flatten = False

				if self.position[id_]=="Long":
					price = bid
					gain = round((price-self.average_price[id_]),4)

					if price <= self.stoplevel[id_]:
						flatten=True


					current_level = self.price_current_level[id_]

					if self.order_tkstring[id_]["auto_manage"].get()==True  and current_level<4:
						
						

						if price >= self.price_levels[id_][current_level]:

							
							#shake of 1/3 
							share = min(int(int(self.target_share[id_])//4),self.current_share[id_])

							if current_level==3: share=int(self.current_share[id_])
							#if share==0: share = self.current_share[id_]  #if 0. get rid of everything.

							sell_market_order(symbol,share)

							self.stoplevel[id_] = self.price_levels[id_][current_level-1]
							self.adjusting_risk(id_)

							#move up one level if below 3

							self.price_current_level[id_]+=1 

							print(symbol,": target reached,level:",current_level,"New stoploss:",self.price_levels[id_][current_level-1])

				elif self.position[id_]=="Short":
					price = ask
					gain = round(self.average_price[id_]-price,4)
					if price >= self.stoplevel[id_]:
						flatten=True

					current_level = self.price_current_level[id_]
					if self.order_tkstring[id_]["auto_manage"].get()==True and current_level<4:

						
						if price <= self.price_levels[id_][current_level]:

							
							#shake of 1/3 
							share = min(int(int(self.target_share[id_])//4),self.current_share[id_])
							if current_level==3: share=int(self.current_share[id_])

							buy_market_order(symbol,share)

							self.stoplevel[id_] = self.price_levels[id_][current_level-1]
							self.adjusting_risk(id_)

							#move up one level if below 3

							self.price_current_level[id_]+=1 


							print(symbol,": target reached,level:",current_level,"New stoploss:",self.price_levels[id_][current_level-1])


				if self.current_share[id_] >0:
					self.unrealized_pshr[id_] = gain
					self.unrealized[id_] = round(gain*self.current_share[id_],4)

				#if ...loss is enough. flatten.
				#print(gain,self.unrealized[id_])

				if flatten and self.current_share[id_]>0:
					self.flatten_symbol(symbol,id_,self.order_tkstring[id_]["algo_status"])
				
				self.update_display(id_)


	def ppro_order_rejection(self,data):

		symbol=data["symbol"] 
		side=data["side"] 
		info=data["info"]

		
		#get the order id. 

		if symbol+side in self.order_book:
			id_ = self.order_book[symbol+side]
			self.mark_off_algo(id_,self.status["Rejected"])
			print(symbol,"rejected:",info)

		else:
			print("cannot find id for",symbol+side)

	#Utilities. 
	def refresh_support_resistence(self,symbol,ask,bid):

		try:
			if symbol in self.symbols_orders:

				self.current_ask[symbol] = ask
				self.current_bid[symbol] = bid
				for id_ in self.symbols_orders[symbol]:
					change = False
					if self.order_tkstring[id_]["algo_status"].get() == "Pending" and self.order_tkstring[id_]["auto_range"].get()==True:

						#update the levels. low become
						if self.position[id_] == "Long":
							if ask>self.order_tkstring[id_]["break_at"].get():
								self.order_tkstring[id_]["break_at"].set(ask)
								self.break_at[id_]=ask
								change = True
							if bid<self.order_tkstring[id_]["stoplevel"].get():
								self.order_tkstring[id_]["stoplevel"].set(bid)
								self.stoplevel[id_]=ask
								change = True
						else:  #short
							if bid<self.order_tkstring[id_]["break_at"].get():
								self.order_tkstring[id_]["break_at"].set(bid)
								self.break_at[id_]=bid
								change = True
							if ask>self.order_tkstring[id_]["stoplevel"].get():
								self.order_tkstring[id_]["stoplevel"].set(ask)
								self.stoplevel[id_]=ask
								change = True
						if change:
							self.update_target_price(id_)
							self.update_target_entry(id_)
							#here I need to recaculate the estimate risk.
							#self.adjusting_risk(id_)
		except Exception as e:
			print("updating levels errors on",symbol,e)

	#whether it is done, rejected, or cancled. should go here

	def refresh_target_price_on_input(self,id_):
		try:
			self.price_levels[id_][1]=float(self.order_tkstring[id_]["tgtpx1"].get())
			self.price_levels[id_][2]=float(self.order_tkstring[id_]["tgtpx2"].get())
			self.price_levels[id_][3]=float(self.order_tkstring[id_]["tgtpx3"].get())

		except:
			print("invalid price targets set for ",id_)

	def update_target_price(self,id_,price=None): #call this whenever the break at price changes. 

		if price==None:
			price = self.break_at[id_]

		global coecoefficient

		good = False
		if self.position[id_]=="Long":

			ohv = self.data_list[id_]["OHavg"]
			ohs = self.data_list[id_]["OHstd"]
			#print(self.data_list[id_],type(ohv),ohs,type(price))

			if ohv!=0:
				self.price_levels[id_][0] = price
				self.price_levels[id_][1] = round(price+ohv*0.2*coefficient,2)
				self.price_levels[id_][2] = round(price+ohv*0.5*coefficient,2)
				self.price_levels[id_][3] =	round(price+ohv*0.8*coefficient,2)
				good = True
			else:

				self.order_tkstring[id_]["auto_manage"].set(False)
		else:
			olv = self.data_list[id_]["OLavg"]
			ols = self.data_list[id_]["OLstd"]

			if olv!=0:
				self.price_levels[id_][0] = price
				self.price_levels[id_][1] = round(price-olv*0.2*coefficient,2)
				self.price_levels[id_][2] = round(price-olv*0.5*coefficient,2)
				self.price_levels[id_][3] =	round(price-olv*0.8*coefficient,2)
				good = True
			else:
				self.order_tkstring[id_]["auto_manage"].set(False)

		#set the price levels. 
		#print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])
		if good:
			self.order_tkstring[id_]["tgtpx1"].set(self.price_levels[id_][1])
			self.order_tkstring[id_]["tgtpx2"].set(self.price_levels[id_][2])
			self.order_tkstring[id_]["tgtpx3"].set(self.price_levels[id_][3])

		try:
			print("update: cur:",id_,price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])
		except Exception as e:
			print(e)

	def update_target_entry(self,id_):

		cur_risk = round(abs(self.stoplevel[id_] - self.break_at[id_]),3)
		shares = int(self.est_risk[id_]//cur_risk)

		print(id_," updating shares: new risk per share: ",cur_risk," shares from",self.target_share[id_]," to",shares)

		self.target_share[id_] = shares

		self.order_tkstring[id_]["current_share"].set(str(self.current_share[id_])+"/"+str(self.target_share[id_]))

		

	def mark_off_algo(self,id_,status):

		print(status)
		if status == "Rejected":
			self.order_tkstring[id_]["algo_status"].set(status)
			self.order_tklabels[id_]["algo_status"]["background"] = "red"
			self.running_order[self.orders_symbol[id_]] = ""
		elif status =="Done":
			self.order_tkstring[id_]["algo_status"].set(status)
			self.order_tklabels[id_]["algo_status"]["background"] = "#97FEA8"
			self.running_order[self.orders_symbol[id_]] = ""
		elif status =="Canceled":#canceled 

			if self.order_tkstring[id_]["algo_status"].get() == "Pending":
				self.order_tkstring[id_]["algo_status"].set(status)

		
		self.modify_algo_count(-1)

	def recreate_labels(self):

		l = list(self.labels.keys())
		w = list(self.labels.values())

		for i in range(len(l)): #Rows
			self.b = tk.Button(self.deployment_frame, text=l[i],width=w[i],height=2)#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)

	def update_display(self,id_):

		#need to update, current_share, realized,unrealized,unlreaized per, and avg price. 
		#
		#"algo_status","realized","shares","unrealized","unrealized_pshr","average_price"
		#print()

		#print(self.average_price[id_],self.unrealized[id_].get(),self.unrealized_pshr[id_].get())
		#print(id_,self.current_share[id_],self.average_price[id_],self.unrealized_pshr[id_],self.unrealized[id_])

		self.order_tkstring[id_]["current_share"].set(str(self.current_share[id_])+"/"+str(self.target_share[id_]))
		self.order_tkstring[id_]["realized"].set(str(self.realized[id_]))
		self.order_tkstring[id_]["unrealized"].set(str(self.unrealized[id_]))
		self.order_tkstring[id_]["unrealized_pshr"].set(str(self.unrealized_pshr[id_]))
		self.order_tkstring[id_]["average_price"].set(self.average_price[id_])

		#check color.f9f9f9

		if self.unrealized_pshr[id_]>0:
			self.order_tklabels[id_]["unrealized_pshr"]["background"] = STRONGGREEN
			self.order_tklabels[id_]["unrealized"]["background"] = STRONGGREEN
		elif self.unrealized_pshr[id_]<0:
			self.order_tklabels[id_]["unrealized_pshr"]["background"] = STRONGRED
			self.order_tklabels[id_]["unrealized"]["background"] = STRONGRED
		else:
			self.order_tklabels[id_]["unrealized_pshr"]["background"] = DEFAULT
			self.order_tklabels[id_]["unrealized"]["background"] =DEFAULT

		if self.realized[id_]==0:
			self.order_tklabels[id_]["realized"]["background"] = DEFAULT
		elif self.realized[id_]>0:
			self.order_tklabels[id_]["realized"]["background"] = STRONGGREEN
		elif self.realized[id_]<0:
			self.order_tklabels[id_]["realized"]["background"] = STRONGRED

		current_level = self.price_current_level[id_]
		if  current_level==1:
			self.order_tklabels[id_]["pxtgt1"]["background"] = LIGHTYELLOW
			self.order_tklabels[id_]["pxtgt2"]["background"] = DEFAULT
			self.order_tklabels[id_]["pxtgt3"]["background"] = DEFAULT
		elif  current_level==2:
			self.order_tklabels[id_]["pxtgt1"]["background"] = DEFAULT
			self.order_tklabels[id_]["pxtgt2"]["background"] = LIGHTYELLOW
			self.order_tklabels[id_]["pxtgt3"]["background"] = DEFAULT
		elif  current_level==3:
			self.order_tklabels[id_]["pxtgt1"]["background"] = DEFAULT
			self.order_tklabels[id_]["pxtgt2"]["background"] = DEFAULT
			self.order_tklabels[id_]["pxtgt3"]["background"] = LIGHTYELLOW

		elif current_level ==4:
			self.order_tklabels[id_]["pxtgt1"]["background"] = DEFAULT
			self.order_tklabels[id_]["pxtgt2"]["background"] = DEFAULT
			self.order_tklabels[id_]["pxtgt3"]["background"] = DEFAULT	

	def rebind(self,canvas,frame):
		canvas.update_idletasks()
		canvas.config(scrollregion=frame.bbox()) 

	def receive(self):
		time.sleep(3)
		count = 0
		while True:
			d = self.pipe.recv()

			if d[0] =="msg":
				print(d[1])
				try:
					self.main_app_status.set("Main: "+str(d[1]))
					if str(d[1])=="Connected":
						self.main_status["background"] = "#97FEA8"
					else:
						self.main_status["background"] = "red"
				except Exception as e:
					print(e)
			if d[0] =="pkg":
				print("new package arrived",d)
				self.goodtrade_listener(d[1])

	# def threads_manager(self):
	# 	time.sleep(3)

	# 	while True:
	# 		update = self.internal_communication.get()

	def goodtrade_listener(self,d):

		#['id', 'QQQ.NQ', 'Breakout on Support on 0.0 for 0 sec', 'Short', 20, 20.0]
		#handle database. and add labels. 
		#id, symbol, type, status, description, position, shares, risk$

		if d!=None:

			message_type = d[0]

			if message_type =="New order": 

				self.order_creation(d)

			elif message_type =="Confirmed":

				self.order_confirmation(d)

		else:
			print("Missing package.")

	def delete(self):
		for i in self.tabs:
			for widget in i.winfo_children():
				widget.destroy()

	def register(self,symbol):
		if symbol not in self.symbols:
			self.symbols.append(symbol)
			req = threading.Thread(target=self.register_to_ppro, args=(symbol, True,),daemon=True)
			req.start()
			
	def deregister(self,symbol):

		if symbol in self.symbols:
			self.symbols.remove(symbol)
			self.register_to_ppro(symbol, False)

	def register_to_ppro(self,symbol,status):

		print("Registering",symbol,status)
		if status == True:
			postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=on"
		else:
			postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=off"

		try:
			r= requests.get(postbody)
			if r.status_code==200:
				return True
			else:
				return False
		except:
			print("register failed")
			return False

		#Invalid Request		


if __name__ == '__main__':



	multiprocessing.freeze_support()

	port =4609

	goodtrade_pipe, receive_pipe = multiprocessing.Pipe()


	algo_voxcom = multiprocessing.Process(target=algo_manager_voxcom, args=(receive_pipe,),daemon=True)
	algo_voxcom.daemon=True
	algo_voxcom.start()


	ppro_pipe, ppro_pipe_end = multiprocessing.Pipe()

	algo_ppro_manager = multiprocessing.Process(target=algo_ppro_manager, args=(port,ppro_pipe_end,),daemon=True)
	algo_ppro_manager.daemon=True
	algo_ppro_manager.start()

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager v1b") 
	root.geometry("1600x1000")
	root.minsize(1600, 1000)
	root.maxsize(1800, 1200)

	view = algo_manager(root,port,goodtrade_pipe,ppro_pipe,ppro_pipe_end)

	#receive_pipe.send(['New order', 'Break up2268503', 'Break up', 'QQQ.NQ', 'Pending', 'Breakout on Resistance on 338.85 for 0 sec', 'Long', 'Market', '338.85', '2104', 5050.0])

	root.mainloop()

	algo_voxcom.terminate()
	algo_voxcom.join()

	algo_ppro_manager.terminate()
	algo_ppro_manager.join()

	os._exit(1) 
