import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import database as db
import Spread_viewer_function as SVF
import numpy as np

from datetime import datetime

from Symbol_data_manager import *

# from modules.pannel import *
# from modules.scanner_process_manager import *

from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import matplotlib.ticker as mtick
from pannel import *
from tkinter import *


def ts_to_str(timestamp):
	
	h= int(timestamp//60)
	m= int(timestamp%60)
	
	if h//10 == 0:
		h = "0"+str(h)
	else:
		h = str(h)
		
	if m//10 == 0:
		m = "0"+str(m)
	else:
		m = str(m)
		
	return(h+":"+m)

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

		self.symbolist = {'Unselected','SPY.AM','QQQ.NQ','USO.AM','SMH.AM','KRE.AM'}

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
### SC QQQ
### SC SPY
### AVG. C
###
###
###

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
			if self.symbol1.get()!='Unselected' and self.symbol2.get()!='Unselected':
				return True

		return False

	def create_new_tab(self):


		if self.validation():

			symbol1 = self.symbol1.get()
			symbol2 = self.symbol2.get()
			pair_name = symbol1[:-3]+symbol2[:-3]
			self.tabs[pair_name] = tk.Canvas(self.spread_lists)


			# self.graph = ttk.LabelFrame(self.tabs[pair_name])
			# self.graph.place(relx=0,y=0,relheight=1,relwidth=0.8)

			self.spread_lists.add(self.tabs[pair_name], text =pair_name) 

			

			#For majortiy just once set.

			#Only update is Current Max Spread. 
			#And Current Spread.
			#Current Spread graph. etc. 


			outlier = dict(linewidth=3, color='darkgoldenrod',marker='o')
			plt.style.use("seaborn-darkgrid")
			f = plt.figure(1,figsize=(10,8))
			f.canvas.set_window_title('SPREAD MONITOR')
			min_form = DateFormatter("%H:%M")
			sec_form = DateFormatter("%M:%S")
			gs = f.add_gridspec(4, 4)


			pair = spread(symbol1, symbol2,self.data)

			spread_data,spread_time,current_spread = pair.get_current_data()
			m_dis,w_dis,roc1l,roc5l,roc15l = pair.get_hist_data()


			spread_time = pd.to_datetime(spread_time,format='%H:%M')

			spread_ = f.add_subplot(gs[0,:-1])
			spread_.tick_params(axis='both', which='major', labelsize=8)
			spread_line,=spread_.plot(spread_time,spread_data)

			spread_.xaxis.set_major_formatter(min_form)
			spread_.yaxis.set_major_formatter(mtick.PercentFormatter())
			spread_.set_title('IntraDay Spread')

			max_spread_d = f.add_subplot(gs[1,0])
			max_spread_d.set_title('Spread Today')
			max_spread_d.boxplot([], flierprops=outlier,vert=False, whis=1)
			cur_spread1 = max_spread_d.axvline(x=current_spread,color="r")

			max_spread_w = f.add_subplot(gs[1,1])
			max_spread_w.set_title('Spread Weekly')
			max_spread_w.boxplot(w_dis, flierprops=outlier,vert=False, whis=1)
			cur_spread2 = max_spread_w.axvline(x=current_spread,color="r")

			max_spread_m = f.add_subplot(gs[1,2])
			max_spread_m.set_title('Spread Monthly')
			max_spread_m.boxplot(m_dis, flierprops=outlier,vert=False, whis=1)
			cur_spread3 = max_spread_m.axvline(x=current_spread,color="r")

			roc1 = f.add_subplot(gs[2,0])
			roc1.set_title('Change 1 min')
			roc1.boxplot(roc1l, flierprops=outlier,vert=False, whis=2.5)
			roc1_ = roc1.axvline(x=0,color="r")

			roc5 = f.add_subplot(gs[2,1])
			roc5.set_title('Change 5 min')
			roc5.boxplot(roc5l, flierprops=outlier,vert=False, whis=1.5)
			roc5_ = roc5.axvline(x=0,color="r")

			roc15 =f.add_subplot(gs[2,2])
			roc15.set_title('Change 15 min')
			roc15.boxplot(roc15l, flierprops=outlier,vert=False, whis=1.5)
			roc15_ = roc15.axvline(x=0,color="r")

			pair.set_graphical_components([[cur_spread1,cur_spread2,cur_spread3],[spread_line,roc1_,roc5_,roc15_]]) 
		

			plt.tight_layout()
			plotcanvas = FigureCanvasTkAgg(f, self.tabs[pair_name])
			plotcanvas.get_tk_widget().grid(column=1, row=1)

			# self.tab1 = tk.Canvas(self.tabControl)
			# self.tab2 = tk.Canvas(self.tabControl)

			# 

#the data object.

class spread:

	def __init__(self,symbol1,symbol2,data:Symbol_data_manager):

		self.data = data

		self.trace = []

		self.symbol1= symbol1
		self.symbol2= symbol2 

		self.spreads = []
		self.minutes = []

		#now = datetime.now()
		#now.hour*60 + now.minute
		self.current_minute = 0 
		self.current_spread = 0

		self.roc1 = 0
		self.roc5 = 0
		self.roc15 = 0

		#necessary data.

		#m_dis,w_dis,roc1l,roc5l,roc15l
		symbols = [self.symbol1[:-3],self.symbol2[:-3]]
		self.m_dis,self.w_dis,self.roc1l,self.roc5l,self.roc15l = SVF.find_info(symbols)

		now = datetime.now()
		ts=now.hour*60 + now.minute
		print(ts)
		if ts>570:
			self.fetch_missing_data()

			#missing data fetched

			print("missing data fetched ")
		self.lock = False

		#if this is created after 9:30.
		# if before 9:30. 






		#set the graph. 

		#m=self.data.symbol_price[symbol1].trace('w', lambda *_, text=info[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
		# m=self.data.symbol_price[symbol1].trace('w', self.spread_update)
		# self.trace.append(m)

		# m=self.data.symbol_price[symbol2].trace('w', self.spread_update)
		# self.trace.append(m)


	def get_hist_data(self):

		return self.m_dis,self.w_dis,self.roc1l,self.roc5l,self.roc15l

	def get_current_data(self):

		return 	self.spreads,self.minutes,self.current_spread
		

	def set_graphical_components(self,gc):

		#unpack
		self.current_spread_graph_list = gc[0]
		self.intraday_spread_graph = gc[1][0]
		self.roc1_graph =  gc[1][1]
		self.roc5_graph =  gc[1][2]
		self.roc15_graph =  gc[1][3]


	def fetch_missing_data(self):

		ts = []
		ps = []
		s=[self.symbol1[:-3],self.symbol2[:-3]]

		for i in s:
			timestamp,price = SVF.fetch_data_yahoo(i)
			ts.append(timestamp[:-2])
			ps.append(price[:-2])

		#print(ts,ps)

		#MUST SYNC THE DATA.
		if len(ts[1]) > len(ts[0]):
			for i in range(len(ts[1])-len(ts[0])):
				ps[0].append(ps[0][-1])
			ts[0] = ts[1][:]
		else:
			for i in range(len(ts[0])-len(ts[1])):
				ps[1].append(ps[1][-1])
			ts[1] = ts[0][:]

		#Now let's set init.

		#Spread.
		# print(ps[0])
		# print(ps[1])
		c1 = (np.array(ps[0])-ps[0][0])*100/ps[0][0]
		c2 = (np.array(ps[1])-ps[1][0])*100/ps[1][0]

		intra_spread = list(c1 - c2)

		# self.intra_spread_MA5 = list(chiao.SMA(self.intra_spread, 5))
		# self.intra_spread_MA15 = list(chiao.SMA(self.intra_spread, 15))

		cur_minute_list = ts[0][:]

		#Time 
		self.spreads = intra_spread
		self.minutes = cur_minute_list
		self.current_minute = cur_minute_list[-1]
		self.current_spread = intra_spread[-1]

	#when either of the price is updated. this is called. 
	def spread_update(self):
		if self.lock == False:
			self.lock = True

			#update the data.

			now = datetime.now()
			ts = now.hour*60 + now.minute

			self.current_minute = ts
			self.current_spread = self.data.symbol_percentage_since_open[self.symbol1] - self.data.symbol_percentage_since_open[self.symbol2]


			if len(self.intra_spread)>0: 

				self.roc1 = self.current_spread - self.spreads[-1]      
				len_ = min(5, len(self.intra_spread)-1)

				#print(len_,self.intra_spread[-len_],self.spread)
				self.roc5 = self.current_spread- self.spreads[-len_] 

				len_ = min(15, len(self.intra_spread)-1)
				#print(len_,self.intra_spread[-len_],self.spread)
				self.roc15 = self.current_spread-self.spreads[-len_] 

			if ts>self.current_minute:
				self.spreads.append(self.current_spread)
				self.time.append(ts_to_str(self.current_minute))


			self.lock = False

	def update_graph(self):
		pass

root = tk.Tk() 
root.title("GoodTrade PairTrader") 

s = spread_trader(root,None,None)
root.geometry("700x800")
root.minsize(1000, 800)
root.maxsize(1800, 1200)
root.mainloop()

#spread("SPY.AM", "QQQ.NQ", None)