
from tkinter import *
import numpy as np
from os import path
import threading
import time
import requests


class Symbol_data_manager:	

	#if file does not exist, create an empty file. 
	def __init__(self):

		if not path.exists("list.txt"):
			self.symbols = []
		else:
			self.symbols = np.array(np.loadtxt('list.txt',dtype="str")).tolist()

			if type(self.symbols) is str:
				self.symbols = [self.symbols]

		print("data initilize:",self.symbols)

		self.reg_symbols = self.symbols[:]
		#These filed need to be initilized. 

		self.symbol_init =[]


		#system

		self.ppro = None

		self.ppro_status = StringVar()#.set("Ppro status: Connecting")
		self.ppro_status.set("Ppro Status: Connecting")

		self.auto_support_resistance = {} 
		self.auto_trade = {}

		self.all_auto_trade = IntVar()
		self.all_auto = IntVar()

		#basics
		self.symbol_price = {}
		self.symbol_price_high = {}
		self.symbol_price_low = {}
		self.symbol_price_open = {}
		self.symbol_price_range = {}
		self.symbol_price_openhigh = {}
		self.symbol_price_openlow = {}

		self.symbol_price_opennow = {}

		self.symbol_price_prevclose = {}
		self.symbol_price_prevclose_to_now= {}

		### Update these upon new ticks 
		self.minute_count = {}
		self.minute_data = {}
		self.minute_timestamp = {}
		self.minute_timestamp_val = {}

		self.last_5_min_range = {}
		self.last_5_min_volume = {}


		self.first_5_list = []
		self.first_5_min_range = {}
		self.first_5_min_volume = {}
		#self.symbol_volume = {}

		self.symbol_status = {}
		self.symbol_status_color = {}
		self.symbol_update_time = {}

		#data

		self.symbol_data_openhigh_range = {}
		self.symbol_data_openlow_range = {}
		self.symbol_data_range_range = {}

		self.symbol_data_openhigh_val = {}
		self.symbol_data_openlow_val = {}
		self.symbol_data_range_val = {}

		self.symbol_data_openhigh_dis = {}
		self.symbol_data_openlow_dis = {}
		self.symbol_data_range_dis = {}

		self.symbol_data_openhigh_std = {}
		self.symbol_data_openlow_std = {}
		self.symbol_data_range_std = {}

		self.symbol_data_first5_range = {}
		self.symbol_data_first5_vol_range = {}

		self.symbol_data_first5_val = {}
		self.symbol_data_first5_vol_val = {}

		self.symbol_data_first5_std = {}
		self.symbol_data_first5_vol_std = {}

		self.symbol_data_first5_dis = {}
		self.symbol_data_first5_vol_dis = {}


		self.symbol_data_normal5_range = {}
		self.symbol_data_normal5_vol_range = {}

		self.symbol_data_normal5_val = {}
		self.symbol_data_normal5_vol_val = {}

		self.symbol_data_normal5_std = {}
		self.symbol_data_normal5_vol_std = {}

		self.symbol_data_normal5_dis = {}
		self.symbol_data_normal5_vol_dis = {}

		self.symbol_data_first5_range_eval = {}
		self.symbol_data_first5_vol_eval = {}

		self.symbol_data_normal5_range_eval = {}
		self.symbol_data_normal5_vol_eval = {}

		self.symbol_data_openhigh_eval = {}
		self.symbol_data_openlow_eval= {}
		self.symbol_data_range_eval = {}

		self.symbol_data_resistance = {}
		self.symbol_data_support = {}
		self.symbol_data_support_resistance_range = {}
		self.symbol_data_breakout_eval = {}


		self.symbol_data_prev_close_dis ={}
		self.symbol_data_prev_close_val ={}
		self.symbol_data_prev_close_range ={}
		self.symbol_data_prev_close_std ={}
		self.symbol_data_prev_close_eval = {}

		self.symbol_data_ATR = {}

		#alerts
		self.symbol_last_alert = {}
		self.symbol_last_alert_time ={}

		self.alert_prev_val = {}
		self.alert_hl_val = {}
		self.alert_oh_val = {}
		self.alert_ol_val = {}
		self.alert_openning_rg_val = {}
		self.alert_openning_vol_val ={}
		self.alert_recent5_rg = {}
		self.alert_recent5_vol = {}


		#mark this when a symbol datastructure is completely loaded. 

		self.data_list = [self.symbol_data_openhigh_range,self.symbol_data_openlow_range,self.symbol_data_range_range,
		self.symbol_data_first5_range,self.symbol_data_first5_vol_range,self.symbol_data_normal5_range,
		self.symbol_data_normal5_vol_range,
		self.symbol_data_openhigh_val,self.symbol_data_openlow_val,self.symbol_data_range_val,
		self.symbol_data_first5_val,self.symbol_data_first5_vol_val,self.symbol_data_normal5_val,
		self.symbol_data_normal5_vol_val,
		self.symbol_data_openhigh_std,self.symbol_data_openlow_std,self.symbol_data_range_std,
		self.symbol_data_first5_std,self.symbol_data_first5_vol_std,self.symbol_data_normal5_std,
		self.symbol_data_normal5_vol_std,
		self.symbol_data_prev_close_val,self.symbol_data_prev_close_range,self.symbol_data_prev_close_std,self.symbol_data_ATR]
		self.data_ready = {}

		self.update_list = [self.symbol_status,self.symbol_price,self.symbol_update_time,
		self.minute_timestamp_val,
		self.symbol_price_high,
		self.symbol_price_low ,
		self.symbol_price_range,
		self.last_5_min_range,
		self.last_5_min_volume,
		self.symbol_price_open,
		self.symbol_price_openhigh,
		self.symbol_price_openlow,
		self.first_5_min_range,
		self.first_5_min_volume,
		self.symbol_price_prevclose,
		self.symbol_price_prevclose_to_now]

		self.init_data()


	def toggle_all(self,vals,val):
		for i in self.symbols:
			vals[i].set(val)

	def init_data(self):

		for i in self.symbols:
			self.init_symbol(i)


	def set_ppro_manager(self,ppro):
		self.ppro = ppro

	def set_database_manager(self,database):
		self.database = database

	def init_symbol(self,i):

		#system
		self.auto_support_resistance[i] = IntVar()
		self.auto_trade[i] = IntVar()
		#basic

		self.data_ready[i] = BooleanVar(value=False)
		self.symbol_status[i] = StringVar()
		self.symbol_status_color[i] = StringVar()
		self.symbol_price[i] = DoubleVar()

		self.symbol_price_open[i] = DoubleVar()
		self.symbol_price_range[i] = DoubleVar()
		self.symbol_price_high[i] = DoubleVar()
		self.symbol_price_low[i] = DoubleVar()
		self.symbol_price_openhigh[i] = DoubleVar()
		self.symbol_price_openlow[i] = DoubleVar()
		self.symbol_price_opennow[i] = DoubleVar()
		self.symbol_price_prevclose_to_now[i] = DoubleVar()

		self.symbol_price_prevclose[i] = DoubleVar()

		self.minute_count[i] = 0
		self.minute_data[i] = {"high":[],"low":[],"vol":[]}
		self.minute_timestamp[i] = []
		self.minute_timestamp_val[i] =DoubleVar()

		self.last_5_min_range[i] = DoubleVar()
		self.last_5_min_volume[i] = DoubleVar()

		self.first_5_min_range[i] = DoubleVar()
		self.first_5_min_volume[i] = DoubleVar()

		self.symbol_update_time[i] = StringVar()

		#data
		self.symbol_data_openhigh_dis[i] = []
		self.symbol_data_openlow_dis[i] = []
		self.symbol_data_range_dis[i] = []

		self.symbol_data_normal5_dis[i]  = []
		self.symbol_data_normal5_vol_dis[i]  = []
		self.symbol_data_first5_dis[i] = []
		self.symbol_data_first5_vol_dis[i] = []

		self.symbol_data_openhigh_range[i] = StringVar()
		self.symbol_data_openlow_range[i] = StringVar()
		self.symbol_data_range_range[i] = StringVar()

		self.symbol_data_openhigh_val[i] = DoubleVar()
		self.symbol_data_openlow_val[i] = DoubleVar()
		self.symbol_data_range_val[i] = DoubleVar()

		self.symbol_data_openhigh_std[i] = DoubleVar()
		self.symbol_data_openlow_std[i] = DoubleVar()
		self.symbol_data_range_std[i] = DoubleVar()

		self.symbol_data_first5_range[i] = StringVar()
		self.symbol_data_first5_vol_range[i] = StringVar()

		self.symbol_data_first5_val[i] = DoubleVar()
		self.symbol_data_first5_vol_val[i] = DoubleVar()

		self.symbol_data_first5_std[i] = DoubleVar()
		self.symbol_data_first5_vol_std[i] = DoubleVar()

		self.symbol_data_normal5_range[i] = StringVar()
		self.symbol_data_normal5_vol_range[i] = StringVar()



		self.symbol_data_normal5_val[i] = DoubleVar()
		self.symbol_data_normal5_vol_val[i] = DoubleVar()

		self.symbol_data_normal5_std[i] = DoubleVar()
		self.symbol_data_normal5_vol_std[i] = DoubleVar()

		#eval

		self.symbol_data_first5_range_eval[i] =  StringVar()
		self.symbol_data_first5_vol_eval[i] = StringVar()

		self.symbol_data_normal5_range_eval[i] =  StringVar()
		self.symbol_data_normal5_vol_eval[i] = StringVar()

		self.symbol_data_openhigh_eval[i] = StringVar()
		self.symbol_data_openlow_eval[i] = StringVar()
		self.symbol_data_range_eval[i] = StringVar()


		###newly added

		self.symbol_data_prev_close_dis[i] = []
		self.symbol_data_prev_close_val[i] = DoubleVar()
		self.symbol_data_prev_close_range[i] = StringVar()
		self.symbol_data_prev_close_std[i]  = DoubleVar()
		self.symbol_data_prev_close_eval[i] = StringVar()

		self.symbol_data_ATR[i] = DoubleVar()


		###
		self.symbol_data_resistance[i] = DoubleVar()
		self.symbol_data_support[i] = DoubleVar()
		self.symbol_data_support_resistance_range[i] = DoubleVar()
		self.symbol_data_breakout_eval[i] = StringVar()

		#alert
		self.symbol_last_alert[i] = StringVar()
		self.symbol_last_alert_time[i] = StringVar()

		self.alert_prev_val[i] = DoubleVar()
		self.alert_hl_val[i] = DoubleVar()
		self.alert_oh_val[i] = DoubleVar()
		self.alert_ol_val[i] = DoubleVar()
		self.alert_recent5_rg[i] = DoubleVar()
		self.alert_recent5_vol[i] = DoubleVar()
		self.alert_openning_rg_val[i] = DoubleVar()
		self.alert_openning_vol_val[i] = DoubleVar()
		#self.ppro.register(i)
		# reg = threading.Thread(target=register,args=(i,), daemon=True)
		# reg.start()

	def change_status(self,symbol,status):
		self.symbol_status[symbol].set(status)

	def change_status_color(self,symbol,color):
		self.symbol_status_color[symbol].set(color)


	def add(self,symbol):
		self.init_symbol(symbol)
		self.symbols.append(symbol)
		self.save()

		self.database.send_request(symbol)
		self.ppro.register(symbol)

		print("registering:",symbol)



	def delete(self,symbol):
		if symbol in self.symbols:
			self.symbols.remove(symbol)
		self.save()

		self.ppro.deregister(symbol)
		# dereg = threading.Thread(target=deregister,args=(symbol,), daemon=True)
		# dereg.start()

	def save(self):
		np.savetxt('list.txt',self.symbols, delimiter=",", fmt="%s")   
	def get_list(self):
		return self.symbols

	def get_count(self):
		return len(self.symbols)
