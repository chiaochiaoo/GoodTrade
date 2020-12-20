import tkinter as tk                     
from tkinter import ttk 
from pannel import *
from Symbol_data_manager import *

class alert(pannel):

	def __init__(self,frame,data:Symbol_data_manager):

		super()

		#pannel
		self.ticker_index = {}
		self.label_count = 0
		self.ticker_count = 0
		self.tickers_labels = []

		self.data = data

		self.frame_ = ttk.LabelFrame(frame) 
		self.frame_.place(x=0, y=40, relheight=0.85, relwidth=1)

		self.canvas = tk.Canvas(self.frame_)
		self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.frame_)
		self.scroll.config(orient=tk.VERTICAL, command=self.canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")

		self.canvas.configure(yscrollcommand=self.scroll.set)
		#self.scanner_canvas.bind('<Configure>', lambda e: self.scanner_canvas.configure(scrollregion = self.scanner_canvas.bbox('all')))

		self.frame = tk.Frame(self.canvas)
		self.frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.canvas.create_window(0, 0, window=self.frame, anchor=tk.NW)

		#init the labels. 


	#any alert will need a threshold. deviation. std. 

	def add_symbol(self,symbol,format,width):

		self.ticker_index[symbol] = self.ticker_count 
		i = self.ticker_count

		l = self.label_count

		# print("adding position:",symbol,":",i)
		# width = [8,10,12,10,10,12,10,10]
		# info = [symbol,\
		# 		self.data.symbol_status[symbol],\
		# 		self.data.symbol_update_time[symbol],\
		# 		self.data.symbol_price[symbol],\
		# 		self.data.symbol_last_alert[symbol],\
		# 		self.data.symbol_last_alert_time[symbol],
		# 		""]

		self.tickers_labels.append([])

		#add in tickers.
		for j in range(len(format)):

			if j==0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=format[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			if j==1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))

			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)


	def delete_symbol(self,format,symbol):
		return True

class highlow(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

		self.labels = ["Ticker","Status","Cur Range","Cur High","Cur low","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,12]
		self.labels_creator(self.frame)


	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_range[symbol]
		cur_high = self.data.symbol_price_high[symbol]
		cur_low = self.data.symbol_price_low[symbol]
		hist_avg= self.data.symbol_data_range_val[symbol]
		hist_std = self.data.symbol_data_range_std[symbol]
		hist_range= self.data.symbol_data_range_range[symbol]
		eva= ""
		labels = [symbol,status,cur_range,cur_high,cur_low,hist_avg,hist_std,hist_range,eva]

		#any alert will need a threshold. deviation. std. 
		super().add_symbol(symbol, labels, self.width)

	def delete_symbol(self,symbol):
		return True
