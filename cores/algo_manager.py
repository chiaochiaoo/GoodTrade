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



	def __init__(self,root,pipe):


		self.orders = []
		self.algo_status = {}
		self.current_share = {}
		self.realized = {}
		self.unrealized = {}


		super().__init__(root)

		self.width = [10,10,30,10,10,12,6,8,8,6]
		self.labels = ["Symbol","Algo status","Type","Position","Current hold","Entry Shares","Risk","Realized","Unrealized","flatten"]

		self.pipe = pipe

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

		# self.market = tk.StringVar(self.setting)
		# self.choices_m = {'All Markets','Nasdaq','NYSE','AMEX'}
		# self.market.set('Nasdaq') 

		# self.om = tk.OptionMenu(self.setting, self.market, *sorted(self.choices_m))
		# self.menu2 = ttk.Label(self.setting, text="Market").grid(row = 1, column = 1)
		# self.om.grid(row = 2, column =1)


		# self.refresh = tk.Button(self.setting,command= lambda: self.refresh_pannel()) #,command=self.loadsymbol
		# self.refresh.grid(row = 2, column =7)#.place(x=700, y=12, height=30, width=80, bordermode='ignore')
		# self.refresh.configure(activebackground="#ececec")
		# self.refresh.configure(activeforeground="#000000")
		# self.refresh.configure(background="#d9d9d9")
		# self.refresh.configure(disabledforeground="#a3a3a3")
		# self.refresh.configure(foreground="#000000")
		# self.refresh.configure(highlightbackground="#d9d9d9")
		# self.refresh.configure(highlightcolor="black")
		# self.refresh.configure(pady="0")
		# self.refresh.configure(text='''Apply filter''')

	def add_order(self,d):

		#['id', 'QQQ.NQ', 'Breakout on Support on 0.0 for 0 sec', 'Short', 20, 20.0]
		#handle database. and add labels. 


		#id, symbol, type, status, description, position, shares, risk$

		message_type = d[0]

		if message_type =="New order": 

			id_,symbol,type_,status,des,pos,share,risk = d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8] 

			print(id_,"added to new order")
			if id_ not in self.orders:
				self.orders.append(id_)
				self.algo_status[id_] = tk.StringVar()
				self.algo_status[id_].set(status)
				self.current_share[id_] = tk.StringVar()
				self.current_share[id_].set("0")
				self.realized[id_] = tk.StringVar()
				self.realized[id_].set("0")

				self.unrealized[id_] = tk.StringVar()
				self.unrealized[id_].set("0")

				#avoid repetitive order. 
				l = [symbol,self.algo_status[id_],des,pos,self.current_share[id_],share,risk,self.realized[id_],self.unrealized[id_]]
				#1,4,7
				self.add_new_labels(l)
			else:
				print("adding order failed")

		elif message_type =="Confirmed":
			id_ = d[1]
			print(id_,"confirmed")

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
		count = 0
		while True:
			d = self.pipe.recv()

			if d[0] =="msg":
				print(d[1])
				self.status.set("Status: "+str(d[1]))
			if d[0] =="pkg":
				print("new package arrived",d)

				self.add_order(d[1])

	def delete(self):
		for i in self.tabs:
			for widget in i.winfo_children():
				widget.destroy()

if __name__ == '__main__':


# 	sell_limit_order("AAPL.NQ",150,2)
	#try:
	multiprocessing.freeze_support()

	request_scanner, receive_pipe = multiprocessing.Pipe()
	algo_voxcom = multiprocessing.Process(target=algo_manager_voxcom, args=(receive_pipe,),daemon=True)
	algo_voxcom.daemon=True
	algo_voxcom.start()

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager") 
	root.geometry("1000x800")
	root.minsize(1000, 800)
	root.maxsize(1800, 1200)

	view = algo_manager(root,request_scanner)
	root.mainloop()
	algo_voxcom.terminate()
	algo_voxcom.join()
	os._exit(1) 