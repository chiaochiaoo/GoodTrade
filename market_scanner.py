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
import os

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
		self.setting.place(x=10,y=10,height=80,relwidth=1)

		self.market = tk.StringVar(self.setting)
		self.choices_m = {'All Markets','Nasdaq','NYSE','AMEX'}
		self.market.set('Nasdaq') 

		self.om = tk.OptionMenu(self.setting, self.market, *sorted(self.choices_m))
		self.menu2 = ttk.Label(self.setting, text="Market").grid(row = 1, column = 1)
		self.om.grid(row = 2, column =1)

		self.sector = tk.StringVar(self.setting)
		self.choices2 = {'All Sectors','Consumer Defensive','Financial','Industrials','Technology','Healthcare','Communication Services','Utilities','Real Estate','Energy','Basic Materials','Consumer Cyclical'}
		self.sector.set('All Sectors') 

		self.om2 = tk.OptionMenu(self.setting, self.sector, *sorted(self.choices2))
		self.menu2 = ttk.Label(self.setting, text="Sector").grid(row = 1, column = 2)
		self.om2.grid(row = 2, column =2)

		self.country = tk.StringVar(self.setting)
		self.choices = {'Any','USA','Canada','China','UK'}
		self.country.set('Any') 

		self.om3 = tk.OptionMenu(self.setting, self.country, *sorted(self.choices))
		self.menu1 = ttk.Label(self.setting, text="Country").grid(row = 1, column = 3)
		self.om3.grid(row = 2, column =3)


		self.mc = tk.StringVar(self.setting)
		self.mc_choice = {'Any','Small','Small & above','Medium','Medium & above','Large'}
		self.mc.set('Any') 

		self.om4 = tk.OptionMenu(self.setting, self.mc, *sorted(self.mc_choice))
		self.menu4 = ttk.Label(self.setting, text="Market Cap").grid(row = 1, column = 4)
		self.om4.grid(row = 2, column =4)

		self.relv = tk.StringVar(self.setting)
		self.relv_choice = {'0.5 above','1 above','2 above','Any'}
		self.relv.set('Any') 

		self.om3 = tk.OptionMenu(self.setting, self.relv, *sorted(self.relv_choice))
		self.menu1 = ttk.Label(self.setting, text="Min Rel.Volume").grid(row = 1, column = 5)
		self.om3.grid(row = 2, column =5)


		self.status = tk.StringVar()
		self.status.set("Status:")
		self.ppro_status = ttk.Label(self.setting, textvariable=self.status)
		self.ppro_status.place(x = 600, y =12)

		self.refresh = tk.Button(self.setting,command= lambda: self.refresh_pannel()) #,command=self.loadsymbol
		self.refresh.grid(row = 2, column =7)#.place(x=700, y=12, height=30, width=80, bordermode='ignore')
		self.refresh.configure(activebackground="#ececec")
		self.refresh.configure(activeforeground="#000000")
		self.refresh.configure(background="#d9d9d9")
		self.refresh.configure(disabledforeground="#a3a3a3")
		self.refresh.configure(foreground="#000000")
		self.refresh.configure(highlightbackground="#d9d9d9")
		self.refresh.configure(highlightcolor="black")
		self.refresh.configure(pady="0")
		self.refresh.configure(text='''Apply filter''')

		self.setting = ttk.LabelFrame(root,text="Market Heatmap") 
		self.setting.place(x=10,y=85,relheight=1,relwidth=1)

		self.in_progress = False

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
		self.tab2_buttons = []
		self.tab3_buttons = []
		self.tab4_buttons = []

		self.tabs=[self.tab1,self.tab2,self.tab3,self.tab4]

		self.data = None

		receiver = threading.Thread(target=self.receive, daemon=True)
		receiver.start()


	def refresh_pannel(self):

		print("progress:",self.in_progress)
		if self.in_progress == False:
			self.in_progress == True
			self.delete()
			pkg = self.filter(self.data)
			self.add_(pkg,self.tab1,"Close-price-ATR",self.tab1_buttons)
			self.add_(pkg,self.tab2,"Open-High-ATR",self.tab2_buttons)
			self.add_(pkg,self.tab3,"Open-Low-ATR",self.tab3_buttons)
			self.add_(pkg,self.tab4,"High-Low-ATR",self.tab4_buttons)
			self.in_progress == False
		else:
			self.status.set("Status: System updating, please wait..")
		print("progress:",self.in_progress)
	def rebind(self,canvas,frame):
		canvas.update_idletasks()
		canvas.config(scrollregion=frame.bbox()) 

	def receive(self):
		count = 0
		while True:
			d = self.pipe.recv()

			if d[0] =="msg":
				print(d[1])
				self.status.set("Status:"+d[1])
			if d[0] =="pkg":

				
				print("new package arrived")
				today = datetime.datetime.strftime(datetime.datetime.today() , '%H:%M:%S')
				self.status.set("Status:"+" Updated at "+today)
				pkg = d[1]

				self.data = pkg

				print("building start")
				if count %3 == 0:
					self.refresh_pannel()
				count +=1
				print("building finish")
			#update each. 

			#delete all first

			#add new ones. 

	def delete(self):
		for i in self.tabs:
			for widget in i.winfo_children():
				widget.destroy()

		# for j in self.tabs:
		# 	for i in j:
		# 		try:
		# 			i.grid_forget()
		# 			i.destroy()
		# 		except Exception as e:
		# 			pass
		# 			#print(e)
		# 	j = []

# self.add_(pkg,self.tab1,"Close-price-ATR",self.tab1_buttons)
# self.add_(pkg,self.tab2,"Open-High-ATR",self.tab2_buttons)
# self.add_(pkg,self.tab3,"Open-Low-ATR",self.tab3_buttons)
# self.add_(pkg,self.tab4,"High-Low-ATR",self.tab4_buttons)


	def filter(self,a):

		country = self.country.get() 
		if country != 'Any':
			a = a.loc[a["Country"]==country]

		mc = self.mc.get()

		if mc != 'Any':
			if mc =="Small":
				a = a.loc[a["Market Cap"]==2]
			elif mc =="Small & above":
				a = a.loc[a["Market Cap"]>=2]
			elif mc =="Medium":
				a = a.loc[a["Market Cap"]==3]
			elif mc =="Medium & above":
				a = a.loc[a["Market Cap"]>=3]
			elif mc =="Large":
				a = a.loc[a["Market Cap"]==4]

		return a

	def add_(self,a,pannel,type_,lst):

		#lets filter them out. Market Cap. Country.
		sectors = a["Sector"].unique()
		row = 1

		for i in sectors:

			if type_ == "Open-High-ATR" or type_ == "Open-Low-ATR":
				n = a.loc[(a["Sector"]==i)&(a["Open"]!=0)]
				n = n.loc[n[type_]>0.5]
			elif type_ == "Close-price-ATR":
				n = a.loc[(a["Sector"]==i)&(a["Prev Close P"]!=0)&(a["Price"]!=0)]
				n = n.loc[n[type_]>0.5]
			elif type_ == "High-Low-ATR":
				n = a.loc[a["Sector"]==i]
				n = n.loc[n[type_]>0.5]
			else:
				n = a.loc[a["Sector"]==i]


			n =n.sort_values(type_,ascending=False)
			n = n.iloc[:30]
			#take top 20.
			count = 1
			frame = ttk.Label(pannel,text=i) 
			frame.grid(row=row, column=count,padx=0)
			count +=1
			row +=1

			try:
				maxx = max(n[type_])
			except:
				maxx = 0

			for index,j in n.iterrows():
				symbol = tk.Button(pannel) #,command=loadsymbol
				symbol.configure(activebackground="#ececec")
				symbol.configure(activeforeground="#000000")
				symbol.configure(background=hexcolor(j[type_]/maxx))
				symbol.configure(disabledforeground="#a3a3a3")
				symbol.configure(foreground="#000000")
				symbol.configure(highlightbackground="#d9d9d9")
				symbol.configure(highlightcolor="black")
				symbol.configure(pady="0")
				symbol.configure(text=j.name+" "+str(j[type_]))
				symbol.grid(row= row, column=count,padx=0)

				#lst.append(symbol)

				if count == 20:
					count = 1
					row +=1
				count +=1

			row +=4






if __name__ == '__main__':

	#try:
	multiprocessing.freeze_support()

	request_scanner, receive_pipe = multiprocessing.Pipe()
	process_scanner = multiprocessing.Process(target=client_market_scanner, args=(receive_pipe,),daemon=True)
	process_scanner.daemon=True
	process_scanner.start()

	root = tk.Tk() 
	root.title("GoodTrade Market Scanner") 
	root.geometry("1200x800")
	root.minsize(1800, 1200)
	root.maxsize(1800, 1200)

	view = market_scanner(root,request_scanner)
	root.mainloop()
	process_scanner.terminate()
	process_scanner.join()
	os._exit(1) 