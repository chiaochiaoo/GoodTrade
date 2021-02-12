import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import os
import time
import threading

import sys



class algo_placer:

	def __init__(self,symbol,triggers):

		root = tk.Tk() 
		root.title("Algo Placer: "+symbol) 
		root.geometry("700x400")
		#root.minsize(600, 400)
		root.maxsize(700, 400)

		self.root = root

		self.symbol = tk.Label(root,text="Symbol: "+symbol)
		self.symbol.place(x=10,y=10)

		self.symbol = tk.Label(root,text="Trigger type: "+triggers)
		self.symbol.place(x=10,y=30)

		self.entry = ttk.LabelFrame(root,text="Entry") 
		self.entry.place(x=10,y=60,height=100,width=200)

		self.target = ttk.LabelFrame(root,text="Stoploss") 
		self.target.place(x=220,y=60,height=100,width=200)

		self.stop = ttk.LabelFrame(root,text="Position Management") 
		self.stop.place(x=440,y=60,height=100,width=200)	


		self.start()

		# sm = price_updater(self.data)
		# sm.start()


	def start(self):

		self.root.mainloop()

# class ticker_manager(pannel):
# 	def __init__(self,frame,data,alerts):
# 		super().__init__(frame)

# 		self.alerts = alerts

# 		self.Entry1 = tk.Entry(frame)
# 		self.Entry1.place(x=5, y=5, height=30, width=80, bordermode='ignore')
# 		self.Entry1.configure(background="white")
# 		self.Entry1.configure(cursor="fleur")
# 		self.Entry1.configure(disabledforeground="#a3a3a3")
# 		self.Entry1.configure(font="TkFixedFont")
# 		self.Entry1.configure(foreground="#000000")
# 		self.Entry1.configure(insertbackground="black")

# 		self.symbol = tk.Button(frame,command= lambda: self.add_symbol_reg_list(self.Entry1.get().upper())) #,command=self.loadsymbol
# 		self.symbol.place(x=105, y=5, height=30, width=80, bordermode='ignore')
# 		self.symbol.configure(activebackground="#ececec")
# 		self.symbol.configure(activeforeground="#000000")
# 		self.symbol.configure(background="#d9d9d9")
# 		self.symbol.configure(disabledforeground="#a3a3a3")
# 		self.symbol.configure(foreground="#000000")
# 		self.symbol.configure(highlightbackground="#d9d9d9")
# 		self.symbol.configure(highlightcolor="black")
# 		self.symbol.configure(pady="0")
# 		self.symbol.configure(text='''Add Symbol''')

# 		#"Ppro Status: "+"Connecting"
# 		self.ppro_status = ttk.Label(frame, textvariable=data.ppro_status)
# 		self.ppro_status.place(x = 200, y =12)
# 		#data.ppro_status.set("Hello")

# 		self.ticker_stats = ttk.Label(frame, text="Current Registered Tickers: "+str(self.ticker_count))
# 		self.ticker_stats.place(x = 500, y =12)

# 		#############Registration Window ####################

# 		self.data = data


# 		self.width = [8,10,12,10,24,10,10]
# 		self.labels = ["Ticker","Status","Last update","Price","Last Alert","Last Alert time","Remove"]

# 		#init the labels. 
# 		self.labels_creator(self.frame)



algo_placer("AAPL.NQ","Breakout")