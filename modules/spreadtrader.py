import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import numpy as np
from datetime import datetime

import time

from modules.pannel import *
from modules.Symbol_data_manager import *
import modules.database as db
import modules.Spread_viewer_function as SVF

#import Spread_viewer_function as SVF
#from modules.scanner_process_manager import *
#from pannel import *
#from Symbol_data_manager import *
#import database as db


from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import matplotlib.ticker as mtick

from tkinter import *

def timestamp(s):

	p = s.split(":")
	try:
		x = int(p[0])*60+int(p[1])
		return x
	except Exception as e:
		print(e)
		return 0

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

	def __init__(self,root,data):

		super()

		self.data = data
		#mark if already created. if so, just update the infos. 

		self.tab_count = 0
		#a giant labelframe

		self.main = ttk.LabelFrame(root,text="Spread")
		self.main.place(x=10,y=10,relheight=1,relwidth=0.95)


		self.spread_lists = ttk.Notebook(self.main)
		self.spread_lists.place(x=0,rely=0.1,relheight=0.9,relwidth=1)


		self.symbol1 = tk.StringVar(self.main)
		self.symbol2 = tk.StringVar(self.main)

		self.refresh_symbol_list()

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

		self.refresh_symbols = ttk.Button(self.main,text ="Refresh Symbol",width=15,command=self.refresh_options).grid(row = 1, column = 3)#.place(relx=0.01, rely=0.01, height=25, width=70)
		self.add_symbols = ttk.Button(self.main,text ="Create pair",command=self.create_new_tab,width=15).grid(row =2, column = 3)#.place(relx=0.01, rely=0.01, height=25, width=70)


		self.tabs = {}



	def refresh_symbol_list(self):

		if self.data!=None:
			self.symbolist = set(self.data.get_list())

			if len(self.symbolist)==0:
				self.symbolist = set(" ")
		else:
			self.symbolist= set(" ")

	def refresh_options(self):

		self.refresh_symbol_list()
		self.op1['menu'].delete(0, 'end')
		self.op2['menu'].delete(0, 'end')
		# Insert list of new options (tk._setit hooks them up to var)

		for choice in self.symbolist:
			 self.op1['menu'].add_command(label=choice, command=tk._setit(self.symbol1, choice))
			 self.op2['menu'].add_command(label=choice, command=tk._setit(self.symbol2, choice))
					

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

			self.spread_lists.add(self.tabs[pair_name], text =pair_name) 


			#For majortiy just once set.

			#Only update is Current Max Spread. 
			#And Current Spread.
			#Current Spread graph. etc. \\\\\\
			exsit=False
			if self.tab_count>0:
				exsit= True

			pair = spread(symbol1, symbol2,self.data,self.tabs[pair_name],exsit)
			self.tab_count+=1




			# self.tab1 = tk.Canvas(self.tabControl)
			# self.tab2 = tk.Canvas(self.tabControl)

			# 

#the data object.

class spread:

	def __init__(self,symbol1,symbol2,data:Symbol_data_manager,pannel,exsit):


		self.data = data
		self.exsit = exsit
		self.trace = []
		self.pannel = pannel



		self.symbol1= symbol1
		self.symbol2= symbol2 
		self.ratio = tk.StringVar()
		self.spreads = []
		self.minutes = []

		#now = datetime.now()
		#now.hour*60 + now.minute
		self.current_minute = 0 
		self.current_spread = 0

		self.roc1 = 0
		self.roc5 = 0
		self.roc15 = 0

		self.lock = False

		self.i= 0
		#necessary data.
		self.col = 0

		#m_dis,w_dis,roc1l,roc5l,roc15l
		symbols = [self.symbol1[:-3],self.symbol2[:-3]]
		self.m_dis,self.w_dis,self.roc1l,self.roc5l,self.roc15l = SVF.find_info(symbols) #[],[],[],[],[] #



		self.graph = ttk.LabelFrame(self.pannel)
		self.graph.place(relx=0,y=0,relheight=1,relwidth=0.8)

		self.chart = ttk.LabelFrame(self.pannel)
		self.chart.place(relx=0.8,y=0,relheight=1,relwidth=0.2)

		now = datetime.now()
		ts=now.hour*60 + now.minute
		#print(ts)
		if ts>570:
			self.fetch_missing_data()

			print("missing data fetched ")
		
		self.create_graphs()

		self.create_chart()
		#if this is created after 9:30.
		# if before 9:30. 

		reg = threading.Thread(target=self.calculate_ratio, daemon=True)
		reg.start()
		#set the graph. 

		#m=self.data.symbol_price[symbol1].trace('w', lambda *_, text=info[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))


	def calculate_ratio(self):

		while True:
			a=self.data.symbol_status[self.symbol1].get()
			b=self.data.symbol_status[self.symbol2].get()

			if a==b and a=="Connected":
				break
			else:
				time.sleep(5)

		print("Price get.")
		price1= float(self.data.symbol_price[self.symbol1].get())
		price2= float(self.data.symbol_price[self.symbol2].get())

		ratio = self.ratio_compute(price1,price2)

		s = str(ratio[0])+":"+str(ratio[1])
		self.ratio.set(s)

	def ratio_compute(self,a,b):
		a_=[]
		b_=[]
		turn = 0
		while True:
			if turn==0:
				a_.append(a)
				#print(a_)
			else:
				b_.append(b)
				#print(b_)

			#check differentce. who's losing, who's turn is it.
			ratio = (b*len(b_))/(a*len(a_))
			#print(ratio)
			if ratio>0.998 and ratio<1.002:
				break
			else:
				if ratio>1:
					turn=0
				else:
					turn=1

		return (len(a_),len(b_))


	def create_chart(self):


		#self.col+=1

		self.b=tk.Button(self.chart,text="Pair Research")
		self.b.grid(row=self.col,column=0)

		self.b=tk.Button(self.chart,text="Back Test")
		self.b.grid(row=self.col,column=1)
		self.col+=1

		self.b=tk.Button(self.chart,text="Create Algo")
		self.b.grid(row=self.col,column=0)

		self.b=tk.Button(self.chart,text="Close Chart")
		self.b.grid(row=self.col,column=1)
		self.col+=1

		#width = [8,12,10,6,10,10]

		labels ={"Attribute":"Value",\
				 "SC:"+self.symbol1[:-3]:self.data.symbol_percentage_since_close[self.symbol1],
				 "SC:"+self.symbol2[:-3]:self.data.symbol_percentage_since_close[self.symbol2],
				 "SO:"+self.symbol1[:-3]:self.data.symbol_percentage_since_open[self.symbol1],
				 "SO:"+self.symbol2[:-3]:self.data.symbol_percentage_since_open[self.symbol2],
				 "Price Ratio":self.ratio,
				 "Avg. 5m Cor":"",
				 "Avg. 15m Cor":"",
				 "Avg. Linearity":""
				 }

		#str(type(info[j]))=="<class 'tkinter.StringVar'>":
		self.info = []

		for key in labels: #Rows
			self.b = tk.Label(self.chart, text=key,width=12)#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.col, column=0)

			if str(type(labels[key]))=="<class 'tkinter.StringVar'>" or str(type(labels[key]))=="<class 'tkinter.DoubleVar'>":
				self.b = tk.Label(self.chart, textvariable=labels[key],width=10)#,command=self.rank
				
			else:
				self.b = tk.Label(self.chart, text=labels[key],width=10)#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.col, column=1)

			self.col +=1

	def create_graphs(self):

		if self.exsit:
			plt.clf()
		symbol1	= self.symbol1
		symbol2 = self.symbol2

		self.outlier = dict(linewidth=3, color='darkgoldenrod',marker='o')
		plt.style.use("seaborn-darkgrid")

		self.f = plt.figure(1,figsize=(10,9))

		self.min_form = DateFormatter("%H:%M")

		self.gs = self.f.add_gridspec(4, 4)

		# spread_data,spread_time,current_spread = self.get_current_data()
		# m_dis,w_dis,roc1l,roc5l,roc15l = self.get_hist_data()

		spread_time = pd.to_datetime(self.minutes,format='%H:%M')

		self.spread_ = self.f.add_subplot(self.gs[0,:-1])
		self.spread_.tick_params(axis='both', which='major', labelsize=8)
		self.spread_line,=self.spread_.plot(spread_time,self.spreads)

		self.spread_.xaxis.set_major_formatter(self.min_form)
		self.spread_.yaxis.set_major_formatter(mtick.PercentFormatter())
		self.spread_.set_title('IntraDay Spread')

		self.max_spread_d = self.f.add_subplot(self.gs[1,0])
		self.max_spread_d.set_title('Spread Today')
		self.max_spread_d.boxplot(self.spreads, flierprops=self.outlier,vert=False, whis=1)
		self.cur_spread1 = self.max_spread_d.axvline(x=self.current_spread,color="r")

		self.max_spread_w = self.f.add_subplot(self.gs[1,1])
		self.max_spread_w.set_title('Spread Weekly')
		self.max_spread_w.boxplot(self.w_dis, flierprops=self.outlier,vert=False, whis=1)
		self.cur_spread2 = self.max_spread_w.axvline(x=self.current_spread,color="r")

		self.w_dis_min = min(self.w_dis)
		self.w_dis_max = max(self.w_dis)

		self.max_spread_m = self.f.add_subplot(self.gs[1,2])
		self.max_spread_m.set_title('Spread Monthly')
		self.max_spread_m.boxplot(self.m_dis, flierprops=self.outlier,vert=False, whis=1)
		self.cur_spread3 = self.max_spread_m.axvline(x=self.current_spread,color="r")

		self.m_dis_min = min(self.m_dis)
		self.m_dis_max = max(self.m_dis)

		self.roc1_box = self.f.add_subplot(self.gs[2,0])
		self.roc1_box.set_title('Change 1 min')
		self.roc1_box.boxplot(self.roc1l, flierprops=self.outlier,vert=False, whis=2.5)
		self.roc1_ = self.roc1_box.axvline(x=self.roc1,color="r")

		self.roc1l_min = min(self.roc1l)
		self.roc1l_max = max(self.roc1l)

		self.roc5_box = self.f.add_subplot(self.gs[2,1])
		self.roc5_box.set_title('Change 5 min')
		self.roc5_box.boxplot(self.roc5l, flierprops=self.outlier,vert=False, whis=1.5)
		self.roc5_ = self.roc5_box.axvline(x=self.roc5,color="r")

		self.roc5l_min = min(self.roc5l)
		self.roc5l_max = max(self.roc5l)

		self.roc15_box =self.f.add_subplot(self.gs[2,2])
		self.roc15_box.set_title('Change 15 min')
		self.roc15_box.boxplot(self.roc15l, flierprops=self.outlier,vert=False, whis=1.5)
		self.roc15_ = self.roc15_box.axvline(x=self.roc15,color="r")

		self.roc15l_min = min(self.roc15l)
		self.roc15l_max = max(self.roc15l)


		#self.set_graphical_components([[cur_spread1,cur_spread2,cur_spread3],[spread_line,roc1_,roc5_,roc15_]]) 
	
		plt.tight_layout()

		plotcanvas = FigureCanvasTkAgg(self.f, self.graph)
		plotcanvas.get_tk_widget().grid(column=1, row=1)

		if self.data!=None:

			m=self.data.symbol_price[symbol1].trace('w', self.spread_update)
			self.trace.append(m)

			m=self.data.symbol_price[symbol2].trace('w', self.spread_update)
			self.trace.append(m)


	def get_hist_data(self):

		return self.m_dis,self.w_dis,self.roc1l,self.roc5l,self.roc15l

	def get_current_data(self):

		return 	self.spreads,self.minutes,self.current_spread


	def fetch_missing_data(self):

		ts = []
		ps = []
		s=[self.symbol1[:-3],self.symbol2[:-3]]

		for i in s:
			times,price = SVF.fetch_data_yahoo(i)
			ts.append(times[:-2])
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

		# #Spread.
		# print("open",ps[0][0])
		# print("open",ps[1][0])
		c1 = (np.array(ps[0])-ps[0][0])*100/ps[0][0]
		c2 = (np.array(ps[1])-ps[1][0])*100/ps[1][0]

		intra_spread = list(c1 - c2)

		# self.intra_spread_MA5 = list(chiao.SMA(self.intra_spread, 5))
		# self.intra_spread_MA15 = list(chiao.SMA(self.intra_spread, 15))

		cur_minute_list = ts[0][:]

		self.spreads = intra_spread
		self.minutes = cur_minute_list
		print(cur_minute_list[-1])
		self.current_minute = timestamp(cur_minute_list[-1])
		self.current_spread = intra_spread[-1]

		if len(intra_spread)>0: 

			self.roc1 = self.current_spread - self.spreads[-1]      
			len_ = min(5, len(self.spreads)-1)

			#print(len_,self.intra_spread[-len_],self.spread)
			self.roc5 = self.current_spread- self.spreads[-len_] 

			len_ = min(15, len(self.spreads)-1)
			#print(len_,self.intra_spread[-len_],self.spread)
			self.roc15 = self.current_spread-self.spreads[-len_] 

		#Time 


	#when either of the price is updated. this is called. 
	def spread_update(self,a,b,c):

		#print(a,b,c)
		if self.lock == False:

			self.lock = True

			#update the data.

			now = datetime.now()
			ts = now.hour*60 + now.minute

			#ts = self.current_minute+1

			if ts>=570:
			
				self.current_spread = float(self.data.symbol_percentage_since_open[self.symbol1].get()) - float(self.data.symbol_percentage_since_open[self.symbol2].get())

				if self.current_spread !=0:
					if len(self.spreads)>0: 

						self.roc1 = self.current_spread - self.spreads[-1]      
						len_ = min(5, len(self.spreads)-1)

						#print(len_,self.intra_spread[-len_],self.spread)
						self.roc5 = self.current_spread- self.spreads[-len_] 

						len_ = min(15, len(self.spreads)-1)
						#print(len_,self.intra_spread[-len_],self.spread)
						self.roc15 = self.current_spread-self.spreads[-len_] 


					if ts>self.current_minute:
						self.spreads.append(self.current_spread)
						self.minutes.append(ts_to_str(ts))
						self.current_minute = ts

						print("spread-update",ts,self.spreads[-5:],len(self.minutes),len(self.spreads),self.current_spread,self.roc1,self.roc5,self.roc15)

					self.update_graph()
			self.lock = False

	def update_graph(self):
		
		spread_time = pd.to_datetime(self.minutes,format='%H:%M')

		self.spread_line.set_data(spread_time,self.spreads)

		#can i set a bit ahead of time?
		self.spread_.set_xlim(spread_time[0], spread_time[-1])
		self.spread_.set_ylim(min(self.spreads)-0.1,max(self.spreads)+0.1)

		#self.max_spread_d
		self.max_spread_d.cla()
		self.max_spread_d.boxplot(self.spreads, flierprops=self.outlier,vert=False, whis=1)
        
		#print(spread_time[:-5])
		#self.spread_.tick_params(axis='both', which='major', labelsize=8)
		#self.spread_.xaxis.set_major_formatter(self.min_form)

		self.cur_spread1.set_data(self.current_spread,[0,1])
		self.cur_spread2.set_data(self.current_spread,[0,1])
		self.cur_spread3.set_data(self.current_spread,[0,1])
		self.roc1_.set_data(self.roc1,[0,1])
		self.roc5_.set_data(self.roc5,[0,1])
		self.roc15_.set_data(self.roc15,[0,1])


		# self.max_spread_d.set_xlim(min(self.spreads)-0.1,max(self.spreads)+0.1)
		# self.max_spread_w.set_xlim(min(self.current_spread,self.w_dis_min)-0.1,max(self.current_spread,self.w_dis_min)+0.1)
		# self.max_spread_m.set_xlim(min(self.current_spread,self.m_dis_min)-0.1,max(self.current_spread,self.m_dis_min)+0.1)

		#self.max_spread_d.set_xlim(min(self.spreads)-0.1,max(self.spreads)+0.1)
		self.max_spread_w.set_xlim(min(self.w_dis)-0.5,max(self.w_dis)+0.5)
		self.max_spread_m.set_xlim(min(self.m_dis)-0.5,max(self.w_dis)+0.5)


		self.roc1_box.set_xlim(min(self.roc1,self.roc1l_min)-0.1,max(self.roc1,self.roc1l_max)+0.1)
		self.roc5_box.set_xlim(min(self.roc5,self.roc5l_min)-0.1,max(self.roc5,self.roc5l_max)+0.1)
		self.roc15_box.set_xlim(min(self.roc15,self.roc15l_min)-0.1,max(self.roc15,self.roc15l_max)+0.1)


		self.f.canvas.draw()



