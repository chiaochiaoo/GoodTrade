import tkinter as tk                     
from tkinter import ttk 
from pannel import *
from Symbol_data_manager import *

class alert(pannel):

	def __init__(self,frame,data:Symbol_data_manager):

		super()

		self.label_count = 0
		self.tickers_labels = {}

		self.data = data

		self.frame_ = ttk.LabelFrame(frame) 
		self.frame_.place(x=0, y=40, relheight=0.85, relwidth=1)

		self.canvas = tk.Canvas(self.frame_)
		self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.frame_)
		self.scroll.config(orient=tk.VERTICAL, command=self.canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")

		self.canvas.configure(yscrollcommand=self.scroll.set)

		self.frame = tk.Frame(self.canvas)
		self.frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.canvas.create_window(0, 0, window=self.frame, anchor=tk.NW)

		#init the labels. 

	#any alert will need a threshold. deviation. std. 
	def add_symbol(self,symbol,format,width,val_position,alert_position,alert_vals):

		l = self.label_count

		self.tickers_labels[symbol] = []
		i = symbol

		for j in range(len(format)):

			if j==0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=format[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			elif j==1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))

			#when it is alert label creation, create a trace set for value position 
			elif j == alert_position:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[val_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals: self.alert(eval_string,label,alertsvals))

			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

	def delete_symbol(self,symbol):

		for i in self.tickers_labels[symbol]:
			i.destroy()

		self.tickers_labels.pop(symbol,None)

		self.rebind(self.canvas,self.frame)


	#alert vals: cur, mean, std.
	def alert(self,eval_string,eval_label,alerts_vals):

		#check how many std it is. 

		cur = round((alerts_vals[0]-alerts_vals[1])/alerts_vals[2],3)

		eval_string.set(str(cur)+" from mean")


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
		eva= self.data.symbol_[symbol]

		value_position = 2
		alert_position = 7
		#cur, mean, std. 
		alertvals= [cur_range,hist_avg,hist_std]
		labels = [symbol,status,cur_range,cur_high,cur_low,hist_avg,hist_std,hist_range,eva,value_position,alert_position,alertvals]

		#any alert will need a threshold. deviation. std. 
		super().add_symbol(symbol, labels, self.width)

	#find a way to bound the special checking value to. hmm. every update.