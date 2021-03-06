import tkinter as tk
from tkinter import ttk

import socket
import pickle
import pandas as pd
import time
import multiprocessing
import threading
from pannel import *

def client_market_scanner(pipe):
	while True:

		HOST = '10.29.10.132'  # The server's hostname or IP address
		PORT = 65422       # The port used by the server

		try:

			print("Trying to connect to the server")
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
				try:
					s.sendall(b'Alive check')
				except:
					connection = False
					break
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
							#k = pd.read_pickle(b"".join(data))
							break
						except:
							pass
				#k is received. 
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



class market_scanner:

	def __init__(self,root,pipe):

		self.pipe = pipe

		self.setting = ttk.LabelFrame(root,text="Market Heatmap Setting") 
		self.setting.place(x=10,y=10,height=80,width=780)

		self.market = tk.StringVar(self.setting)
		self.choices_m = {'All Markets','Nasdaq','NYSE','AMEX'}
		self.market.set('Nasdaq') 

		self.om = tk.OptionMenu(self.setting, self.market, *sorted(self.choices_m))
		self.menu2 = ttk.Label(self.setting, text="Market").grid(row = 1, column = 1)
		self.om.grid(row = 2, column =1)

		self.sector = tk.StringVar(self.setting)
		self.choices2 = {'All Sectors','Consumer Defensive','Financial','Industrials','Technology','Healthcare','Communication Services','Utilities','Real Estate','Energy','Basic Materials','Consumer Cyclical'}
		self.sector.set('Technology') 

		self.om2 = tk.OptionMenu(self.setting, self.sector, *sorted(self.choices2))
		self.menu2 = ttk.Label(self.setting, text="Sector").grid(row = 1, column = 2)
		self.om2.grid(row = 2, column =2)

		self.country = tk.StringVar(self.setting)
		self.choices = {'All countries','US','Canada','China','UK'}
		self.country.set('All countries') 

		self.om3 = tk.OptionMenu(self.setting, self.country, *sorted(self.choices))
		self.menu1 = ttk.Label(self.setting, text="Country").grid(row = 1, column = 3)
		self.om3.grid(row = 2, column =3)

		self.relv = tk.StringVar(self.setting)
		self.relv_choice = {'0.5 above','1 above','2 above','Any'}
		self.relv.set('Any') 

		self.om3 = tk.OptionMenu(self.setting, self.country, *sorted(self.relv_choice))
		self.menu1 = ttk.Label(self.setting, text="Min Rel.Volume").grid(row = 1, column = 4)
		self.om3.grid(row = 2, column =4)

		self.setting = ttk.LabelFrame(root,text="Market Heatmap") 
		self.setting.place(x=10,y=85,height=800,width=780)

		self.tabControl = ttk.Notebook(self.setting)
		self.tabControl.place(x=10,rely=0,relheight=1,relwidth=1)
		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)
		self.tab3 = tk.Canvas(self.tabControl)
		self.tab4 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Prev Close') 
		self.tabControl.add(self.tab2, text ='Open High') 
		self.tabControl.add(self.tab3, text ='Open Low') 
		self.tabControl.add(self.tab4, text ='High Low') 


		self.tab1_buttons = []

		receiver = threading.Thread(target=self.receive, daemon=True)
		receiver.start()


	def rebind(self,canvas,frame):
		canvas.update_idletasks()
		canvas.config(scrollregion=frame.bbox()) 

	def receive(self):

		while True:
			d = self.pipe.recv()

			if d[0] =="msg":
				print(d[1])
			if d[0] =="pkg":
				print("new package arrived")
				pkg = d[1]

				self.delete()
				self.add_(pkg)

			
			#update each. 

			#delete all first

			#add new ones. 

	def delete(self):
		for i in self.tab1_buttons:
			i.destroy()

	def add_(self,a):
		sectors = a["Sector"].unique()
		row = 1
		for i in sectors:
			n = a.loc[a["Sector"]==i]
			n =n.sort_values("Close-price-ATR",ascending=False)
			n = n.iloc[:25]
			#take top 20.
			count = 1
			frame = ttk.Label(self.tab1,text=i) 
			frame.grid(row=row, column=count,padx=0)
			count +=1
			row +=1

			maxx = max(n['Close-price-ATR'])
			for index,j in n.iterrows():
				symbol = tk.Button(self.tab1) #,command=loadsymbol
				symbol.configure(activebackground="#ececec")
				symbol.configure(activeforeground="#000000")
				symbol.configure(background=hexcolor(j['Close-price-ATR']/maxx))
				symbol.configure(disabledforeground="#a3a3a3")
				symbol.configure(foreground="#000000")
				symbol.configure(highlightbackground="#d9d9d9")
				symbol.configure(highlightcolor="black")
				symbol.configure(pady="0")
				symbol.configure(text=j.name+" "+str(j['Close-price-ATR']))
				symbol.grid(row= row, column=count,padx=0)

				self.tab1_buttons.append(symbol)

				if count == 8:
					count = 1
					row +=1
				count +=1

			row +=4


		self.rebind(self.canvas,self.frame)



if __name__ == '__main__':

	#try:
	multiprocessing.freeze_support()

	request_scanner, receive_pipe = multiprocessing.Pipe()
	process_scanner = multiprocessing.Process(target=client_market_scanner, args=(receive_pipe,),daemon=True)
	process_scanner.daemon=True
	process_scanner.start()

	root = tk.Tk() 
	root.title("GoodTrade Market Scanner") 
	root.geometry("800x400")
	root.minsize(1400, 1200)
	root.maxsize(1800, 900)

	view = market_scanner(root,request_scanner)
	root.mainloop()