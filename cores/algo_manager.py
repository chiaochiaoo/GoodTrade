import tkinter as tk
from tkinter import ttk

import socket
import pickle
import pandas as pd
import time
import multiprocessing
import threading
from pannel import *
import datetime
import time

import requests

import os

from algo_ppro_manager import *


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
					pipe.send(["msg","Cannot connected. Try again in 2 seconds."])
					print("Cannot connected. Try again in 2 seconds.")
					time.sleep(2)

			connection = True
			pipe.send(["msg","Connection Successful"])
			print("Connection Successful")

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
			print("Server disconnected")
			pipe.send(["msg","Server disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			print(e)
		#restarted the whole thing 

class algo_manager(pannel):



	def __init__(self,root,port,gt_pipe,order_pipe):


		self.port = port
		self.symbols = []
		self.orders_registry = []


		# SYMBOL ATTRIBUTE. Getting symbol -> ID 

		self.active_order = {}

		# ORDER ATTRIBUTE. Init upon receiving. 

		
		# Tk Strings. 

		# Actual data. 

		#		l = [(symbol,id_),self.algo_status[id_],des,risk,pos,self.current_share[id_],self.average_price[id_],self.unrealized[id_],self.unrealized_pshr[id_],self.realized[id_]]
		

		#self.algo_status = {} #Pending, Running,Cancled,Complete.
		#self.order_status = {}

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=["symbol","algo_status","description","risk","position","shares","average_price","unrealized_pshr","unrealized","realized"]

		self.order_tkstring = {}
		self.order_tklabels = {}


		self.realized = {}
		self.current_share = {}
		self.target_share = {}
		self.unrealized = {}
		self.unrealized_pshr ={}
		self.average_price = {}
		self.risk = {}
		self.position = {}

		self.holdings= {}

		self.order_info = {}


		# self.current_share_data = {}
		# self.target_share_data = {}
		# self.realized_data ={}
		# self.unrealized_data = {}
		# self.unrealized_pshr_data={}
		# self.average_price_data = {}
		# self.risk_data = {}

		

		#input symbol, get id (active.)


		###if a symbol is running, or already flattened.
		

		super().__init__(root)

		self.width = [10,10,30,8,8,8,8,8,8,8,6]
		self.labels = ["Symbol","Algo status","description","Risk","Position","SzIn","AvgPx","UPshr","U","R","flatten"]

		self.pipe = gt_pipe

		self.order_pipe = order_pipe

		self.setting = ttk.LabelFrame(root,text="Algo Manager") 
		self.setting.place(x=10,y=10,height=80,relwidth=0.95)

		self.status = tk.StringVar()
		self.status.set("Status:")
		self.ppro_status = ttk.Label(self.setting, textvariable=self.status)
		self.ppro_status.place(x = 20, y =12)

		self.deployment_frame = ttk.LabelFrame(root,text="Algos deployment") 
		self.deployment_frame.place(x=10,y=85,relheight=1,relwidth=0.95)

		self.in_progress = False

		self.recreate_labels()

		#self.add_order(['id', 'QQQ.NQ', 'Breakout on Support on 0.0 for 0 sec', 'Short', 20, 20.0])


		receiver = threading.Thread(target=self.receive, daemon=True)
		receiver.start()

		receiver2 = threading.Thread(target=self.order_pipe_listener, daemon=True)
		receiver2.start()

		self.register_order_listener()


	#this pipe tracks the current price, P/L. order status.

	def flatten_symbol(self,symbol,id_=None,status_text=None):

		#check if this order is running.
		running = self.check_order_running(id_,symbol)
		if running:
			flatten = threading.Thread(target=flatten_symbol,args=(symbol,), daemon=True)
			flatten.start()
			#self.current_share_data[id_]=0

		if id_!= None and status_text!= None:
			if id_ in self.orders_registry:
				self.orders_registry.remove(id_)
				current_status = status_text.get()
				if current_status=="Pending":
					status_text.set("Canceled")
				# else:
				# 	status_text.set("Done.")

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

	def order_creation(self,d):

		#['New order', 'Break up2268503', 'Break up', 'QQQ.NQ', 'Pending', 'Breakout on Resistance on 338.85 for 0 sec', 'Long', 'Market', '338.85', '2104', 5050.0]
		id_,symbol,type_,status,des,pos,order_type,order_price,share,risk = d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10]

		print(id_,"added to new order")

		if id_ not in self.orders_registry:

			self.orders_registry.append(id_)

			#create the tkstring.

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

			#Initilize the data values. 

			self.realized[id_] = 0
			self.current_share[id_] = 0
			self.target_share[id_] = share
			self.unrealized[id_] = 0
			self.unrealized_pshr[id_] = 0
			self.average_price[id_] = 0
			self.risk[id_] = -risk
			self.position[id_] = pos

			self.order_info[id_] = [order_type,pos,order_price,share,symbol]

			#turns the order. 

			l = [(symbol,id_),\
			self.order_tkstring[id_]["algo_status"],\
			des,\
			risk,\
			pos,\
			self.order_tkstring[id_]["current_share"],\
			self.order_tkstring[id_]["average_price"],\
			self.order_tkstring[id_]["unrealized_pshr"],\
			self.order_tkstring[id_]["unrealized"],\
			self.order_tkstring[id_]["realized"]]


			self.order_ui_creation(l)
		else:
			print("adding order failed")

	def order_ui_creation(self,info):
		i = info[0][0]
		id_ = info[0][1]
		status = info[1]
		l = self.label_count

		#self.tickers_labels[i]=[]
		self.tickers_tracers[i] = []
		self.order_tklabels[id_] = {}

		#add in tickers.
		print("LENGTH",len(info))
		for j in range(len(info)):
			#if j == 1 or j ==5 or j ==6 or j==7  or j==8 or j==9:
			label_name = self.tk_labels[j]

			if j == 0:
				self.order_tklabels[id_][label_name] =tk.Label(self.deployment_frame ,text=info[j][0],width=self.width[j])		
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.order_tklabels[id_][label_name]=tk.Label(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					self.order_tklabels[id_][label_name]=tk.Label(self.deployment_frame ,text=info[j],width=self.width[j])

			self.label_default_configure(self.order_tklabels[id_][label_name])
			self.order_tklabels[id_][label_name].grid(row= l+2, column=j,padx=0)

			#else: #command = lambda s=symbol: self.delete_symbol_reg_list(s))

		j+=1
		flatten=tk.Button(self.deployment_frame ,text="flatten",width=self.width[j],command= lambda k=i:self.flatten_symbol(k,id_,status))
		self.label_default_configure(flatten)
		flatten.grid(row= l+2, column=j,padx=0)

		self.label_count +=1

	def check_running_order(self,symbol):

		if symbol in self.active_order:

			#ust be ""
			if self.active_order[symbol] =="":
				return False
			else:
				return True

		else:
			return False

	#return true if current order is running.
	def check_order_running(self,id_,symbol):

		if symbol in self.active_order:
			return self.active_order[symbol] ==id_
		else:
			return False


	def order_confirmation(self,d):
		id_ = d[1]
		print(id_,"confirmed and is a go")

		#wrong place to look at.
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
				self.order_execution(id_,type_,symbol,share,pos,order_price)
			else:

				####check what is going on? #### THINK THINK THINK. 

				current_order = self.order_info[self.active_order[symbol]]
				pos_ = order[1]
				
				if pos_!= pos:	
					conflicting_order = threading.Thread(target=self.conflicting_order,args=(id_,type_,pos,order_price,share,symbol), daemon=True)
					conflicting_order.start()	
				else:
					print("Already containning one running order.")		
				#should be a thread.

	def order_execution(self,id_,type_,symbol,share,pos,order_price):

		self.active_order[symbol] = id_

		if type_ == "Market":

			if pos=="Long":
				buy_market_order(symbol,share)
				
				self.active_order[symbol] = id_
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


	def conflicting_order(self,id_,type_, pos,price,share,symbol):

		flatten_symbol(symbol)

		previous_order = self.active_order[symbol]

		while True:
			if self.current_share[previous_order]==0:
				break
			else:
				time.sleep(0.1)

		self.active_order[symbol] = id_

		if type_ == "Market":

			if pos=="Long":
				buy_market_order(symbol,share)
				
				self.active_order[symbol] = id_
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


			if d[0] =="msg":
				print(d[1])

			if d[0] =="order confirm":
				#get symbol,price, shares.
				# maybe filled. maybe partial filled.
				self.ppro_order_confirmation(d[1])

			if d[0] =="order update":

				#update the quote, unrealized. 
				self.ppro_order_update(d[1])
			

	#when there is a change of quantity of an order. 
	def ppro_order_confirmation(self,data):

		symbol = data["symbol"]
		price = data["price"]
		shares = data["shares"]
		side = data["side"]

		if symbol in self.active_order:

			if self.active_order[symbol]!= "":

				id_ = self.active_order[symbol]

				#if same side, add. if wrong side.take off.
				#same side.

				current = self.current_share[id_]

				print("symbol",symbol,"side:",side,"shares",shares,"price",price)
				if (self.position[id_]=="Long" and side =="B") or (self.position[id_]=="Short" and (side =="S" or side=="T")):

					self.current_share[id_] = current+shares

					if current ==0:
						self.average_price[id_] = round(price,3)
					else:
						self.average_price[id_] = round(((self.average_price[id_]*current)+(price*shares))/self.current_share[id_],3)

					for i in range(shares):
						self.holdings[id_].append(price)

				#Taking shares off. assume it's all gone. -- NO. NO
				else:
					self.current_share[id_] = current-shares	

					print("curren shares:",self.current_share[id_] )			
					gain = 0
					if self.position[id_]=="Long":
						#self.realized[id_] += (price-self.average_price[id_])*shares
						

						for i in range(shares):
							try:
								gain += price-self.holdings[id_].pop()
							except:
								print("Holding calculation error")
					elif self.position[id_]=="Short":
						for i in range(shares):
							#try:
							gain += self.holdings[id_].pop() - price	
							#except:
							#	print("Holding calculation error")			
						#self.realized[id_] += (self.average_price[id_]-price)*shares
					self.realized[id_]+=gain
					self.realized[id_]= round(self.realized[id_],4)

					print("realized:",self.realized[id_])

					#finish a trade if current share is 0.

					if self.current_share[id_] == 0:
						self.unrealized[id_] = 0
						self.unrealized_pshr[id_] = 0

						#mark it done.
						current_status = self.order_tkstring[id_]["algo_status"].get()
						if current_status=="Running":
							self.order_tkstring[id_]["algo_status"].set("Done")

						#dont support multiple symbol on the same trade yet.
						# dereg = threading.Thread(target=self.deregister,args=(symbol,), daemon=True)
						# dereg.start()

						#deactive the order.
						self.active_order[symbol]= ""

				#print(self.holdings[id_])
				self.update_display(id_)

	#update the current status of a current order. 
	def ppro_order_update(self,data):

		symbol = data["symbol"]
		bid = data["bid"]
		ask = data["ask"]

		#get position

		if symbol in self.active_order:

			if self.active_order[symbol]!= "":
				id_ = self.active_order[symbol]

				if self.position[id_]=="Long":
					price = bid
					gain = round((price-self.average_price[id_]),4)

				elif self.position[id_]=="Short":
					price = ask
					gain = round(self.average_price[id_]-price,4)

				#loss:
				#print(gain)
				self.unrealized_pshr[id_] = gain
				self.unrealized[id_] = round(gain*self.current_share[id_],4)

				#if ...loss is enough. flatten.
				#print(gain,self.unrealized[id_])

				if self.unrealized[id_] <= self.risk[id_]:
					self.flatten_symbol(symbol,id_,self.order_tkstring[id_]["algo_status"])
				
				self.update_display(id_)


						
	#info= 
	#symbol,status,type,position,curretn,shares,risk,p/l


	#Utilities. 


	def recreate_labels(self):

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.deployment_frame, text=self.labels[i],width=self.width[i])#,command=self.rank
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

		self.order_tkstring[id_]["current_share"].set(str(self.current_share[id_])+"/"+str(self.target_share[id_]))
		self.order_tkstring[id_]["realized"].set(str(self.realized[id_]))
		self.order_tkstring[id_]["unrealized"].set(str(self.unrealized[id_]))
		self.order_tkstring[id_]["unrealized_pshr"].set(str(self.unrealized_pshr[id_]))
		self.order_tkstring[id_]["average_price"].set(self.average_price[id_])

		#check color.f9f9f9
		if self.unrealized_pshr[id_]>0:
			self.order_tklabels[id_]["unrealized_pshr"]["background"] = "#3DFC68"
			self.order_tklabels[id_]["unrealized"]["background"] = "#3DFC68"
		elif self.unrealized_pshr[id_]<0:
			self.order_tklabels[id_]["unrealized_pshr"]["background"] = "#FC433D"
			self.order_tklabels[id_]["unrealized"]["background"] = "#FC433D"
		else:
			self.order_tklabels[id_]["unrealized_pshr"]["background"] = "#ECF57C"
			self.order_tklabels[id_]["unrealized"]["background"] = "#ECF57C"

		if self.realized[id_]==0:
			self.order_tklabels[id_]["realized"]["background"] = "#d9d9d9"
		elif self.realized[id_]>0:
			self.order_tklabels[id_]["realized"]["background"] = "#3DFC68"
		elif self.realized[id_]<0:
			self.order_tklabels[id_]["realized"]["background"] = "#FC433D"



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
					self.status.set("Status: "+str(d[1]))
				except Exception as e:
					print(e)
			if d[0] =="pkg":
				print("new package arrived",d)
				self.goodtrade_listener(d[1])

	def delete(self):
		for i in self.tabs:
			for widget in i.winfo_children():
				widget.destroy()


	def register(self,symbol):
		if symbol not in self.symbols:
			self.symbols.append(symbol)
			self.register_to_ppro(symbol, True)			

	def deregister(self,symbol):

		if symbol in self.symbols:
			self.symbols.remove(symbol)
			self.register_to_ppro(symbol, False)

	def register_to_ppro(self,symbol,status):

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

	def register_order_listener(self):

		postbody = "http://localhost:8080/SetOutput?region=1&feedtype=OSTAT&output="+ str(self.port)+"&status=on"

		try:
			r= requests.get(postbody)
			if r.status_code==200:
				return True
			else:
				return False
		except:
			print("register failed")
			return False





if __name__ == '__main__':


# 	sell_limit_order("AAPL.NQ",150,2)
	#try:

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
	root.title("GoodTrade Algo Manager") 
	root.geometry("1000x800")
	root.minsize(1000, 800)
	root.maxsize(1800, 1200)

	view = algo_manager(root,port,goodtrade_pipe,ppro_pipe)

	receive_pipe.send(['New order', 'Break up2268503', 'Break up', 'QQQ.NQ', 'Pending', 'Breakout on Resistance on 338.85 for 0 sec', 'Long', 'Market', '338.85', '2104', 5050.0])

	root.mainloop()

	algo_voxcom.terminate()
	algo_voxcom.join()

	algo_ppro_manager.terminate()
	algo_ppro_manager.join()

	os._exit(1) 
