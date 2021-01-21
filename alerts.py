import tkinter as tk                     
from tkinter import ttk 
from pannel import *
from Symbol_data_manager import *


def to_number(str):

	try:
		x = round(float(str),2)
		return x 

	except Exception as e:
		print("to_num",e)
		return 0.00


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

		self.rebind(self.canvas,self.frame)

class alert(pannel):

	def __init__(self,frame,data:Symbol_data_manager,alert_pannel:all_alerts):

		super().__init__(frame)

		self.alert_pannel=alert_pannel
		self.data = data

		self.alerts = {}


		self.breakout_time = {}

		#init the labels. 

	#any alert will need a threshold. deviation. std. 
	def add_symbol(self,symbol,format,alert_positions,alerts,data_ready):

		#init the alert value
		if symbol not in self.alerts:
				self.alerts[symbol] = {}

		for i in alert_positions:
			self.alerts[symbol][alerts[i][2][5]] = 0

		l = self.label_count

		self.tickers_labels[symbol] = []
		self.tickers_tracers[symbol] = []
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
				m=format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
				self.tickers_tracers[i].append((format[j],m))

			#when it is alert label creation, create a trace set for value position 
			elif j in alert_positions:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				#unpack value_position,alert_position,alertvals
				value_position = alerts[j][0]
				alert_position = alerts[j][1]
				alert_vals = alerts[j][2]
				m=format[value_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals,ready=data_ready,status=format[1]: self.alert(eval_string,label,alertsvals,ready,status))
				self.tickers_tracers[i].append((format[value_position],m))
			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

	def add_symbol_breakout(self,symbol,format,alert_positions,alerts,data_ready):

		try:
			#init the alert value
			if symbol not in self.alerts:
					self.alerts[symbol] = {}
					self.breakout_time[symbol] = 0


		except Exception as e:
			print("add problem")

		for i in alert_positions:
			self.alerts[symbol][alerts[i][2][5]] = 0

		l = self.label_count

		self.tickers_labels[symbol] = []
		#self.tickers_tracers[symbol] = []
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
				m=format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
				self.tickers_tracers[i].append((format[j],m))

			elif j ==2 or j ==3:
				self.tickers_labels[i].append(tk.Checkbutton(self.frame,variable=format[j]))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				#self.tickers_labels[i][j].configure(text='Auto range detection')
			#text filed for hmm,,,entry, 
			elif j ==4 or j ==5:
				self.tickers_labels[i].append(tk.Entry(self.frame ,textvariable=format[j],width=self.width[j]))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			#when it is alert label creation, create a trace set for value position 
			elif j in alert_positions:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				#unpack value_position,alert_position,alertvals
				value_position = alerts[j][0]
				alert_position = alerts[j][1]
				alert_vals = alerts[j][2]
				m=format[value_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals,ready=data_ready,status=format[1]: self.alert(eval_string,label,alertsvals,ready,status))
				self.tickers_tracers[i].append((format[value_position],m))
			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

	def delete_symbol(self,symbol):
		for i in self.tickers_tracers[symbol]:
			i[0].trace_vdelete("w",i[1])


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

		try:

			if ready.get() == True and status.get() =="Connected":

				symbol= alerts_vals[0]
				time= alerts_vals[1].get()
				alert_type = alerts_vals[5]

				minute= time[:5]
				second = time[:8]
				ts = timestamp(time)
				seconds = timestamp_seconds(second)

				auto_trade = self.data.auto_trade

				#print(time,ts)


				#print(alert_type)
				if alert_type=="breakout":


					### ASSUME NUMBER ONLY.
					cur_price= round(alerts_vals[2].get(),3)
					support= to_number(alerts_vals[3].get())
					resistance =  to_number(alerts_vals[4].get())

					#print("breakout check:",cur_price,support,resistance)

					if support != 0.00 and resistance != 0.00 and ts>565:
						#print(support,resistance,cur_price)

						if cur_price<support and cur_price<resistance and self.alerts[symbol][alert_type]!=2:

							self.alerts[symbol][alert_type] = 2

							if self.breakout_time[symbol] == 0:
								self.breakout_time[symbol] = seconds

							been = seconds - self.breakout_time[symbol]

							print(seconds,self.breakout_time[symbol],been)

							alert_str = "Support "+alert_type +" :"+str(been)+" sec ago"

							eval_string.set(alert_str)

							self.alert_pannel.add_alerts([symbol,time,alert_str])
							self.set_latest_alert(symbol, alert_str, time)



						elif cur_price>resistance and cur_price>support and self.alerts[symbol][alert_type]!=1 :

							self.alerts[symbol][alert_type] = 1
							#check time. 
							if self.breakout_time[symbol] == 0:
								self.breakout_time[symbol] = seconds

							been = seconds - self.breakout_time[symbol]

							if been<60:
								alert_str = "Resistance "+alert_type +" :"+str(been)+" sec ago"
							else:
								alert_str = "Resistance "+alert_type +" :"+str(been//60)+" min ago"


							eval_string.set(alert_str)

							self.alert_pannel.add_alerts([symbol,time,alert_str])
							self.set_latest_alert(symbol, alert_str, time)



						elif cur_price<resistance and cur_price>support and self.alerts[symbol][alert_type]!=0 :

							#refresh it back.
							self.breakout_time[symbol] = 0

							self.alerts[symbol][alert_type] = 0

							#normal white color
							eval_label["background"]="#d9d9d9"
							eval_string.set("")

						#only update the time
						else:
							#print("ts:",seconds,self.breakout_time[symbol])
							been = seconds - self.breakout_time[symbol]

							if self.alerts[symbol][alert_type]==2:
								if been<60:
									alert_str = "Support "+alert_type +" :"+str(been)+" sec ago"
								else:
									alert_str = "Support "+alert_type +" :"+str(been//60)+" min ago"
								eval_string.set(alert_str)
							if self.alerts[symbol][alert_type]==1:

								if been<60:
									alert_str = "Resistance "+alert_type +" :"+str(been)+" sec ago"
								else:
									alert_str = "Resistance "+alert_type +" :"+str(been//60)+" min ago"	

								eval_string.set(alert_str)

							if self.alerts[symbol][alert_type]!=0:
								if been>60 and been<180:
									#green
									eval_label["background"]="#67FF37"
								if been>180 and been <300:
									eval_label["background"]="yellow"

								if been >180 and been <190:
									if auto_trade[symbol].get()==1 and self.alerts[symbol][alert_type]==1:
										self.data.ppro.long(symbol)
									if auto_trade[symbol].get()==1 and self.alerts[symbol][alert_type]==2:
										self.data.ppro.short(symbol)

								if been>300 and been <600:
									eval_label["background"]="#FF5B5B"
								if been>600:
									eval_label["background"]="red"



				else:

					cur_price= round(alerts_vals[2].get(),3)
					mean= round(alerts_vals[3].get(),3)
					std=  round(alerts_vals[4].get(),3)

					#on certain alert_type, the math can be different. 


					if std != 0:
						cur = round((cur_price-mean)/std,3)
						eval_string.set(str(cur)+" from mean")
					else:
						cur = 0
						eval_string.set("Unable to process std 0")

					#color.
					#cur = abs(cur)

					if cur <0.5:
						eval_label["background"]="white"

					elif cur>0.5 and cur<1:
						
						alert_str = "Moderate "+alert_type
						eval_label["background"]="#97FEA8"

						if ts>570 and self.alerts[symbol][alert_type] < 0.5:
							self.alerts[symbol][alert_type] = 0.5
							self.alert_pannel.add_alerts([symbol,time,alert_str])
							self.set_latest_alert(symbol, alert_str, time)

					elif cur>1 and cur<2 and self.alerts[symbol][alert_type] < 1:
						self.alerts[symbol][alert_type] = 1
						alert_str = "High "+alert_type
						eval_label["background"]="yellow"
						if ts>570:
							#only set when there is higher severity. 
							self.alert_pannel.add_alerts([symbol,time,alert_str])
							self.set_latest_alert(symbol, alert_str, time)
					elif cur>2 and self.alerts[symbol][alert_type] < 2:

						self.alerts[symbol][alert_type] = 2
						### Send the alert to alert pannel.
						alert_str = "Very high "+alert_type
						eval_label["background"]="red"
						if ts>570:
							self.alert_pannel.add_alerts([symbol,time,alert_str])
							self.set_latest_alert(symbol, alert_str, time)

		except Exception as e:
			print("Alert Error:",e)



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


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

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


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

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

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.

#########################
class open_now(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Open","Cur Price","Cur Range","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_opennow[symbol]
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

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.

class prevclose(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Prev Close","Cur Range","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,15,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_prevclose_to_now[symbol]
		prev_close = self.data.symbol_price_prevclose[symbol]

		hist_avg= self.data.symbol_data_prev_close_val[symbol]
		hist_std = self.data.symbol_data_prev_close_std[symbol]
		hist_range= self.data.symbol_data_prev_close_range[symbol]

		eva= self.data.symbol_data_prev_close_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 7
		alert_type = "Change Since Prev Close"

		#cur, mean, std. symbol, time.
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		labels = [symbol,status,prev_close,cur_range,hist_avg,hist_std,hist_range,eva]


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std.

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class firstfive(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","H. Avg","H. Std","H. Range","Cur Vol","H.Vol Avg","H.Vol Std","H.Vol Range","Evaluation:Range","Evaluation:Volume"]
		self.width = [8,10,7,7,7,7,7,7,7,12,14,15,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?
		cur_range =self.data.first_5_min_range[symbol]
		cur_vol = self.data.first_5_min_volume[symbol]

		hist_avg= self.data.symbol_data_first5_val[symbol]
		hist_std = self.data.symbol_data_first5_std[symbol]
		hist_range= self.data.symbol_data_first5_range[symbol]

		hist_v_avg= self.data.symbol_data_first5_vol_val[symbol]
		hist_v_std = self.data.symbol_data_first5_vol_std[symbol]
		hist_v_range= self.data.symbol_data_first5_vol_range[symbol]

		eva= self.data.symbol_data_first5_range_eval[symbol]

		eva2 = self.data.symbol_data_first5_vol_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]


		labels = [symbol,status,cur_range,hist_avg,hist_std,hist_range,cur_vol,hist_v_avg,hist_v_std,hist_v_range,eva,eva2]

		value_position = 2
		alert_position = 10
		alert_type = "Opening Rg"
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		#cur, mean, std. symbol, time. 
		

		value_position2 = 6
		alert_position2 = 11

		alert_type2 = "Opening Vol"
		alertvals2= [symbol,time,cur_vol,hist_v_avg,hist_v_std,alert_type2]


		alert_positions = [alert_position,alert_position2]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		alerts[alert_position2] = [value_position2,alert_position2,alertvals2]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class extremrange(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,15,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?
		cur_range =self.data.last_5_min_range[symbol]

		hist_avg= self.data.symbol_data_normal5_val[symbol]
		hist_std = self.data.symbol_data_normal5_std[symbol]
		hist_range= self.data.symbol_data_normal5_range[symbol]

		eva= self.data.symbol_data_normal5_range_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 6
		alert_type = "Intraday Range"
		alert_time = 0
		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_time]
		labels = [symbol,status,cur_range,hist_avg,hist_std,hist_range,eva]

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class extremevolume(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Vol(k)","H. Avg(k)","H. Std(k)","H. Range","Evaluation"]
		self.width = [8,10,15,7,7,15,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?

		cur_vol = self.data.last_5_min_volume[symbol]

		hist_avg= self.data.symbol_data_normal5_vol_val[symbol]
		hist_std = self.data.symbol_data_normal5_vol_std[symbol]
		hist_range= self.data.symbol_data_normal5_vol_range[symbol]

		eva= self.data.symbol_data_normal5_vol_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 6
		alert_type = "Intraday Open-Low"

		alert_time = 0

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_vol,hist_avg,hist_std,alert_type,alert_time]
		labels = [symbol,status,cur_vol,hist_avg,hist_std,hist_range,eva]

		#any alert will need a threshold. deviation. std. or type.

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.



class breakout(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","AR","AT","Support","Resistance ","Range","Cur Price","Evaluation"]
		self.width = [8,10,4,4,10,10,10,10,35]
		self.labels_creator(self.frame)


		self.checker = tk.Checkbutton(frame,variable=self.data.all_auto)
		self.checker.place(x=5, y=5, height=30, width=150, bordermode='ignore')
		self.checker.configure(text='Auto range detection')


		self.checker2 = tk.Checkbutton(frame,variable=self.data.all_auto_trade)
		self.checker2.place(x=175, y=5, height=30, width=150, bordermode='ignore')
		self.checker2.configure(text='Auto Trade Breakout')


		self.data.all_auto.trace('w', lambda *_,vals=self.data.auto_support_resistance,val=self.data.all_auto: self.set_auto(vals,val))
		self.data.all_auto_trade.trace('w', lambda *_,vals=self.data.auto_trade,val=self.data.all_auto_trade: self.set_auto(vals,val))


	def set_auto(self,vals,val):

		v = val.get()
		self.data.toggle_all(vals,v)


	def range_tracker(self,support,resistance,rg):
		try:
			num = float(resistance.get())-float(support.get())
			if num>0:
				rg.set(round(num,2))
			else:
				rg.set(0)
			#print("setting rg suc")
		except:
			#print("setting rg failed")
			return None

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?

		cur_price = self.data.symbol_price[symbol]

		checker = self.data.auto_support_resistance[symbol]

		checker_trade = self.data.auto_trade[symbol]

		support = self.data.symbol_data_support[symbol]
		resistance  = self.data.symbol_data_resistance[symbol]

		range_ = self.data.symbol_data_support_resistance_range[symbol]

		self.tickers_tracers[symbol] = []

		m=support.trace('w', lambda *_, support=support,resist=resistance,rg=range_: self.range_tracker(support,resist,rg))
		self.tickers_tracers[symbol].append((support,m))
		n=resistance.trace('w', lambda *_, support=support,resist=resistance,rg=range_: self.range_tracker(support,resist,rg))
		self.tickers_tracers[symbol].append((resistance,n))


		eva= self.data.symbol_data_breakout_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 7
		alert_position = 8
		alert_type = "breakout"

		alert_time = 0


		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_price,support,resistance ,alert_type]
		labels = [symbol,status,checker,checker_trade,support,resistance ,range_,cur_price,eva]

		#any alert will need a threshold. deviation. std. or type.

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol_breakout(symbol,labels,alert_positions,alerts,data_ready)
