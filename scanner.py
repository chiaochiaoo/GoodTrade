import tkinter as tk                     
from tkinter import ttk 
import threading
from pannel import *

from scanner_process_manager import *


def status_change(var,label):
	label["text"] = "Current Status: "+var.get()

class scanner(pannel):

	def __init__(self,root,tickers_manager,scanner_process:scanner_process_manager):

		super()

		self.tickers_manager = tickers_manager

		self.scanner_process_manager = scanner_process

		self.setting = ttk.LabelFrame(root,text="Scanner Settings") 
		self.setting.place(relx=0.01, rely=0.05, relheight=1, width=480)

		self.refresh = ttk.Button(self.setting,  
			text ="Fetch Data",command=self.refresh).place(relx=0.8, rely=0.01, height=50, width=70)   

		self.market = tk.StringVar(self.setting)
		self.choices2 = {'Nasdaq','NYSE','AMEX'}
		self.market.set('Nasdaq') 

		self.popupMenu2 = tk.OptionMenu(self.setting, self.market, *self.choices2)
		self.menu2 = ttk.Label(self.setting, text="Select Market").grid(row = 1, column = 1)
		self.popupMenu2.grid(row = 2, column =1)

		self.signal = tk.StringVar(self.setting)
		self.choices = { 'Most Active','Unusual Volume','Top Gainner','New Highs'}
		self.signal.set('Most Active') 

		self.popupMenu = tk.OptionMenu(self.setting, self.signal, *self.choices)
		self.menu1 = ttk.Label(self.setting, text="Select signal type").grid(row = 1, column = 2)
		self.popupMenu.grid(row = 2, column =2)

		self.relv = tk.StringVar(self.setting)
		self.relvc = {'0.5','1','2','3'}
		self.relv.set('2') 

		self.popupMenu3 = tk.OptionMenu(self.setting, self.relv, *self.relvc)
		self.menu3 = ttk.Label(self.setting, text="Min RelVol").grid(row = 1, column = 3)
		self.popupMenu3.grid(row = 2, column =3)

		self.markcap = tk.StringVar(self.setting)
		self.markcapchoice = {'Any','Mega','Large','Mid','Small','Large+','Mid+','Small+'}
		self.markcap.set('Any') 

		self.popupMenu4 = tk.OptionMenu(self.setting, self.markcap, *self.markcapchoice)
		self.menu4 = ttk.Label(self.setting, text="Market Cap").grid(row = 1, column = 4)
		self.popupMenu4.grid(row = 2, column =4)


		self.downloading = False

		self.status_info = ttk.Label(self.setting, text="Current Status: ")
		self.status = tk.StringVar()
		self.status.trace('w', lambda *_, var=self.status,label=self.status_info:status_change(var,label))
		self.status_info.place(x = 0, y =60)

		self.status.set("Ready")

		self.tab = ttk.LabelFrame(self.setting,text="Scanner") 
		self.tab.place(x=0, y=80, relheight=0.85, relwidth=1)

		self.scanner_canvas = tk.Canvas(self.tab)
		self.scanner_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.tab)
		self.scroll.config(orient=tk.VERTICAL, command=self.scanner_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")

		self.scanner_canvas.configure(yscrollcommand=self.scroll.set)
		#self.scanner_canvas.bind('<Configure>', lambda e: self.scanner_canvas.configure(scrollregion = self.scanner_canvas.bbox('all')))

		self.scanner_frame = tk.Frame(self.scanner_canvas)
		self.scanner_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.scanner_canvas.create_window(0, 0, window=self.scanner_frame, anchor=tk.NW)

		labels = ["Symbol","Rel.V","Price","Change","Perf Week","MCap","Inst own",\
		"Inst tran","Insi own","Insi tran","Short float","Short Ratio","Prem Low","Prem high","Prem Avg","Status"]
		width = [8,6,6,6,8,8,8,8,8,8,10,10,10,10,10,10]

		width = [8,12,10,6,10,10]
		labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]

		self.info = []

		for i in range(len(labels)): #Rows
			self.b = tk.Button(self.scanner_frame, text=labels[i],width=width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)

		self.rebind(self.scanner_canvas,self.scanner_frame)


	def status_change(self,var):
		self.status.set(var)

	def market_suffix(self):
		market_ = self.market.get()
		market = ""
		if market_ == 'Nasdaq':
			market = '.NQ'
			#cond = 'sh_relvol_o2'

		elif market_ =='NYSE':
			market = '.NY'
			#cond = 'sh_relvol_o1'

		elif market_ =='AMEX':
			market = '.AM'
		return market

	#This is the button function. 
	#Take all the information needed and send it to the new process. 


	#Steps1. Asychonous Version.
	#Steps2. Synchonous Version. - Just need to let it load, and then call it and sne,.d 

	def delete_old_lables(self):

		if len(self.info)>0:
			for i in self.info:
				for j in i:
					j.destroy()

		

	def refresh(self):

		#this is where it downloads the stock info. Turn this into multi processing. just allocate the info and send it.

		cond = "sh_relvol_o"+self.relv.get()
		market_ = self.market.get()
		type_ = self.signal.get()
		cap = self.markcap.get() 

		self.delete_old_lables()

		self.scanner_process_manager.send_request(cond,market_,type_,cap)
		

	def add_labels(self,d):
		#This is where it adds the labels. 

		if (len(d)==0):
			#got nothing!
			self.status_change("Unmatch results")
			self.scanner_process_manager.adding_comlete()
		else:
			width = [8,12,10,6,10,10]
			labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]
			suffix = self.market_suffix()

			self.info = []
			good = True
			try:
				for i in range(len(d)):
					#info = [d.iloc[i]["Ticker"],d.iloc[i]["Volume"],d.iloc[i]["Avg Volume"],d.iloc[i]["Rel Volume"],\d.iloc[i]["Change"],"","","",""]
					info = [d[i]["Ticker"],d[i]["Volume"],d[i]["Avg Volume"],d[i]["Rel Volume"],\
					d[i]["Change"],"","","",""]
					self.info.append([])
					for j in range(len(labels)):
						if j!= len(labels)-1:
							self.info[i].append(tk.Label(self.scanner_frame ,text=info[j],width=width[j]))
							#self.label_default_configure(self.info[i][j])
							self.info[i][j].grid(row=i+2, column=j,padx=0)
						else:
							self.info[i].append(tk.Button(self.scanner_frame ,text=info[j],width=width[j],command= lambda k=i: self.tickers_manager.add_symbol_reg_list(d[k]["Ticker"]+suffix)))
							#self.label_default_configure(self.info[i][j])
							self.info[i][j].grid(row=i+2, column=j,padx=0)
			except:
				good = False
			
			super().rebind(self.scanner_canvas,self.scanner_frame)

			self.scanner_process_manager.adding_comlete()

			if good:
				self.scanner_process_manager.adding_comlete()
				self.status_change("Ready")
			else:
				self.status_change("Please retry")
				self.scanner_process_manager.adding_comlete()
			 

