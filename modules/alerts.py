import tkinter as tk                     
from tkinter import ttk 
from modules.pannel import *
from modules.Symbol_data_manager import *
from cores.algo_placer import *
import threading


BREAISH =   "  Bearish"
BULLISH =   "  Bullish"
BREAKUP =   " BreakUp"
BREAKDOWN = " BreakDn"
BREAKANY =  "BreakAny"
DIPBUY = "Dipbuy"
RIPSELL = "Ripsell"
FADEANY = "FadeAny"
BREAKFIRST = "BreakFirst"


def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a

def hexcolor(level):
	code = int(510*(level))
	#print(code,"_")
	if code >255:
		first_part = code-255
		return "#FF"+hex_to_string(255-first_part)+"00"
	else:
		return "#FF"+"FF"+hex_to_string(255-code)


def color_bind(val,label):

	val = val.get()

	#get color code.
	if val>3:
		val = 1
	elif val<0:
		val = 0
	else:
		val = val/3

	label["background"] = hexcolor(val)

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

	def __init__(self,frame,data:Symbol_data_manager,commlink=None):

		super().__init__(frame)


		self.reverse = True
		#self.alert_pannel=alert_pannel
		self.data = data

		self.alerts = {}

		self.eval_time = 0

		if commlink:
			self.algo_commlink = commlink

		self.breakout_time = {}


		self.symbol_ranking = {}

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

		self.symbol_ranking[symbol]= l

		#print(self.symbol_ranking)

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
				#m=format[value_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals,ready=data_ready,status=format[1]: self.alert(eval_string,label,alertsvals,ready,status))
				#self.tickers_tracers[i].append((format[value_position],m))
			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

	def add_symbol_breakout(self,symbol,format,alert_positions,alerts,data_ready,default_risk):

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
				#m=format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
				#self.tickers_tracers[i].append((format[j],m))

			elif j ==2 :
				self.tickers_labels[i].append(tk.Checkbutton(self.frame,variable=format[j]))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[j].set(self.auto_range.get())
				#self.tickers_labels[i][j].configure(text='Auto range detection')
			#text filed for hmm,,,entry, 
			elif j ==3 or j ==4:
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
			elif j==9:
				self.tickers_labels[i].append(tk.Checkbutton(self.frame,variable=format[j]))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[j].set(self.auto_trade.get())

			#trigger type
			elif j==10:
				self.trigger_types = {BREAISH,BULLISH,BREAKUP,BREAKDOWN,BREAKANY,DIPBUY,RIPSELL,BREAKFIRST,}
				format[j].set(BREAKFIRST) 
				self.tickers_labels[i].append(tk.OptionMenu(self.frame, format[j], *sorted(self.trigger_types)))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			#Trigger timer
			elif j==11:
				self.tickers_labels[i].append(tk.Entry(self.frame ,textvariable=format[j],width=self.width[j]))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

			elif j==len(format)-1:
				support,resistence = format[3],format[4]
				timer_trade = format[11]
				type_trade = format[10]
				info = [symbol,support,resistence,timer_trade,type_trade,default_risk]
				self.tickers_labels[i].append(tk.Button(self.frame,textvariable=format[j],width=10,command = lambda info=info: self.break_out_trade(info)))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#add configure entry button. 
		#command = lambda s=symbol: self.delete_symbol_reg_list(s))

		#

		#symbol,status,checker,support,resistance ,range_,atr,cur_price,eva,algo_status,trigger_type,trigger_timer]


		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

		#algo_placer("AAPL.NQ","Breakout on Resistance on 134.45 for 60 secs",134.45,133.45,500)

	def break_out_trade(self,info,auto=False):

		symbol,support,resistence,timer_trade,type_trade,default_risk = info[0],float(info[1].get()),float(info[2].get()),info[3].get(),info[4].get(),info[5].get()

		print(symbol,support,resistence,timer_trade,type_trade,default_risk)
		risk = 0
		try:
			risk = float(default_risk)
		except:
			risk = 0

		data_list = {}
		atr,oha,ohs,ola,ols = self.data.symbol_data_ATR[symbol].get(),\
		self.data.symbol_data_openhigh_val[symbol].get(),\
		self.data.symbol_data_openhigh_std[symbol].get(),\
		self.data.symbol_data_openlow_val[symbol].get(),\
		self.data.symbol_data_openlow_std[symbol].get()

		data_list = {"ATR":atr,
					 "OHavg":oha,
					 "OHstd":ohs,
					 "OLavg":ola,
					 "OLstd":ols}
		#'Break Up','Break Down','Any'


		info = ["New order",[type_trade,symbol,support,resistence,risk,data_list]]


		#type_,symbol,description,entry_price,stop_price,position,capital,total_risk

		if risk!=0 and support!=0 and resistence!=0:
			self.algo_commlink.send(info)

	def break_out_trades(self,infos):

		#print(infos)

		l=["Orders Request add"]
		count = 0
		for i in infos:
			if count %2 ==0:
				if count !=0:
					self.algo_commlink.send(l)
					#print(l)
				l=["Orders Request add"]
			l.append(i)
			count+=1

		l[0]="Orders Request finish"
		self.algo_commlink.send(l)
		#self.algo_commlink.send("sdsdsdsdsdsds")
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

				#print("eval.")
				#print(time,ts)
				#print(alert_type)

				if self.eval_time != seconds:
					self.eval_time = seconds
					if alert_type=="breakout":


						### ASSUME NUMBER ONLY.
						cur_price= round(alerts_vals[2].get(),3)
						support= to_number(alerts_vals[3].get())
						resistance =  to_number(alerts_vals[4].get())

						#print("breakout check:",cur_price,support,resistance)

						if support != 0.00 and resistance != 0.00 and ts>569:
							#print(support,resistance,cur_price)

							break_up_confirmation = ["Pending","BreakDn"]
							break_down_confirmation = ["Pending","BreakUp"]
							if cur_price<support and cur_price<resistance and self.alerts[symbol][alert_type]!=2:

								self.alerts[symbol][alert_type] = 2

								if self.breakout_time[symbol] == 0:
									self.breakout_time[symbol] = seconds

								been = seconds - self.breakout_time[symbol]

								#print(seconds,self.breakout_time[symbol],been)

								alert_str = "Support "+alert_type +" :"+str(been)+" sec ago"

								eval_string.set(alert_str)

								#self.alert_pannel.add_alerts([symbol,time,alert_str])
								self.set_latest_alert(symbol, alert_str, time)


								if self.data.algo_breakout_down[symbol].get()!="" and self.data.algo_breakout_status[symbol].get() in break_down_confirmation:

									timer = int(self.data.algo_breakout_timer[symbol].get())
									if timer ==0:
										#send id.
										order_id = self.data.algo_breakout_down[symbol].get()

										self.data.algo_breakout_status[symbol].set("BreakDn")

										print(order_id,"confirmed")
										self.confirm_trade(order_id)

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

								#self.alert_pannel.add_alerts([symbol,time,alert_str])
								self.set_latest_alert(symbol, alert_str, time)

								#send out confirm.

								if self.data.algo_breakout_up[symbol].get()!=""  and self.data.algo_breakout_status[symbol].get() in break_up_confirmation:

									timer = int(self.data.algo_breakout_timer[symbol].get())
									if timer ==0:
										#send id.
										order_id = self.data.algo_breakout_up[symbol].get()
										self.data.algo_breakout_status[symbol].set("BreakUp")

										print(order_id,"confirmed")
										self.confirm_trade(order_id)

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


									if self.data.algo_breakout_down[symbol].get()!="" and self.data.algo_breakout_status[symbol].get() in break_down_confirmation:

										timer = int(self.data.algo_breakout_timer[symbol].get())
										if been>=timer :
											#send id.
											order_id = self.data.algo_breakout_down[symbol].get()

											self.data.algo_breakout_status[symbol].set("BreakDn")

											print(order_id,"confirmed")

											self.confirm_trade(order_id)


								if self.alerts[symbol][alert_type]==1:

									if been<60:
										alert_str = "Resistance "+alert_type +" :"+str(been)+" sec ago"
									else:
										alert_str = "Resistance "+alert_type +" :"+str(been//60)+" min ago"	

									eval_string.set(alert_str)


									if self.data.algo_breakout_up[symbol].get()!="" and self.data.algo_breakout_status[symbol].get() in break_up_confirmation:

										timer = int(self.data.algo_breakout_timer[symbol].get())
										if been>=timer :
											#send id.
											order_id = self.data.algo_breakout_up[symbol].get()
											self.data.algo_breakout_status[symbol].set("BreakUp")

											print(order_id,"confirmed")

											self.confirm_trade(order_id)

								if self.alerts[symbol][alert_type]!=0:
									if been>60 and been<180:
										#green
										eval_label["background"]="#67FF37"
									if been>180 and been <300:
										eval_label["background"]="yellow"

									# if been >180 and been <190:
									# 	if auto_trade[symbol].get()==1 and self.alerts[symbol][alert_type]==1:
									# 		self.data.ppro.long(symbol)
									# 	if auto_trade[symbol].get()==1 and self.alerts[symbol][alert_type]==2:
									# 		self.data.ppro.short(symbol)

									if been>300 and been <600:
										eval_label["background"]="#FF5B5B"
									if been>600:
										eval_label["background"]="red"

					else:

						cur_price= abs(round(alerts_vals[2].get(),3))
						mean= round(alerts_vals[3].get(),3)
						std=  round(alerts_vals[4].get(),3)

						#on certain alert_type, the math can be different. 


						if std != 0:
							cur = round((cur_price-mean)/std,1)
							eval_string.set(str(cur)+" from mean")
						else:
							cur = 0
							eval_string.set("Unable to process std 0")

						#color.
						#cur = abs(cur)
						alert_val = alerts_vals[6]
						alert_val.set(cur)

						if cur <0.5:
							eval_label["background"]="white"

						elif cur>0.5 and cur<1:

							alert_str = "Moderate "+alert_type
							eval_label["background"]="#97FEA8"

							if ts>570 and self.alerts[symbol][alert_type] < 0.5:
								self.alerts[symbol][alert_type] = 0.5
								#self.alert_pannel.add_alerts([symbol,time,alert_str])
								self.set_latest_alert(symbol, alert_str, time)

						elif cur>1 and cur<2 and self.alerts[symbol][alert_type] < 1:
							self.alerts[symbol][alert_type] = 1
							alert_str = "High "+alert_type
							eval_label["background"]="yellow"
							if ts>570:
								#only set when there is higher severity. 
								#self.alert_pannel.add_alerts([symbol,time,alert_str])
								self.set_latest_alert(symbol, alert_str, time)
						elif cur>2 and self.alerts[symbol][alert_type] < 2:

							self.alerts[symbol][alert_type] = 2
							### Send the alert to alert pannel.
							alert_str = "Very high "+alert_type
							eval_label["background"]="red"
							if ts>570:
								#self.alert_pannel.add_alerts([symbol,time,alert_str])
								self.set_latest_alert(symbol, alert_str, time)

		except Exception as e:
			print("Alert Error:",e)


	def confirm_trade(self,order_id):

		self.algo_commlink.send(["Confirmed",order_id])

class alert_map(pannel):
	def __init__(self,frame,data):

		self.reverse= True
		super().__init__(frame)

		self.labels = ["Ticker","Status","Prev Close","High-Low","Open-High","Open-Low","Open Range","Open Vol","5m Range","5m Vol"]
		self.width = [8,10,8,8,8,8,8,8,8,8]

		command={}
		command["Prev Close"] = lambda :self.sort_cur_range(self.data.alert_prev_val)
		command["High-Low"] = lambda :self.sort_cur_range(self.data.alert_hl_val)
		command["Open-High"] = lambda :self.sort_cur_range(self.data.alert_oh_val)
		command["Open-Low"] = lambda :self.sort_cur_range(self.data.alert_ol_val)
		command["Open Range"] = lambda :self.sort_cur_range(self.data.alert_openning_rg_val)
		command["Open Vol"] = lambda :self.sort_cur_range(self.data.alert_openning_vol_val)
		command["5m Range"] = lambda :self.sort_cur_range(self.data.alert_recent5_rg)
		command["5m Vol"] = lambda :self.sort_cur_range(self.data.alert_recent5_vol)
		self.labels_creator(self.frame,command)
		self.alert_base = []

		self.data = data

	def add_symbol(self,symbol):

		#init the alert value

		l = self.label_count

		self.tickers_labels[symbol] = []
		self.tickers_tracers[symbol] = []
		i = symbol


		info = [i,\
			self.data.symbol_status[symbol],\
			self.data.alert_prev_val[symbol],\
			self.data.alert_hl_val[symbol],\
			self.data.alert_oh_val[symbol],
			self.data.alert_ol_val[symbol],
			self.data.alert_openning_rg_val[symbol],
			self.data.alert_openning_vol_val[symbol],
			self.data.alert_recent5_rg[symbol],
			self.data.alert_recent5_vol[symbol]]

		for j in range(len(info)):
			if j >0:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=info[j],width=self.width[j]))
			else:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=info[j],width=self.width[j]))

			if j >1:
				m=info[j].trace('w', lambda *_, val=info[j],label=self.tickers_labels[i][j]: color_bind(val,label))
				self.tickers_tracers[i].append((info[j],m))

			self.label_default_configure(self.tickers_labels[i][j])
			self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

	# def sort_cur_range(self,d):

	# 	#get all range,put in a dictionary.

	# 	l = self.data.get_list()
	# 	rank= {}
	# 	for symbol in l:
	# 		rank[symbol] = d[symbol].get()

	# 	self.reverse = False if self.reverse else True
	# 	rank = sorted(rank.items(), reverse=self.reverse,key=lambda x: x[1])

	# 	new_ranking = {}
	# 	for i in range(len(rank)):
	# 		new_ranking[rank[i][0]]=i

	# 	self.redraw(new_ranking)

	# def redraw(self,symbol_list):
	# 	#only change the grid position
	# 	print(symbol_list)
	# 	for key,value in symbol_list.items():
	# 		for j in range(len(self.labels)):
	# 			self.tickers_labels[key][j].grid(row=symbol_list[key]+2,column=j,padx=0)
				
	def delete_symbol(self,symbol):
		for i in self.tickers_tracers[symbol]:
			i[0].trace_vdelete("w",i[1])

		for i in self.tickers_labels[symbol]:
			i.destroy()

		self.tickers_labels.pop(symbol,None)

		self.rebind(self.canvas,self.frame)




class highlow(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

		self.labels = ["Ticker","Status","Cur Range","Cur High","Cur Low","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]

		#a dictionary. labels: function
		command={}
		command["H. Avg"] = lambda :self.sort_cur_range(self.data.symbol_data_range_val)
		command["Evaluation"] = lambda :self.sort_cur_range(self.data.alert_hl_val)

		self.labels_creator(self.frame,command)


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

		alert_val = self.data.alert_hl_val[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Range"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_val]
		labels = [symbol,status,cur_range,cur_high,cur_low,hist_avg,hist_std,hist_range,eva]


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	def print(self):
		print("hello")

	#find a way to bound the special checking value to. hmm. every update.

class openhigh(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

		self.labels = ["Ticker","Status","Cur Range","Cur Open","Cur High","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]

		command={}
		command["H. Avg"] = lambda :self.sort_cur_range(self.data.symbol_data_openhigh_val)
		command["Evaluation"] = lambda :self.sort_cur_range(self.data.alert_oh_val)

		self.labels_creator(self.frame,command)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_openhigh[symbol]
		cur_open = self.data.symbol_price_open[symbol]
		cur_high = self.data.symbol_price_high[symbol]
		hist_avg= self.data.symbol_data_openhigh_val[symbol]
		hist_std = self.data.symbol_data_openhigh_std[symbol]
		hist_range= self.data.symbol_data_openhigh_range[symbol]

		open_now  = self.data.symbol_price_opennow[symbol]

		eva= self.data.symbol_data_openhigh_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		alert_val = self.data.alert_oh_val[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Open-High"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_val,open_now]
		labels = [symbol,status,cur_range,cur_open,cur_high,hist_avg,hist_std,hist_range,eva]


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.
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


				cur_price= abs(round(alerts_vals[2].get(),3))

				now =  round(alerts_vals[7].get(),3)

				mean= round(alerts_vals[3].get(),3)
				std=  round(alerts_vals[4].get(),3)

				#on certain alert_type, the math can be different. 


				if std != 0:
					cur = round((cur_price-mean)/std,1)
					if now>0:
						now_ = round((now-mean)/std,1)
					else:
						now_ = 0 
					eval_string.set("Cur:"+str(now_)+" Max:"+str(cur))
				else:
					cur = 0
					eval_string.set("Unable to process std 0")

				#color.
				#cur = abs(cur)
				alert_val = alerts_vals[6]
				alert_val.set(now_)

				if now_ <0.5:
					eval_label["background"]="white"

				elif now_>0.5 and now_<1:

					alert_str = "Moderate "+alert_type
					eval_label["background"]="#97FEA8"

					if ts>570 and self.alerts[symbol][alert_type] < 0.5:
						self.alerts[symbol][alert_type] = 0.5
						#self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)

				elif now_>1 and now_<2 and self.alerts[symbol][alert_type] < 1:
					self.alerts[symbol][alert_type] = 1
					alert_str = "High "+alert_type
					eval_label["background"]="yellow"
					if ts>570:
						#only set when there is higher severity. 
						#self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)
				elif now_>2 and self.alerts[symbol][alert_type] < 2:

					self.alerts[symbol][alert_type] = 2
					### Send the alert to alert pannel.
					alert_str = "Very high "+alert_type
					eval_label["background"]="red"
					if ts>570:
						#self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)

		except Exception as e:
			print("Alert Error:",e)


class openlow(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

		self.labels = ["Ticker","Status","Cur Range","Cur Open","Cur Low","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]

		command={}
		command["H. Avg"] = lambda :self.sort_cur_range(self.data.symbol_data_openlow_val)
		command["Evaluation"] = lambda :self.sort_cur_range(self.data.alert_ol_val)

		self.labels_creator(self.frame,command)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_openlow[symbol]
		cur_open = self.data.symbol_price_open[symbol]
		cur_low = self.data.symbol_price_low[symbol]
		hist_avg= self.data.symbol_data_openlow_val[symbol]
		hist_std = self.data.symbol_data_openlow_std[symbol]
		hist_range= self.data.symbol_data_openlow_range[symbol]
		open_now  = self.data.symbol_price_opennow[symbol]

		eva= self.data.symbol_data_openlow_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		alert_val = self.data.alert_ol_val[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Open-Low"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_val,open_now]
		labels = [symbol,status,cur_range,cur_open,cur_low,hist_avg,hist_std,hist_range,eva]


		#any alert will need a threshold. deviation. std. 

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)
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


				cur_price= abs(round(alerts_vals[2].get(),3))

				now =  round(alerts_vals[7].get(),3)

				mean= round(alerts_vals[3].get(),3)
				std=  round(alerts_vals[4].get(),3)

				#on certain alert_type, the math can be different. 


				if std != 0:
					cur = round((cur_price-mean)/std,1)
					if now<0:
						now_ = round((abs(now)-mean)/std,1)
					else:
						now_ = 0 
					eval_string.set("Cur:"+str(now_)+" Max:"+str(cur))
				else:
					cur = 0
					eval_string.set("Unable to process std 0")

				#color.
				#cur = abs(cur)
				alert_val = alerts_vals[6]
				alert_val.set(now_)

				if now_ <0.5:
					eval_label["background"]="white"

				elif now_>0.5 and now_<1:

					alert_str = "Moderate "+alert_type
					eval_label["background"]="#97FEA8"

					if ts>570 and self.alerts[symbol][alert_type] < 0.5:
						self.alerts[symbol][alert_type] = 0.5
						#self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)

				elif now_>1 and now_<2 and self.alerts[symbol][alert_type] < 1:
					self.alerts[symbol][alert_type] = 1
					alert_str = "High "+alert_type
					eval_label["background"]="yellow"
					if ts>570:
						#only set when there is higher severity. 
						#self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)
				elif now_>2 and self.alerts[symbol][alert_type] < 2:

					self.alerts[symbol][alert_type] = 2
					### Send the alert to alert pannel.
					alert_str = "Very high "+alert_type
					eval_label["background"]="red"
					if ts>570:
						#self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)

		except Exception as e:
			print("Alert Error:",e)
	#find a way to bound the special checking value to. hmm. every update.

#########################
class open_now(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data,)

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

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

		self.labels = ["Ticker","Status","Prev Close","Cur Range","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,15,15]

		command={}
		command["H. Avg"] = lambda :self.sort_cur_range(self.data.symbol_data_prev_close_val)
		command["Evaluation"] = lambda :self.sort_cur_range(self.data.alert_prev_val)

		self.labels_creator(self.frame,command)

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

		alert_val = self.data.alert_prev_val[symbol]

		value_position = 2
		alert_position = 7
		alert_type = "Change Since Prev Close"

		#cur, mean, std. symbol, time.
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_val]
		labels = [symbol,status,prev_close,cur_range,hist_avg,hist_std,hist_range,eva]


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std.

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class firstfive(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

		self.labels = ["Ticker","Status","Cur Range","H. Avg","H. Std","H. Range","Cur Vol","H.Vol Avg","H.Vol Std","H.Vol Range","Evaluation:Range","Evaluation:Volume"]
		self.width = [8,10,7,7,7,7,7,7,7,12,14,15,15]

		command={}
		command["H. Avg"] = lambda :self.sort_cur_range(self.data.symbol_data_first5_val)
		command["Evaluation:Range"] = lambda :self.sort_cur_range(self.data.alert_openning_rg_val)

		self.labels_creator(self.frame,command)

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

		alert_val1 = self.data.alert_openning_rg_val[symbol]
		alert_val2 = self.data.alert_openning_vol_val[symbol]


		labels = [symbol,status,cur_range,hist_avg,hist_std,hist_range,cur_vol,hist_v_avg,hist_v_std,hist_v_range,eva,eva2]

		value_position = 2
		alert_position = 10
		alert_type = "Opening Rg"
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_val1]
		#cur, mean, std. symbol, time. 
		

		value_position2 = 6
		alert_position2 = 11

		alert_type2 = "Opening Vol"
		alertvals2= [symbol,time,cur_vol,hist_v_avg,hist_v_std,alert_type2,alert_val2]


		alert_positions = [alert_position,alert_position2]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		alerts[alert_position2] = [value_position2,alert_position2,alertvals2]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class extremrange(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

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

		alert_val = self.data.alert_recent5_rg[symbol]

		value_position = 2
		alert_position = 6
		alert_type = "Intraday Range"
		alert_time = 0
		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_val]
		labels = [symbol,status,cur_range,hist_avg,hist_std,hist_range,eva]

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class extremevolume(alert):

	def __init__(self,frame,data:Symbol_data_manager):

		super().__init__(frame,data)

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

		alert_val = self.data.alert_recent5_vol[symbol]
		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_vol,hist_avg,hist_std,alert_type,alert_val]
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

	def __init__(self,frame,data:Symbol_data_manager,commlink=None):

		super().__init__(frame,data,commlink)

		self.labels = ["Ticker","Status","AR","Support","Resistance ","Range","ATR","Cur Price","Evaluation","Algo","Trigger Type","Trigger Timer","Configure Entry",]
		self.width = [8,10,4,7,7,7,7,7,25,4,10,10,12]
		self.labels_creator(self.frame)


		self.checker = tk.Checkbutton(frame,variable=self.data.all_auto)
		self.checker.place(x=5, y=5, height=30, width=150, bordermode='ignore')
		self.checker.configure(text='Auto range detection')
		self.checker.toggle()

		self.checker2 = tk.Checkbutton(frame,variable=self.data.all_auto_trade)
		self.checker2.place(x=175, y=5, height=30, width=150, bordermode='ignore')
		self.checker2.configure(text='Toggle all Breakout algo')

		# self.default_capital = 
		# self.default_risk =

		#tk.Label(frame,text="Default capital per trade:",height=1,width=20).place(x=180,y=5)

		self.default_risk = tk.StringVar()

		tk.Label(frame,text="Default risk per trade:",height=1,width=20).place(x=340,y=10)

		tk.Entry(frame,textvariable=self.default_risk,width=5).place(x=480,y=10)


		tk.Button(frame,text="Place all algos",command=self.placeall).place(x=550,y=10)

		self.auto_range = self.data.all_auto
		self.auto_trade =self.data.all_auto_trade

		self.socket = Label(frame,textvariable=self.data.algo_socket,background="red",height=1,width=12)
		self.connection =Label(frame,textvariable=self.data.algo_manager_connected,background="red",height=1,width=14)

		self.socket.place(x=650,y=10)
		self.connection.place(x=750,y=10)

		self.data.all_auto.trace('w', lambda *_,vals=self.data.auto_support_resistance,val=self.data.all_auto: self.set_auto(vals,val))
		self.data.all_auto_trade.trace('w', lambda *_,vals=self.data.algo_breakout_trade,val=self.data.all_auto_trade: self.set_auto(vals,val))

		self.data.algo_socket.trace('w', lambda *_,vals=self.socket,val=self.data.algo_socket: self.color(vals,val))
		self.data.algo_manager_connected.trace('w', lambda *_,vals=self.connection,val=self.data.algo_manager_connected: self.color(vals,val))


	def placeall(self):


		print("Placing all")

		total = []
		for symbol in self.data.get_list():

			if self.data.algo_breakout_trade[symbol].get()==True:

				support = self.data.symbol_data_support[symbol]
				resistance  = self.data.symbol_data_resistance[symbol]
				timer_trade = self.data.algo_breakout_timer[symbol]
				type_trade = self.data.algo_breakout_type[symbol]
				default_risk = self.default_risk
				info = [symbol,support,resistance,timer_trade,type_trade,default_risk]

				#self.break_out_trade(info,True)

				#print("Placing ",symbol)
				symbol,support,resistence,timer_trade,type_trade,default_risk = info[0],float(info[1].get()),float(info[2].get()),info[3].get(),info[4].get(),info[5].get()
				atr,oha,ohs,ola,ols = self.data.symbol_data_ATR[symbol].get(),\
				self.data.symbol_data_openhigh_val[symbol].get(),\
				self.data.symbol_data_openhigh_std[symbol].get(),\
				self.data.symbol_data_openlow_val[symbol].get(),\
				self.data.symbol_data_openlow_std[symbol].get()

				default_risk = float(default_risk)
				data_list = {"ATR":atr,
							 "OHavg":oha,
							 "OHstd":ohs,
							 "OLavg":ola,
							 "OLstd":ols}
				if default_risk!=0 and support!=0 and resistence!=0:
					total.append([type_trade,symbol,support,resistence,default_risk,data_list])
	
		self.break_out_trades(total)
		#print(l)

	def color(self,vals,val):

		if val.get()[-4:]=="alse":
			vals["background"] = "red"
		elif val.get()[-4:]=="True":
			vals["background"] = "#97FEA8"
			
	def set_auto(self,vals,val):

		v = val.get()
		print(v)
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

		cur_price = self.data.symbol_price[symbol]

		checker = self.data.auto_support_resistance[symbol]

		checker_trade = self.data.auto_trade[symbol]

		support = self.data.symbol_data_support[symbol]
		resistance  = self.data.symbol_data_resistance[symbol]

		range_ = self.data.symbol_data_support_resistance_range[symbol]

		atr = self.data.symbol_data_ATR[symbol]
		self.tickers_tracers[symbol] = []

		m=support.trace('w', lambda *_, support=support,resist=resistance,rg=range_: self.range_tracker(support,resist,rg))
		self.tickers_tracers[symbol].append((support,m))

		n=resistance.trace('w', lambda *_, support=support,resist=resistance,rg=range_: self.range_tracker(support,resist,rg))
		self.tickers_tracers[symbol].append((resistance,n))


		algo_placement = self.data.algo_breakout_placement[symbol]

		eva= self.data.symbol_data_breakout_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		algo_data = self.data.algo_breakout_type[symbol]
		algo_trade,trigger_timer,trigger_type = self.data.algo_breakout_trade[symbol],self.data.algo_breakout_timer[symbol],self.data.algo_breakout_type[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 7
		alert_position = 8
		alert_type = "breakout"

		alert_time = 0


		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_price,support,resistance ,alert_type]
		labels = [symbol,status,checker,support,resistance ,range_,atr,cur_price,eva,algo_trade,trigger_type,trigger_timer,algo_placement]

		#any alert will need a threshold. deviation. std. or type.

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		default_risk = self.default_risk
		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol_breakout(symbol,labels,alert_positions,alerts,data_ready,default_risk)
