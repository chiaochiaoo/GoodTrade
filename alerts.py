import tkinter as tk                     
from tkinter import ttk 
from pannel import *
from Symbol_data_manager import *

class all_alerts(pannel):
	def __init__(self,frame):
		super().__init__(frame)

		self.labels = ["Ticker","Time","Alert","Dismiss"]
		self.width = [8,10,24,10]
		self.labels_creator(self.frame)

		self.alert_base = []

	

	#if the type and the time match, then don't add. 

	def dismiss_alerts(self,key):

		for i in self.tickers_labels[key]:
			i.destroy()

		self.rebind(self.canvas,self.frame)

	#vals = symbol,time ,alert type
	def add_alerts(self,vals):

		l = self.label_count 

		symbol = vals[0]
		
		if set(vals) not in self.alert_base:

			key = str(vals)
			self.tickers_labels[key] = []
			for i in range(len(vals)):
				
				self.tickers_labels[key].append(tk.Label(self.frame ,text=vals[i],width=self.width[i]))
				self.label_default_configure(self.tickers_labels[key][i])
				self.tickers_labels[key][i].grid(row= l+2, column=i,padx=0)

			i+=1
			self.tickers_labels[key].append(tk.Button(self.frame ,width=self.width[i],command = lambda k=key: self.dismiss_alerts(k)))
			self.label_default_configure(self.tickers_labels[key][i])
			self.tickers_labels[key][i].grid(row= l+2, column=i,padx=0)


			self.label_count +=1
			self.alert_base.append(set(vals))
			self.rebind(self.canvas,self.frame)

class alert(pannel):

	def __init__(self,frame,data:Symbol_data_manager,alert_pannel:all_alerts):

		super().__init__(frame)

		self.alert_pannel=alert_pannel
		self.data = data

		#init the labels. 

	#any alert will need a threshold. deviation. std. 
	def add_symbol(self,symbol,format,val_position,alert_position,alert_vals,data_ready):

		l = self.label_count

		self.tickers_labels[symbol] = []
		i = symbol

		for j in range(len(format)):

			if j==0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			elif j==1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))

			#when it is alert label creation, create a trace set for value position 
			elif j == alert_position:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[val_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals,ready=data_ready,status=format[1]: self.alert(eval_string,label,alertsvals,ready,status))

			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
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



	def set_latest_alert(self,symbol,alert,time):

		self.data.symbol_last_alert[symbol].set(alert)
		self.data.symbol_last_alert_time[symbol].set(time)

	#alert vals: cur, mean, std.
	def alert(self,eval_string,eval_label,alerts_vals,ready,status):

		#check how many std it is. `

		#attention, only do the calculation when the database is set. 

		if ready.get() == True and status.get() =="Connected":

			symbol= alerts_vals[0]
			time= alerts_vals[1].get()[:5]
			
			cur_price= round(alerts_vals[2].get(),3)
			mean= round(alerts_vals[3].get(),3)
			std=  round(alerts_vals[4].get(),3)
			alert_type = alerts_vals[5]

			cur = round((cur_price-mean)/std,3)

			eval_string.set(str(cur)+" from mean")

			#color. 

			if cur <0.5:
				eval_label["background"]="white"

			elif cur>0.5 and cur<1:
				alert_type = "Moderate "+alert_type
				eval_label["background"]="#97FEA8"
				self.alert_pannel.add_alerts([symbol,time,alert_type])
				self.set_latest_alert(symbol, alert_type, time)

			elif cur>1 and cur<2:
				alert_type = "High "+alert_type
				eval_label["background"]="yellow"
				self.alert_pannel.add_alerts([symbol,time,alert_type])
				self.set_latest_alert(symbol, alert_type, time)
			else:
				### Send the alert to alert pannel.
				alert_type = "Very high "+alert_type
				eval_label["background"]="red"

				self.alert_pannel.add_alerts([symbol,time,alert_type])
				self.set_latest_alert(symbol, alert_type, time)



class highlow(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","Cur High","Cur Low","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_range[symbol]
		cur_high = self.data.symbol_price_high[symbol]
		cur_low = self.data.symbol_price_low[symbol]
		hist_avg= self.data.symbol_data_range_val[symbol]
		hist_std = self.data.symbol_data_range_std[symbol]
		hist_range= self.data.symbol_data_range_range[symbol]
		eva= self.data.symbol_data_range_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Range"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		labels = [symbol,status,cur_range,cur_high,cur_low,hist_avg,hist_std,hist_range,eva]


		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol, labels,value_position,alert_position,alertvals,data_ready)

	#find a way to bound the special checking value to. hmm. every update.



class openhigh(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","Cur Open","Cur High","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_openhigh[symbol]
		cur_open = self.data.symbol_price_open[symbol]
		cur_high = self.data.symbol_price_high[symbol]
		hist_avg= self.data.symbol_data_openhigh_val[symbol]
		hist_std = self.data.symbol_data_openhigh_std[symbol]
		hist_range= self.data.symbol_data_openhigh_range[symbol]

		eva= self.data.symbol_data_openhigh_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Open-High"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		labels = [symbol,status,cur_range,cur_open,cur_high,hist_avg,hist_std,hist_range,eva]


		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol, labels,value_position,alert_position,alertvals,data_ready)

	#find a way to bound the special checking value to. hmm. every update.

class openlow(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","Cur Open","Cur Low","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_openlow[symbol]
		cur_open = self.data.symbol_price_open[symbol]
		cur_low = self.data.symbol_price_low[symbol]
		hist_avg= self.data.symbol_data_openlow_val[symbol]
		hist_std = self.data.symbol_data_openlow_std[symbol]
		hist_range= self.data.symbol_data_openlow_range[symbol]

		eva= self.data.symbol_data_openlow_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Open-Low"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		labels = [symbol,status,cur_range,cur_open,cur_low,hist_avg,hist_std,hist_range,eva]


		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol, labels,value_position,alert_position,alertvals,data_ready)

	#find a way to bound the special checking value to. hmm. every update.