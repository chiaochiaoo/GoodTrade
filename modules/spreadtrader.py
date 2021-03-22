import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import database as db
import Spread_viewer_function as SVF
# from modules.pannel import *
# from modules.scanner_process_manager import *


from pannel import *

from tkinter import *

def status_change(var,label):
	label["text"] = "Current Status: "+var.get()

class spread_trader(pannel):

	def __init__(self,root,tickers_manager,data):

		super()

		self.data = data
		#mark if already created. if so, just update the infos. 


		#a giant labelframe

		self.main = ttk.LabelFrame(root,text="Spread")
		self.main.place(x=10,y=10,relheight=1,relwidth=0.95)


		self.spread_lists = ttk.Notebook(self.main)
		self.spread_lists.place(x=0,rely=0.1,relheight=0.9,relwidth=1)


		self.symbol1 = tk.StringVar(self.main)
		self.symbol2 = tk.StringVar(self.main)

		self.symbolist = {'Unselected','SPY.AM','QQQ.NQ','USO.AM'}

		self.symbol1.set('Unselected') 
		self.symbol2.set('Unselected') 

		self.op1 = tk.OptionMenu(self.main, self.symbol1,*sorted(self.symbolist))
		self.op1_sub = ttk.Label(self.main, text="Symbol 1").grid(row = 1, column = 1)
		self.op1.grid(row = 2, column =1)
		#self.op1.place(x=25, y=40, height=30, width=100)

		self.op2 = tk.OptionMenu(self.main, self.symbol2,*sorted(self.symbolist))
		self.op2_sub = ttk.Label(self.main, text="Symbol 2").grid(row = 1, column = 2)
		self.op2.grid(row = 2, column =2)
		#self.menu1 = ttk.Label(self.setting, text="Country").grid(row = 1, column = 3)

		self.refresh_symbols = ttk.Button(self.main,text ="Refresh Symbol",width=15).grid(row = 1, column = 3)#.place(relx=0.01, rely=0.01, height=25, width=70)
		self.add_symbols = ttk.Button(self.main,text ="Create pair",command=self.create_new_tab,width=15).grid(row =2, column = 3)#.place(relx=0.01, rely=0.01, height=25, width=70)

		#a button
		#two lists.
		# an add symbol


		self.tabs = {}

		# self.tab1 = tk.Canvas(self.tabControl)
		# self.tab2 = tk.Canvas(self.tabControl)

		# self.tabControl.add(self.tab2, text ='Nasdaq Trader') 
		# self.tabControl.add(self.tab1, text ='Finviz') 


		
		# self.nasdaq = []
		# ############################### Nasdaq Trader ############################################





		# self.update_in_progress = False



		# self.add_button = ttk.Button(self.tab2,
		# 	text ="Add").place(x=380, rely=0.01, height=25, width=70)


		# self.NT_update_time = tk.StringVar(root)
		# self.NT_update_time.set('Last updated') 

		# self.NT_stat = ttk.Label(self.tab2, textvariable=self.NT_update_time).place(x=10, rely=0.01, height=25, width=200)


		# #self.NT = ttk.Notebook(self.tab2)
		# #self.NT.place(x=0,rely=0.05,relheight=1,width=500)

		# self.all = tk.Canvas(self.tab2)
		# self.all.place(x=0,rely=0.05,relheight=1,width=600)



		# width = [8,12,10,6,10,10]
		# labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]

		# self.info = []

		# for i in range(len(labels)): #Rows
		# 	self.b = tk.Button(self.scanner_frame, text=labels[i],width=width[i])#,command=self.rank
		# 	self.b.configure(activebackground="#f9f9f9")
		# 	self.b.configure(activeforeground="black")
		# 	self.b.configure(background="#d9d9d9")
		# 	self.b.configure(disabledforeground="#a3a3a3")
		# 	self.b.configure(relief="ridge")
		# 	self.b.configure(foreground="#000000")
		# 	self.b.configure(highlightbackground="#d9d9d9")
		# 	self.b.configure(highlightcolor="black")
		# 	self.b.grid(row=1, column=i)

		# self.rebind(self.scanner_canvas,self.scanner_frame)

	def validation(self):

		if self.symbol1.get()[:-3]!=self.symbol2.get()[:-3]:
			if self.symbol1.get()!='Unselected':
				return True

		return False

	def create_new_tab(self):


		if self.validation():
			pair_name = self.symbol1.get()[:-3]+self.symbol2.get()[:-3]
			self.tabs[pair_name] = tk.Canvas(self.spread_lists)

			self.spread_lists.add(self.tabs[pair_name], text =pair_name) 

			symbols = [self.symbol1.get()[:-3],self.symbol2.get()[:-3]]

			m_dis,w_dis,roc1l,roc5l,roc15l = SVF.find_info(symbols)

			#successful 
			print(m_dis,w_dis,roc1l,roc5l,roc15l)

			# self.tab1 = tk.Canvas(self.tabControl)
			# self.tab2 = tk.Canvas(self.tabControl)

			# 


root = tk.Tk() 
root.title("GoodTrade Algo Manager") 


s = spread_trader(root,None,None)
root.geometry("1000x800")
root.minsize(1000, 800)
root.maxsize(1800, 1200)
root.mainloop()