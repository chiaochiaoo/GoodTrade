import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import database as db
import Spread_viewer_function as SVF

# from modules.pannel import *
# from modules.scanner_process_manager import *

from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter


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
			if self.symbol1.get()!='Unselected' and self.symbol2.get()!='Unselected':
				return True

		return False

	def create_new_tab(self):


		if self.validation():
			pair_name = self.symbol1.get()[:-3]+self.symbol2.get()[:-3]
			self.tabs[pair_name] = tk.Canvas(self.spread_lists)


			# self.graph = ttk.LabelFrame(self.tabs[pair_name])
			# self.graph.place(relx=0,y=0,relheight=1,relwidth=0.8)

			self.spread_lists.add(self.tabs[pair_name], text =pair_name) 

			symbols = [self.symbol1.get()[:-3],self.symbol2.get()[:-3]]

			#m_dis,w_dis,roc1l,roc5l,roc15l = SVF.find_info(symbols)
			m_dis,w_dis,roc1l,roc5l,roc15l = [-0.3283, 0.1917, -0.03409999999999999, 0.2657, -0.44719999999999993, 0.016600000000000004, -0.1381, 0.4857, -0.3571, 0.1051, -0.0897, 0.3362, -0.28890000000000005, 0.2429, -0.1852, 0.45520000000000005, -0.4226, 0.1296, 0.0, 0.5786000000000001, -0.06529999999999997, 1.3074, -0.8129, 0.8934, -0.21950000000000003, 0.6422, -0.43320000000000003, 0.7110000000000003, -0.7948999999999999, 0.16170000000000007, -0.32610000000000006, 0.5431, 0.0, 1.0438, -0.1055, 1.6807, -0.4252, 0.613, -0.03240000000000001, 0.9425999999999999, -0.1331, 1.9503, -1.1836000000000002, 0.1335, 0.0, 1.7571999999999999, -0.5464, 0.2148, -0.12070000000000003, 0.6159, -0.43250000000000005, 0.2964, -0.8592, 0.10639999999999994, -1.1096, 0.3685, -0.05609999999999998, 0.7834000000000001, -0.6295999999999999, 0.031399999999999983, -0.3638, 0.0] , [-0.8592, 0.10639999999999994, -1.1096, 0.3685, -0.05609999999999998, 0.7834000000000001, -0.6295999999999999, 0.031399999999999983, -0.3638, 0.0] , [-0.00739999999999999, 0.0272, -0.014300000000000007, 0.0296, -0.0898, -0.004399999999999987, -0.0913, 0.0012999999999999678, -0.1, 0.00940000000000002, 0.008099999999999996, 0.0489, -0.03889999999999999, -0.021199999999999997, -0.0511, 0.006000000000000061, -0.020900000000000085, -0.0073, 9.99999999999994e-05, 0.019400000000000084, -0.0257, 0.008300000000000196, -0.002000000000000113, 0.05840000000000001, -0.09010000000000001, 0.0015000000000000568, -0.024099999999999996, 0.010000000000000009, -0.14200000000000002, -0.0030000000000000027, -0.0015000000000000568, 0.0596, -0.0016000000000000458, 0.09620000000000001, -0.1055, 0.041799999999999615, -0.08220000000000001, -0.04960000000000031, -0.02089999999999992, 0.0539, -0.014900000000000357, 0.07179999999999999, -0.026599999999999957, 0.0761, -0.006599999999999939, 0.2135, -0.0271, 0.017699999999999938, -0.0024000000000000687, 0.04580000000000001, 0.009000000000000008, 0.1242, 0.002799999999999997, 0.04730000000000001, -0.005199999999999871, 0.005099999999999993, -0.0532, 0.012800000000000034, -0.2212, -0.0045000000000000595, -0.1038, 0.035099999999999965] , [-0.02092000000000005, 0.04571999999999999, -0.04068000000000002, 0.08468, -0.09576, 0.03398000000000001, -0.03796, -0.01620000000000002, -0.06917999999999999, -0.014119999999999994, -0.022679999999999985, 0.19075999999999999, -0.07502, -0.009639999999999982, -0.048299999999999996, 0.028319999999999984, -0.02017999999999992, -0.014080000000000004, -0.02059999999999995, 0.05294000000000001, -0.021320000000000006, 0.037180000000000005, 0.0033799999999999386, 0.055459999999999995, -0.043139999999999956, 0.031420000000000003, -0.15892, 0.07494, -0.18136000000000002, 0.10619999999999996, -0.07955999999999996, 0.2137, 0.016019999999999923, 0.1336, -0.02057999999999982, -0.00882, -0.19449999999999998, 0.011359999999999981, -0.07876, 0.10613999999999998, 0.00869999999999993, 0.21112000000000003, -0.02532000000000001, -0.02031999999999999, 0.05433999999999983, 0.2427, -0.13926000000000002, 0.012019999999999975, 0.005440000000000035, 0.13302, -0.04580000000000001, 0.18209999999999998, -0.07882, 0.039240000000000025, 0.05134000000000016, 0.053180000000000005, -0.009279999999999993, 0.03145999999999993, -0.33676, -0.12385999999999991, -0.26846000000000003, 0.10044] , [-0.04716666666666669, 0.06445999999999999, -0.016226666666666667, 0.11773333333333334, -0.15864666666666666, 0.012706666666666658, 0.0013733333333333347, 0.026119999999999977, -0.024359999999999993, -0.019439999999999985, -0.04477333333333332, 0.2074, -0.06629333333333333, -0.011406666666666676, -0.09998666666666667, -0.001700000000000021, -0.044346666666666666, 0.024939999999999962, -0.030446666666666677, 0.07416, 0.013339999999999907, 0.07841999999999999, 0.030286666666666795, 0.3384599999999999, -0.04272666666666665, 0.14918, -0.28885333333333335, -0.08113333333333339, -0.32965999999999995, -0.07663333333333355, -0.10555333333333335, 0.33194666666666667, 0.08398666666666665, 0.26236, -0.04730000000000012, 0.1622, -0.17043333333333333, 0.02851999999999988, 0.07852666666666666, 0.21306, 0.059713333333333285, 0.1820133333333333, -0.08106666666666665, 0.06538, 0.023859999999999992, 0.4173133333333333, -0.16266666666666663, 0.03617333333333339, -0.012700000000000019, 0.24782, -0.028179999999999983, 0.20362, -0.10882, 0.01960666666666669, 0.14556000000000002, 0.1653933333333333, 0.0633600000000003, 0.07370666666666667, -0.2990133333333333, -0.16222666666666657, -0.23909333333333335, 0.0024733333333333274]			#

			#successful 
			print(m_dis,",",w_dis,",",roc1l,",",roc5l,",",roc15l)

			outlier = dict(linewidth=3, color='darkgoldenrod',marker='o')
			plt.style.use("seaborn-darkgrid")
			f = plt.figure(1,figsize=(10,8))
			f.canvas.set_window_title('SPREAD MONITOR')
			min_form = DateFormatter("%H:%M")
			sec_form = DateFormatter("%M:%S")
			gs = f.add_gridspec(4, 4)

			spread = f.add_subplot(gs[0,:-1])
			spread.tick_params(axis='both', which='major', labelsize=8)
			spread.set_title('IntraDay Spread')

			# m1 = f.add_subplot(gs[3,:])
			# m1.tick_params(axis='both', which='major', labelsize=8)
			# m1.set_title('1 min Spread')

			max_spread_d = f.add_subplot(gs[1,0])
			max_spread_d.set_title('Spread Today')
			max_spread_d.boxplot([], flierprops=outlier,vert=False, whis=1)

			max_spread_w = f.add_subplot(gs[1,1])
			max_spread_w.set_title('Spread Weekly')
			max_spread_w.boxplot(w_dis, flierprops=outlier,vert=False, whis=1)

			max_spread_m = f.add_subplot(gs[1,2])
			max_spread_m.set_title('Spread Monthly')
			max_spread_m.boxplot(m_dis, flierprops=outlier,vert=False, whis=1)


			roc1 = f.add_subplot(gs[2,0])
			roc1.set_title('Change 1 min')
			roc1.boxplot(roc1l, flierprops=outlier,vert=False, whis=2.5)

			roc5 = f.add_subplot(gs[2,1])
			roc5.set_title('Change 5 min')
			roc5.boxplot(roc5l, flierprops=outlier,vert=False, whis=1.5)

			roc15 =f.add_subplot(gs[2,2])
			roc15.set_title('Change 15 min')
			roc15.boxplot(roc15l, flierprops=outlier,vert=False, whis=1.5)

			plt.tight_layout()
			plotcanvas = FigureCanvasTkAgg(f, self.tabs[pair_name])
			plotcanvas.get_tk_widget().grid(column=1, row=1)

			# self.tab1 = tk.Canvas(self.tabControl)
			# self.tab2 = tk.Canvas(self.tabControl)

			# 


class spread:

	def __init__(self,symbol1,symbol2,data):

		self.data = data

		self.symbol1= symbol1
		self.symbol2= symbol2 

		#necessary data.

		#1. missing data if it is after 9:30

		#2. hisotircal data.

		#3. listen to price update. 

		#output data

		#m_dis,w_dis,roc1l,roc5l,roc15l

		self.current_spread = 0

		self.roc_list = []

		self.roc1 = 0
		self.roc5 = 0
		self.roc15 = 0


# root = tk.Tk() 
# root.title("GoodTrade PairTrader") 


# s = spread_trader(root,None,None)
# root.geometry("700x800")
# root.minsize(1000, 800)
# root.maxsize(1800, 1200)
# root.mainloop()

import numpy as np

ts = []
ps = []
s=["QQQ","SPY"]

for i in s:
    timestamp,price = SVF.fetch_data_yahoo(i)
    ts.append(timestamp[:-2])
    ps.append(price[:-2])

print(ts,ps)


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
print(intra_spread)
print(cur_minute_list)
