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


def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a

def hexcolor(level):
	try:
		code = int(510*(level))
		if code >255:
			first_part = code-255
			return "#FF"+hex_to_string(255-first_part)+"00"
		else:
			return "#FF"+"FF"+hex_to_string(255-code)
	except:
		return "#FFFFFF"



# class order_manager():

# 	def __init__(self):
		
# 		self.orders = {}

# 	def 

def buy_market_order(symbol,share):
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Buy ARCX Market DAY&shares='+str(share))
    if r.status_code == 200:
        print('buy market order Success!')
        return True
    else:
        print("Error sending buy order")

def sell_market_order(symbol,share):
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(share))
    if r.status_code == 200:
        print('sell market order Success!')
        #print(r.text)
        return True
    else:
        print("Error sending sell order")

def buy_limit_order(symbol, price,share):
    price = round(price,2)
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Buy ARCX Limit DAY&shares='+str(share))
    if r.status_code == 200:
        print('buy limit order Success! at',price)

        return True
    else:
        print("Error sending buy order")


def sell_limit_order(symbol, price,share):
    price = round(price,2)
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Sell->Short ARCX Limit DAY&shares='+str(share))
    if r.status_code == 200:
        print('sell limit order Success! at ',price)
        return True
    else:
        print("Error sending sell order")




class algo_manager(pannel):



	def __init__(self,root,port,gt_pipe,order_pipe):

		self.symbols = []

		self.port = port

		self.orders = []
		
		self.algo_status = {}
		
		self.current_share = {}
		self.current_share_data = {}
		self.target_share_data = {}

		self.realized = {}
		self.realized_data ={}

		self.unrealized = {}
		self.unrealized_data = {}

		self.order_book = {}

		self.average_price = {}
		self.average_price_data = {}

		self.position = {}
		#input symbol, get id (active.)
		self.active_order = {}

		super().__init__(root)

		self.width = [10,10,30,10,10,12,6,8,8,6]
		self.labels = ["Symbol","Algo status","Type","Position","Holding","Risk","Realized","Unrealized","flatten"]

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

	def update_display(self,id_):

		self.current_share[id_].set(str(self.current_share_data[id_])+"/"+str(self.target_share_data[id_]))

		self.realized[id_].set(str(self.realized_data[id_]))

		self.unrealized[id_].set(str(self.unrealized_data[id_]))


	def order_pipe_listener(self):
		while True:
			d = self.order_pipe.recv()


			if d[0] =="msg":

				print(d[1])

			if d[0] =="order confirm":
				#get symbol,price, shares.
				# maybe filled. maybe partial filled.
				data = d[1]
				symbol = data["symbol"]
				price = data["price"]
				shares = data["shares"]

				id_ = self.active_order[symbol]

				current = self.current_share_data[id_]
				self.current_share_data[id_] = current+shares

				if current ==0:
					self.average_price_data[id_] = round(price,2)
				else:
					self.average_price_data[id_] = round(((self.average_price_data[id_]*current)+(price*shares))/self.current_share_data[id_],2)

				self.update_display(id_)


			if d[0] =="order update":

				#update the quote, unrealized. 
				data = d[1]
				symbol = data["symbol"]
				bid = data["bid"]
				ask = data["ask"]

				#get position
				id_ = self.active_order[symbol]

				if self.position[id_]=="Long":
					price = bid
					gain = round((price-self.average_price_data[id_])*self.current_share_data[id_],2)

				elif  self.position[id_]=="Short":
					price = ask
					gain = round((self.average_price_data[id_]-price)*self.current_share_data[id_],2)

				#loss:
				#print(gain)
				self.unrealized_data[id_] = gain
				
				self.update_display(id_)

	def add_order(self,d):

		#['id', 'QQQ.NQ', 'Breakout on Support on 0.0 for 0 sec', 'Short', 20, 20.0]
		#handle database. and add labels. 


		#id, symbol, type, status, description, position, shares, risk$

		if d!=None:

			message_type = d[0]

			if message_type =="New order": 

				#['New order', 'Break up2268503', 'Break up', 'QQQ.NQ', 'Pending', 'Breakout on Resistance on 338.85 for 0 sec', 'Long', 'Market', '338.85', '2104', 5050.0]
				id_,symbol,type_,status,des,pos,order_type,order_price,share,risk = d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10]

				print(id_,"added to new order")
				if id_ not in self.orders:
					self.orders.append(id_)
					self.algo_status[id_] = tk.StringVar()
					self.algo_status[id_].set(status)

					self.current_share[id_] = tk.StringVar()
					self.current_share[id_].set("0/"+str(share))

					self.current_share_data[id_] = 0
					self.target_share_data[id_] = share

					self.realized[id_] = tk.StringVar()
					self.realized[id_].set("0")
					self.realized_data[id_] = 0

					self.unrealized[id_] = tk.StringVar()
					self.unrealized[id_].set("0")
					self.unrealized_data[id_] = 0

					self.average_price_data[id_] = 0

					self.order_book[id_] = [order_type,pos,order_price,share,symbol]

					#avoid repetitive order. 
					l = [symbol,self.algo_status[id_],des,pos,self.current_share[id_],risk,self.realized[id_],self.unrealized[id_]]
					#1,4,7
					self.add_new_labels(l)
				else:
					print("adding order failed")

			elif message_type =="Confirmed":
				id_ = d[1]
				print(id_,"confirmed and is a go")

				if id_ not in self.order_book:
					print("Cannot find order",order)
				else:
					order = self.order_book[id_] 

					type_ = order[0]
					pos = order[1]
					order_price = order[2]
					share = order[3]
					symbol = order[4]

					if type_ == "Market":

						if pos=="Long":
							buy_market_order(symbol,share)
							
							self.active_order[symbol] = id_
						elif pos =="Short":
							sell_market_order(symbol,share)

						self.algo_status[id_].set("Running")
							
					elif type_ =="Limit":
						if pos=="Long":
							buy_limit_order(symbol,order_price,share)
							
						elif pos =="Short":
							sell_market_order(symbol,order_price,share)

						self.algo_status[id_].set("Placed")

					self.register(symbol)


					self.active_order[symbol] = id_
					self.average_price[id_] = 0
					self.position[id_] = pos
						
	#info= 
	#symbol,status,type,position,curretn,shares,risk,p/l
	def add_new_labels(self,info):
		i = info[0]
		l = self.label_count

		self.tickers_labels[i]=[]
		self.tickers_tracers[i] = []
		#add in tickers.
		print("LENGTH",len(info))
		for j in range(len(info)):
			if j == 1 or j ==4 or j ==7 or j==8:
				self.tickers_labels[i].append(tk.Label(self.deployment_frame ,textvariable=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

			elif j != (len(info)-1):
				self.tickers_labels[i].append(tk.Label(self.deployment_frame ,text=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			#else: #command = lambda s=symbol: self.delete_symbol_reg_list(s))

		j+=1
		self.tickers_labels[i].append(tk.Button(self.deployment_frame ,text="flatten",width=self.width[j]))
		self.label_default_configure(self.tickers_labels[i][j])
		self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		self.ticker_count +=1
		self.label_count +=1

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

				self.add_order(d[1])

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

	port =4682

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
	os._exit(1) 