
from tkinter import *
import numpy as np
from os import path
import threading
import time
import requests



symbol_status = "symbol_status"
symbol_price = "symbol_price"
symbol_update_time = "symbol_update_time"
minute_timestamp_val = "minute_timestamp_val"
symbol_price_high = "symbol_price_high"
symbol_price_low = "symbol_price_low"
symbol_price_premarket_high = "symbol_price_premarket_high"
symbol_price_premarket_low = "symbol_price_premarket_low"
symbol_price_range = "symbol_price_range"
last_5_min_range = "last_5_min_range"
last_5_min_volume = "last_5_min_volume"
symbol_price_open = "symbol_price_open"
symbol_price_openhigh = "symbol_price_openhigh"
symbol_price_openlow = "symbol_price_openlow"
symbol_price_opennow = "symbol_price_opennow"
first_5_min_range = "first_5_min_range"
first_5_min_volume = "first_5_min_volume"
symbol_price_prevclose = "symbol_price_prevclose"
symbol_price_prevclose_to_now = "symbol_price_prevclose_to_now"
symbol_percentage_since_close = "symbol_percentage_since_close"
symbol_percentage_since_open = "symbol_percentage_since_open"
symbol_percentage_last_5 = "symbol_percentage_last_5"
symbol_position_status = "symbol_position_status"


open_high_eval_alert = "open_high_eval_alert"
open_high_eval_value = "open_high_eval_value"

open_low_eval_alert = "open_low_eval_alert"
open_low_eval_value = "open_low_eval_value"

high_low_alert = "high_low_alert"
high_low_eval = "high_low_eval"

first_5_eval = "first_5_eval"
first_5_alert ="first_5_alert"
first_5_vol_eval ="first_5_vol_eval"
first_5_vol_alert = "first_5_vol_alert"

normal_5_eval = "normal_5_eval"
normal_5_alert =  "normal_5_alert"

normal_5_vol_eval = "normal_5_vol_eval"
normal_5_vol_alert =  "normal_5_vol_alert"

prev_eval = "prev_eval"
prev_alert = "prev_alert"


open_high_range ="open_high_range"
open_high_val ="open_high_val"
open_high_std ="open_high_std"

open_low_range ="open_low_range"
open_low_val ="open_low_val"
open_low_std ="open_low_std"

high_low_range ="high_low_range"
high_low_val ="high_low_val"
high_low_std ="high_low_std"

first_5_range ="first_5_range"
first_5_val ="first_5_val"
first_5_std ="first_5_std"

first_5_vol_range ="first_5_vol_range"
first_5_vol_val ="first_5_vol_val"
first_5_vol_std ="first_5_vol_std"

normal_5_range ="normal_5_range"
normal_5_val ="normal_5_val"
normal_5_std ="normal_5_std"

normal_5_vol_range ="normal_5_vol_range"
normal_5_vol_val ="normal_5_vol_val"
normal_5_vol_std ="normal_5_vol_std"

prev_close_range ="prev_close_range"
prev_close_val ="prev_close_val"
prev_close_std ="prev_close_std"

symbol_data_ATR ="symbol_data_ATR"

expected_momentum ="expected_momentum"


class Symbol_data_manager:	

	"""if file does not exist, create an empty file. """
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

		self.algo_socket = StringVar(value="Socket:False")
		self.algo_manager_connected = StringVar(value="AM:False")
		#basics
		self.symbol_price = {}
		self.symbol_price_high = {}
		self.symbol_price_low = {}
		self.symbol_price_open = {}
		self.symbol_price_range = {}
		self.symbol_price_openhigh = {}
		self.symbol_price_openlow = {}
		self.symbol_open_current_range = {}

		self.symbol_price_premarket_high = {}
		self.symbol_price_premarket_low = {}

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
		self.expected_momentum = {}
		self.risk_reward_ratio = {}
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


		#algos.

		self.algo_breakout = {}


		self.algo_breakout_status = {}
		self.algo_breakout_trade = {}
		self.algo_breakout_up = {}
		self.algo_breakout_down = {}
		self.algo_breakout_timer = {}
		self.algo_breakout_type = {}

		self.algo_breakout_placement={}
		#####

		self.symbol_position_status = {}
		self.symbol_percentage_since_close = {}
		self.symbol_percentage_since_open = {}
		self.symbol_percentage_last_5 = {}



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
		#self.symbol_data_openhigh_dis,self.symbol_data_openlow_dis,self.symbol_data_range_dis,self.symbol_data_prev_close_dis


		self.data_list = {}

		self.data_list[open_high_range] = self.symbol_data_openhigh_range
		self.data_list[open_high_val] = self.symbol_data_openhigh_val
		self.data_list[open_high_std] = self.symbol_data_openhigh_std

		self.data_list[open_low_range] = self.symbol_data_openlow_range
		self.data_list[open_low_val] = self.symbol_data_openlow_val
		self.data_list[open_low_std] = self.symbol_data_openlow_std

		self.data_list[high_low_range] = self.symbol_data_range_range
		self.data_list[high_low_val] = self.symbol_data_range_val
		self.data_list[high_low_std] = self.symbol_data_range_std

		self.data_list[first_5_range] = self.symbol_data_first5_range
		self.data_list[first_5_val] = self.symbol_data_first5_val
		self.data_list[first_5_std] = self.symbol_data_first5_std

		self.data_list[first_5_vol_range] = self.symbol_data_first5_vol_range
		self.data_list[first_5_vol_val] =  self.symbol_data_first5_vol_val
		self.data_list[first_5_vol_std] = self.symbol_data_first5_vol_std

		self.data_list[normal_5_range] = self.symbol_data_normal5_range
		self.data_list[normal_5_val] = self.symbol_data_normal5_val
		self.data_list[normal_5_std] = self.symbol_data_normal5_std

		self.data_list[normal_5_vol_range] = self.symbol_data_normal5_vol_range
		self.data_list[normal_5_vol_val] = self.symbol_data_normal5_vol_val
		self.data_list[normal_5_vol_std] = self.symbol_data_normal5_vol_std

		self.data_list[prev_close_range] = self.symbol_data_prev_close_range
		self.data_list[prev_close_val] = self.symbol_data_prev_close_val
		self.data_list[prev_close_std] = self.symbol_data_prev_close_std

		self.data_list[symbol_data_ATR] = self.symbol_data_ATR

		self.data_list[expected_momentum] = self.expected_momentum

		self.data_ready = {}

		#self.symbol_data_openhigh_dis,self,symbol_data_openlow_dis,self.symbol_data_range_dis

		#self.symbol_price_high,self.symbol_price_low,self.symbol_price_premarket_high,self.symbol_price_premarket_low

		#['Connected', 'QQQ.NQ', 310.64, '14:06:46', 846, 321.5, 310.47, 321.5, 310.47, 11.03, 0.0, 0.0, 317.27, 4.23, 6.8, 0, 0, 318.4, -7.76, 'New Low']

		update_list = [symbol_status,symbol_price,symbol_update_time,
		minute_timestamp_val,
		symbol_price_high,
		symbol_price_low ,
		symbol_price_premarket_high,
		symbol_price_premarket_low,
		symbol_price_range,
		last_5_min_range,
		last_5_min_volume,
		symbol_price_open,
		symbol_price_openhigh,
		symbol_price_openlow,
		symbol_price_opennow,
		first_5_min_range,
		first_5_min_volume,
		symbol_price_prevclose,
		symbol_price_prevclose_to_now,
		symbol_percentage_since_close,
		symbol_percentage_since_open,
		symbol_percentage_last_5,
		symbol_position_status]


		self.update_list = {}

		self.update_list[symbol_status] = self.symbol_status
		self.update_list[symbol_price] = self.symbol_price
		self.update_list[symbol_update_time] = self.symbol_update_time
		self.update_list[minute_timestamp_val] = self.minute_timestamp_val
		self.update_list[symbol_price_high] = self.symbol_price_high
		self.update_list[symbol_price_low] = self.symbol_price_low
		self.update_list[symbol_price_premarket_high] = self.symbol_price_premarket_high
		self.update_list[symbol_price_premarket_low] = self.symbol_price_premarket_low
		self.update_list[symbol_price_range] = self.symbol_price_range
		self.update_list[last_5_min_range] = self.last_5_min_range
		self.update_list[last_5_min_volume] = self.last_5_min_volume
		self.update_list[symbol_price_open] = self.symbol_price_open
		self.update_list[symbol_price_openhigh] = self.symbol_price_openhigh
		self.update_list[symbol_price_openlow] = self.symbol_price_openlow
		self.update_list[symbol_price_opennow] = self.symbol_price_opennow
		self.update_list[first_5_min_range] = self.first_5_min_range
		self.update_list[first_5_min_volume] = self.first_5_min_volume
		self.update_list[symbol_price_prevclose] = self.symbol_price_prevclose
		self.update_list[symbol_price_prevclose_to_now] = self.symbol_price_prevclose_to_now
		self.update_list[symbol_percentage_since_close] = self.symbol_percentage_since_close
		self.update_list[symbol_percentage_since_open] = self.symbol_percentage_since_open
		self.update_list[symbol_percentage_last_5] = self.symbol_percentage_last_5
		self.update_list[symbol_position_status] = self.symbol_position_status
		


		self.update_list[open_high_eval_alert] = self.alert_oh_val
		self.update_list[open_high_eval_value] = self.symbol_data_openhigh_eval

		self.update_list[open_low_eval_alert] = self.alert_ol_val
		self.update_list[open_low_eval_value] = self.symbol_data_openlow_eval

		self.update_list[high_low_alert] = self.alert_hl_val
		self.update_list[high_low_eval] = self.symbol_data_range_eval

		self.update_list[first_5_eval] = self.symbol_data_first5_range_eval
		self.update_list[first_5_alert] = self.alert_openning_rg_val
		self.update_list[first_5_vol_eval] = self.symbol_data_first5_vol_eval
		self.update_list[first_5_vol_alert] = self.alert_openning_vol_val

		self.update_list[normal_5_eval] = self.symbol_data_normal5_range_eval
		self.update_list[normal_5_alert] =self.alert_recent5_rg

		self.update_list[normal_5_vol_eval] = self.symbol_data_normal5_vol_eval
		self.update_list[normal_5_vol_alert] = self.alert_recent5_vol
										
		self.update_list[prev_eval] = self.symbol_data_prev_close_eval
		self.update_list[prev_alert] = self.alert_prev_val

		# self.update_list = [self.symbol_status,self.symbol_price,self.symbol_update_time,
		# self.minute_timestamp_val,
		# self.symbol_price_high,
		# self.symbol_price_low ,
		# self.symbol_price_premarket_high,
		# self.symbol_price_premarket_low,
		# self.symbol_price_range,
		# self.last_5_min_range,
		# self.last_5_min_volume,
		# self.symbol_price_open,
		# self.symbol_price_openhigh,
		# self.symbol_price_openlow,
		# self.symbol_price_opennow,
		# self.first_5_min_range,
		# self.first_5_min_volume,
		# self.symbol_price_prevclose,
		# self.symbol_price_prevclose_to_now,
		# self.symbol_percentage_since_close,
		# self.symbol_percentage_since_open,
		# self.symbol_percentage_last_5,
		# self.symbol_position_status]

		self.start = False
		self.init_data()



	def toggle_all(self,vals,val):
		for i in self.symbols:
			vals[i].set(val)

	def init_data(self):

		for i in self.symbols:
			self.init_symbol(i)

	def get_symbol_price(self,symbol):

		if symbol in self.symbol_init:
			return self.symbol_price[symbol]
		else:
			print("Cannot find symbol",symbol)
			return None

	def get_open_percentage(self,symbol):

		if symbol in self.symbol_init:
			return self.symbol_percentage_since_open[symbol]
		else:
			print("Cannot find symbol",symbol)
			return None

	def get_position_status(self,symbol):

		if symbol in self.symbol_init:
			return self.symbol_position_status[symbol]
		else:
			print("Cannot find symbol",symbol)
			return None

	def get_close_percentage(self,symbol):

		if symbol in self.symbol_init:
			return self.symbol_percentage_since_close[symbol]
		else:
			print("Cannot find symbol",symbol)
			return None

	def get_last_5_range_percentage(self,symbol):
		if symbol in self.symbol_init:
			return self.symbol_percentage_last_5[symbol]
		else:
			print("Cannot find symbol",symbol)
			return None		

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

		self.symbol_price_premarket_high[i] = DoubleVar()
		self.symbol_price_premarket_low[i] = DoubleVar()

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
		self.expected_momentum[i] = DoubleVar()
		self.risk_reward_ratio[i] = DoubleVar()

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

		#algo

		self.symbol_position_status[i] = StringVar()

		self.symbol_percentage_since_close[i] = DoubleVar()
		self.symbol_percentage_since_open[i] = DoubleVar()
		self.symbol_percentage_last_5[i] = DoubleVar()

		self.symbol_init.append(i)

		self.init_breakout_algo(i)
		#self.ppro.register(i)
		# reg = threading.Thread(target=register,args=(i,), daemon=True)
		# reg.start()

	def init_breakout_algo(self,i):


		#algo status,Trigger timer, Trigger type,###
		# self.algo_breakout[i] = []

		# #Algo status
		# self.algo_breakout[i].append(StringVar())
		# self.algo_breakout[i][0].set("None")

		# #Timer
		# self.algo_breakout[i].append(StringVar())
		# self.algo_breakout[i][1].set(0)

		# #Type. 
		# self.algo_breakout[i].append(StringVar())

		#order number

		# self.algo_breakout_status = {}
		# self.algo_breakout_up = {}
		# self.algo_breakout_down = {}

		self.algo_breakout_status[i] = StringVar()
		self.algo_breakout_trade[i] = BooleanVar(value=False)

		self.algo_breakout_timer[i] = StringVar()
		self.algo_breakout_timer[i].set(0)

		self.algo_breakout_type[i] = StringVar()

		#the ids. 
		self.algo_breakout_up[i] = StringVar()
		self.algo_breakout_up[i].set("")
		self.algo_breakout_down[i] = StringVar()
		self.algo_breakout_down[i].set("")

		self.algo_breakout_placement[i] = StringVar()
		self.algo_breakout_placement[i].set("")

	def change_status(self,symbol,status):
		self.symbol_status[symbol].set(status)


	def change_status_color(self,symbol,color):
		self.symbol_status_color[symbol].set(color)

	#seems i need dua channel? probably not! just stick with it then. 

	def partial_register(self,symbol):
		if symbol not in self.symbol_init:
			self.init_symbol(symbol)
			self.ppro.register(symbol)
			#print("partial registering:",symbol)

	def if_registered(self,symbol):

		return symbol in self.symbol_init


	def add(self,symbol):

		#check if already registered.

		if symbol not in self.symbols:

			if symbol not in self.symbol_init:
				self.init_symbol(symbol)

			self.symbols.append(symbol)
			self.save()

			self.database.send_request(symbol)
			self.ppro.register(symbol)

			#print("full registering:",symbol)
			#print(self.symbol_position_status)
		else:
			print("Trying register:",symbol," already registered")

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






