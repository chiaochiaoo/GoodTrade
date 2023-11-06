import numpy as np
import time 
import threading
import requests 
import json
import numpy as np
import pytz
from datetime import datetime
from datetime import date
import pandas as pd 
from functools import reduce
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

import tkinter as tk
from tkinter import ttk
import io 
import os
import traceback
def PrintException(info,additional="ERROR"):
    # exc_type, exc_obj, tb = sys.exc_info()
    # f = tb.tb_frame
    # lineno = tb.tb_lineno
    # filename = f.f_code.co_filename
    # linecache.checkcache(filename)
    # line = linecache.getline(filename, lineno, f.f_globals)
    # log_print (info+'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(additional,info,exc_type, fname, exc_tb.tb_lineno,traceback.format_exc())
def extract_ts(s):
    return s[-5:]
def extract_day(s):
    return s[:10]


def drop_columns(df,drops):

  drop = []
  for i in df.columns:
    for x in drops:
      if x in i:
        drop.append(i)

  return df.drop(drop, axis=1)

def absolute_mean(sl,window):

  if len(sl)==window:
    return np.mean(np.abs(sl))
  else:
    return np.nan

def tailless_mean(sl,window=0):
  if window==0 or len(sl)==window:
    return np.mean(sl[sl<np.percentile(sl,97)])
  else:
    return np.nan

def log_and_subtract(row):
    log_values = np.log(row)
    return log_values - log_values[0]

# Apply the function to each row using np.apply_along_axis
def slicer_vectorized(a,start,end):
    b = a.view((str,1)).reshape(len(a),-1)[:,start:end]
    return np.fromstring(b.tostring(),dtype=(str,end-start))

def get_symbol_basket(symbol,timeframe,days):

  postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval="+str(timeframe)+"&period="+str(days)+"&regular=0&user=sajali26@hotmail.com&password=guupu4upu"

  r= requests.post(postbody)

  if timeframe=="Day":
    df  = pd.read_csv(StringIO(r.text),names=["day","open","high","low","close","volume"])
    return df
  else:
    df  = pd.read_csv(StringIO(r.text),names=["day","time","open","high","low","close","volume"])

  ts_5 = ['09:30', '09:35', '09:40', '09:45', '09:50', '09:55', '10:00', '10:05', '10:10', '10:15', '10:20', '10:25', '10:30', '10:35', '10:40', '10:45', '10:50', '10:55', '11:00', '11:05', '11:10', '11:15', '11:20', '11:25', '11:30', '11:35', '11:40', '11:45', '11:50', '11:55', '12:00', '12:05', '12:10', '12:15', '12:20', '12:25', '12:30', '12:35', '12:40', '12:45', '12:50', '12:55', '13:00', '13:05', '13:10', '13:15', '13:20', '13:25', '13:30', '13:35', '13:40', '13:45', '13:50', '13:55', '14:00', '14:05', '14:10', '14:15', '14:20', '14:25', '14:30', '14:35', '14:40', '14:45', '14:50', '14:55', '15:00', '15:05', '15:10', '15:15', '15:20', '15:25', '15:30', '15:35', '15:40', '15:45', '15:50', '15:55']
  ts_1 = ["09:30","09:31","09:32","09:33","09:34","09:35","09:36","09:37","09:38","09:39","09:40","09:41","09:42","09:43","09:44","09:45","09:46","09:47","09:48","09:49","09:50","09:51","09:52","09:53","09:54","09:55","09:56","09:57","09:58","09:59","10:00","10:01","10:02","10:03","10:04","10:05","10:06","10:07","10:08","10:09","10:10","10:11","10:12","10:13","10:14","10:15","10:16","10:17","10:18","10:19","10:20","10:21","10:22","10:23","10:24","10:25","10:26","10:27","10:28","10:29","10:30","10:31","10:32","10:33","10:34","10:35","10:36","10:37","10:38","10:39","10:40","10:41","10:42","10:43","10:44","10:45","10:46","10:47","10:48","10:49","10:50","10:51","10:52","10:53","10:54","10:55","10:56","10:57","10:58","10:59","11:00","11:01","11:02","11:03","11:04","11:05","11:06","11:07","11:08","11:09","11:10","11:11","11:12","11:13","11:14","11:15","11:16","11:17","11:18","11:19","11:20","11:21","11:22","11:23","11:24","11:25","11:26","11:27","11:28","11:29","11:30","11:31","11:32","11:33","11:34","11:35","11:36","11:37","11:38","11:39","11:40","11:41","11:42","11:43","11:44","11:45","11:46","11:47","11:48","11:49","11:50","11:51","11:52","11:53","11:54","11:55","11:56","11:57","11:58","11:59","12:00","12:01","12:02","12:03","12:04","12:05","12:06","12:07","12:08","12:09","12:10","12:11","12:12","12:13","12:14","12:15","12:16","12:17","12:18","12:19","12:20","12:21","12:22","12:23","12:24","12:25","12:26","12:27","12:28","12:29","12:30","12:31","12:32","12:33","12:34","12:35","12:36","12:37","12:38","12:39","12:40","12:41","12:42","12:43","12:44","12:45","12:46","12:47","12:48","12:49","12:50","12:51","12:52","12:53","12:54","12:55","12:56","12:57","12:58","12:59","13:00","13:01","13:02","13:03","13:04","13:05","13:06","13:07","13:08","13:09","13:10","13:11","13:12","13:13","13:14","13:15","13:16","13:17","13:18","13:19","13:20","13:21","13:22","13:23","13:24","13:25","13:26","13:27","13:28","13:29","13:30","13:31","13:32","13:33","13:34","13:35","13:36","13:37","13:38","13:39","13:40","13:41","13:42","13:43","13:44","13:45","13:46","13:47","13:48","13:49","13:50","13:51","13:52","13:53","13:54","13:55","13:56","13:57","13:58","13:59","14:00","14:01","14:02","14:03","14:04","14:05","14:06","14:07","14:08","14:09","14:10","14:11","14:12","14:13","14:14","14:15","14:16","14:17","14:18","14:19","14:20","14:21","14:22","14:23","14:24","14:25","14:26","14:27","14:28","14:29","14:30","14:31","14:32","14:33","14:34","14:35","14:36","14:37","14:38","14:39","14:40","14:41","14:42","14:43","14:44","14:45","14:46","14:47","14:48","14:49","14:50","14:51","14:52","14:53","14:54","14:55","14:56","14:57","14:58","14:59","15:00","15:01","15:02","15:03","15:04","15:05","15:06","15:07","15:08","15:09","15:10","15:11","15:12","15:13","15:14","15:15","15:16","15:17","15:18","15:19","15:20","15:21","15:22","15:23","15:24","15:25","15:26","15:27","15:28","15:29","15:30","15:31","15:32","15:33","15:34","15:35","15:36","15:37","15:38","15:39","15:40","15:41","15:42","15:43","15:44","15:45","15:46","15:47","15:48","15:49","15:50","15:51","15:52","15:53","15:54","15:55","15:56","15:57","15:58","15:59",\
          "16:00"]
  ts_15 = [i for i in ts_5[::3]]
  ts_30 = [i for i in ts_5[::6]]

  all_ts = [i for i in ts_1[::timeframe]]

  ### ACC ?#
  print("downloaded. processing...")
  all_index = [r[0] +" " + r[1] for r in itertools.product(df['day'].unique().tolist(),all_ts)]

  df['ts'] = df['day'] + " " + df['time']
  df = df.set_index('ts')

  days = df['day'].unique().tolist()


  unique_days = df['day'].unique()

  all = []
  for day in unique_days:

    k = df.loc[df['day']==day].index

    all.extend(df.loc[k]['volume'].cumsum())

  df['acc_vol'] = all
  ndf = pd.DataFrame()

  ndf['ts'] = all_index


  ndf2  = ndf.merge(df, left_on='ts', right_on='ts',how='left')


  ndf2['volume'] = ndf2['volume'].fillna(0)
  #print(ndf2['ts'])
  ndf2['time'] = ndf2['ts'].apply(extract_ts)
  ndf2['day'] = ndf2['ts'].apply(extract_day)


  ndf2['ts'] = pd.to_datetime(ndf2['ts'])
  ndf2['ts'] = ndf2['ts'].dt.hour*60+ndf2['ts'].dt.minute

  len_unique = len(df['day'].unique())
  number_of_minutes = len(all_ts)
  cumsum_array = np.cumsum(ndf2['volume'].to_numpy().reshape(len_unique,number_of_minutes), axis=1)
  ndf2['acc_vol'] = cumsum_array.flatten()
  # ndf2.loc[(ndf2['time']=="16:15")] = ndf2.loc[(ndf2['time']=="16:15")].interpolate(method="ffill")
  # ndf2.loc[(ndf2['time']=="09:00")] = ndf2.loc[(ndf2['time']=="09:00")].interpolate(method="bfill")

  ndf2 =ndf2.interpolate(method="pad")
  #ndf2 = ndf2.drop(['low','high'],axis=1)
  print("finished. ...")
  ndf2.to_csv("/content/drive/MyDrive/Colab Notebooks/Da_Million_Dollar_Dataset/Raw_Data"+str(timeframe)+"/"+symbol+".csv")

  return ndf2
class model:

	def __init__(self):

		self.model_initialized = False 
		self.model = {}

		self.long_symbols =""
		self.short_symbols =""
		self.pnl = np.array([None for i in range(570,960)])
		self.ts  = np.array([i for i in range(570,960)])
		self.spread = 0
		self.cur = 0
		self.long = 0
		self.short =0
		self.e_pnl = []
		self.e_ts  = []

		self.model_initialized = True 
		self.model_early_chart = False 
		self.historical_computed = False 

		self.historical_computed = False
		self.historical_plus = []
		self.historical_minus = []
		self.historical_fixpoint = 0

		self.name = []
		self.symbols =[]


		self.profit = tk.DoubleVar(value=0)
		self.stop = tk.DoubleVar(value=0)

	def model_init(self):
		pass
	def model_early_load(self):
		pass
	def model_load_early_chart(self):
		pass
	def model_update(self):
		pass
	def get_ts(self):
		return self.ts 

	def get_pnl(self):
		return self.pnl 

	def get_long(self):
		return self.long 

	def get_short(self):
		return self.short*-1

	def get_long_symbols(self):

		return self.long_symbols 
	def get_short_symbols(self):


		return self.short_symbols 
	def get_early_ts(self):
		return self.e_ts 

	def get_early_pnl(self):
		return self.e_pnl 

	def model_today_data(self):
		pass 

	def get_spread(self):

		return str(round(self.spread,2))

	def get_price(self):

		return  str(round(self.cur,2))


class quick_model(model):

	def __init__(self,name,model,historical_plus,historical_minus):

		super().__init__()

		self.model_initialized = True 
		self.model = {}

		self.pnl = np.array([None for i in range(570,960)])
		self.ts  = np.array([i for i in range(570,960)])
		self.spread = 0
		self.e_pnl = []
		self.e_ts  = []
		self.cur = 0
		self.model_initialized = True 
		self.model_early_chart = False 

		self.name = "TNV_Model_" + name #"QFAANG"

		self.model =  model 
		self.model_initialized = True 

		self.historical_computed = True 
		self.historical_plus = historical_plus
		self.historical_minus = historical_minus
		self.historical_fixpoint = 0


		self.model_init()

	def model_init(self):

		if self.model_initialized and len(self.model)<10:

			self.long_symbols = ""
			c  =0
			for symbol,share in self.model.items():

				if share>0:
					self.long_symbols += (str(symbol)+":"+str(share)+",")
					c+=1
			self.long_symbols  = self.long_symbols[:-1]

			self.short_symbols = ""
			c  =0
			for symbol,share in self.model.items():

				if share<0:
					self.short_symbols   += (str(symbol)+":"+str(share)+",")
					c+=1
			self.short_symbols  = self.short_symbols[:-1]

	def model_early_load(self):

		if self.model_initialized :
			d = threading.Thread(target=self.model_load_early_chart,daemon=True)
			d.start() 
		else:
			print(" Model not Init.")
	def model_buy(self):

		try:
			now = datetime.now()
			ts = now.strftime("_%H:%M")
			cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_L"+ts+",Order=*"
			for symbol,share in self.model.items():
				cmdstr += symbol+":"+str(share)+","

			cmdstr= cmdstr[:-1]
			cmdstr+="*"


			cmdstr+="Infos=("
			if self.profit.get()>0:
				cmdstr+="Profit="+str(int(self.profit.get()))+","
			if self.stop.get()>0:	
				cmdstr+="Stop="+str(int(self.profit.get()))+","
			cmdstr+=")"
			print(cmdstr)
			requests.get(cmdstr)
		except Exception as e:
			PrintException(e)

	def model_sell(self):

		try:
			now = datetime.now()

			ts = now.strftime("_%H:%M")
			cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_S"+ts+",Order=*"
			for symbol,share in self.model.items():
				cmdstr += symbol+":"+str(share*-1)+","

			cmdstr= cmdstr[:-1]
			cmdstr+="*"

			cmdstr+="Infos=("
			if self.profit.get()>0:
				cmdstr+="Profit="+str(int(self.profit.get()))+","
			if self.stop.get()>0:	
				cmdstr+="Stop="+str(int(self.stop.get()))+","
			cmdstr+=")"
			print(cmdstr)
			requests.get(cmdstr)

		except Exception as e:
			PrintException(e)

	def model_load_early_chart(self):

		try:
			print("loading start")
			dic = {}

			now = datetime.now(tz=pytz.timezone('US/Eastern'))
			ts = now.hour*60 + now.minute

			for key in self.model.keys():
			  postbody = "https://financialmodelingprep.com/api/v3/historical-chart/1min/"+key[:-3]+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"
			  r= requests.get(postbody)
			  # print(r.text)

			  d = json.loads(r.text)
			  dic[key] = d 

			earlier_pnl = np.zeros((len(dic),ts-570+1))
			c = 0

			for symbol,share in self.model.items():

			  df = pd.DataFrame.from_dict(dic[symbol])

			  df['date']= pd.to_datetime(df['date']) 
			  df = df.loc[df['date']>pd.Timestamp(date.today())]
			  df['ts'] = df['date'].dt.hour*60 + df['date'].dt.minute-570

			  idx = df['ts'].tolist()[:ts-570]
			  p = df['open'].to_numpy()[:ts-570]

			  diff = p*share
			  earlier_pnl[c][idx] = diff
			  mask = earlier_pnl[c]==0

			  earlier_pnl[c][mask]= np.interp(np.flatnonzero(mask), np.flatnonzero(~mask),  earlier_pnl[c][~mask])

			  c+=1

			s = np.sum(earlier_pnl,axis=0)
			s = s - s[0]

			self.e_pnl = s
			self.e_ts  = [570+i for i in range(len(self.e_pnl))]

			self.model_early_chart = True 
			print("loading complete ")

		except Exception as e:
			PrintException(e)

	def model_update(self,data):

		try:
			c= 0
			self.long =0
			self.short = 0
			if self.model_initialized:
				spread = 0
				spreads = {}


				try:
					if self.historical_fixpoint==0:
						for key,share in self.model.items():
							key = key[:-3]
							self.historical_fixpoint +=  data[key]['day_open']*share

				except:
					pass 
				for key,share in self.model.items():

					key = key[:-3]
					
					if key in data:
						result = (data[key]['day_current'] - data[key]['day_open'])*share
						c+=result

						if share>0:
							self.long += result 
						else:
							self.short += result

						spread+= (data[key]['ask'] - data[key]['bid'])*abs(share)

						spreads[key]=((data[key]['ask'] - data[key]['bid'])*abs(share))
						#print(key,round( (data[key]['ask'] - data[key]['bid'])*abs(share),1))
					else:
						print("no",key)



				print({k: v for k, v in sorted(spreads.items(), key=lambda item: item[1])})
				
				#print(np.mean(spreads))
				now = datetime.now(tz=pytz.timezone('US/Eastern'))
				ts = now.hour*60 + now.minute
				idx = ts-570

				# before = np.where(self.pnl==None)[0]
				# self.pnl[before[before<idx]]=0

				if c!=0:
					self.pnl[idx] = c
					self.spread = spread
					self.cur = c
			else:
				print("require init model.")
				pass
				pass#self.model_init()
		except Exception as e:
			PrintException(self.name,e)

class obq_model(quick_model):
	def __init__(self):

		super().__init__("OBQ",{},[],[])

		self.model_initialized = False 

	def model_init(self):

		d = threading.Thread(target=self.create_standard_obq_df,daemon=True)
		d.start() 


	def create_standard_obq_df(self):


			# STEP 1 , obtain symbols.
		try:
			print("loading OBQ")
			postbody = "https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey=a901e6d3dd9c97c657d40a2701374d2a"
			r= requests.get(postbody)
			d = json.loads(r.text)
			symbols = [i['symbol'] for i in d]

			print("symbol count:",symbols.__len__())

			# step 2, get the df. 

			k = []
			c=0
			skips = []
			for symbol in symbols:

			  try:
			    postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=day&period=100&user=sajali26@hotmail.com&password=guupu4upu"
			    r= requests.post(postbody)

			    t_df = pd.read_csv(StringIO(r.text),names=["day","open","high","low","close","volume"])
			    t_df['day'] = pd.to_datetime(t_df['day'])
			    t_df[symbol+"_gain"] =  np.log(t_df["close"]) - np.log(t_df["open"])
			    t_df[symbol+"_gap"] =  np.log(t_df["open"]) - np.log(t_df.close.shift(1))
			    t_df[symbol+"_volume"] = t_df["volume"]
			 
			    t_df[symbol+"_std"] =0
			    t_df[symbol+"_current"] =0
			    t_df[symbol+"_ystd"] =0
			    t_df[symbol+"_ranking_norm"] =0
			    t_df[symbol+"_executing_norm"] =0
			    t_df[symbol+"_norm"] =0
			    
			    t_df.rename({'open': symbol+'_open', }, axis=1, inplace=True)
			    t_df.rename({'close': symbol+'_close', }, axis=1, inplace=True)

			    t_df = t_df.drop(["high","low","volume"],axis=1)

			    ####### EXCLUDE SYMBOL $500 and above ####

			    if t_df[symbol+"_open"].iloc[-1]>600:
			      skips.append(symbol)
			    else:
			      k.append(t_df)
			    c+=1
			  except Exception as e:
			    PrintException(symbol,e)

			df = reduce(lambda  left,right: pd.merge(left,right,on=['day'],how='outer'), k).fillna(0)
			print("actual:",k.__len__()," skipping:",skips)


			symbols = [x for x in symbols if x not in skips]



			### STEP 3 MODEL ####

			std_window1 = 50
			std_window2 = 25
			std_window3 = 5

			std1_weight= 0.2
			std2_weight= 0.2
			std3_weight= 0.6

			for symbol in symbols:
			  std1 = df[symbol+"_gain"].rolling(window=std_window1).std()
			  std2 = df[symbol+"_gain"].rolling(window=std_window2).std()
			  std3 = df[symbol+"_gain"].rolling(window=std_window3).std()

			  df[symbol+"_std"] = std1*std1_weight+ std2*std2_weight + std3*std3_weight

			  df[symbol+"_current"] = df[symbol+"_close"].shift(1)
			  df[symbol+"_ystd"] = df[symbol+"_std"].shift(1)

			  df[symbol+"_ystd"].replace(0, np.nan, inplace=True)

			  df[symbol+"_ranking_norm"] = df[symbol+"_gain"]/df[symbol+"_std"]
			  df[symbol+"_executing_norm"] = df[symbol+"_gain"]/df[symbol+"_ystd"]

			  df[symbol+"_norm"] = df[symbol+"_executing_norm"]

			# for symbol in symbols:
			#   print(symbol,df[symbol+"_std"].iloc[-1])


			### STEP 4 OUTPUT ###

			risk = 12 
			columns = [symbol+'_ranking_norm' for symbol in symbols]

			rename ={}
			for i in columns:
			  rename[i] = i[:-13]

			norm_df = df[columns].copy()
			rank_df =  df[columns].copy().rank(axis=1,method='min')
			rank_df.rename(rename, axis=1, inplace=True)
			predicted_rank = rank_df.shift(1)*0.7 + rank_df.shift(2)*0.3

			predicted_rank=predicted_rank.copy().rank(axis=1,method='min')
			top_x = 16

			selected={}
			val = (rank_df.iloc[-1]*0.7 + rank_df.iloc[-2]*0.3).rank(method='min')
			shorts = val.sort_values().iloc[:top_x].index
			longs =  val.sort_values().iloc[-top_x:].index


			selected['long_std'] = longs
			selected['long_open'] = longs +"_open"
			selected['short'] = shorts +"_std"

			l = {}
			s = {}
			t = {}
			for symbol in longs:
			  std = df.iloc[-1][symbol+"_std"]
			  share = int(int(round(risk/(std*df.iloc[-1][symbol+"_close"]),0)))
			  t[symbol+".NQ"] = share
			  symbol +=".NQ"

			  l[symbol] = share

			for symbol in shorts:
			  std = df.iloc[-1][symbol+"_std"]
			  share = -int(int(round(risk/(std*df.iloc[-1][symbol+"_close"]),0)))
			  t[symbol+".NQ"] = share
			  symbol +=".NQ"
			  s[symbol] = share

			self.model = t
			self.model_initialized = True 
			print("OBQ loading complete")

			super().model_init()
		except Exception as e:
			PrintException(e)



class nqg_model(quick_model):
	def __init__(self):

		super().__init__("OQG",{},[],[])

		self.model_initialized = False 

	def model_init(self):

		print("NQG LOADING START")
		d = threading.Thread(target=self.create_standard_obq_df,daemon=True)
		d.start() 


	def create_standard_obq_df(self):


			# STEP 1 , obtain symbols.
		try:
			postbody = "https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey=a901e6d3dd9c97c657d40a2701374d2a"
			r= requests.get(postbody)
			d = json.loads(r.text)
			symbols = [i['symbol'] for i in d]

			symbols.append("QQQ")

			anchord_symbol = 'QQQ'
			name = 'QQQ'
			

			### POLYGON PART ###
			r = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?include_otc=false&apiKey=ezY3uX1jsxve3yZIbw2IjbNi5X7uhp1H"

			r = requests.get(r)
			# print(r.text)

			d = json.loads(r.text)

			symbol_open = {}
			t={}
			for i in d['tickers']:
			  t[i['ticker']] = i
			  #symbol_open[i['ticker']] = [i['lastQuote']['P'],i['lastQuote']['P']]
			  symbol_open[i['ticker']] = [i['day']['o'],i['day']['c']]

			  #premarket
			  #t[i['ticker']] = i['lastTrade']['p']


			# DATA AND ALL #
			total = {}

			eval = ['/'+i for i in symbols]
			std =  ['s/'+i for i in symbols]
			norm =  ['n/'+i for i in symbols]

			t = []
			t.extend(eval)
			t.extend(std)
			t.extend(norm)
			skips = []
			black_list = ['GOOGL']

			print(len(symbols),symbols)
			for symbol in symbols[:]:

			  df = get_symbol_basket(symbol,'Day',50)
			  df.loc[len(df)] = ['Cur',symbol_open[symbol][0],symbol_open[symbol][0],symbol_open[symbol][0],symbol_open[symbol][1],0]
			  df = drop_columns(df,['Unnamed'])

			  df['symbol'] = symbol
			  df['anchord_ret'] =0
			  df['std_ret'] =0
			  df['result'] =0
			  df= pd.concat([df,pd.DataFrame(columns=t)])

			  # df=pd.concat([df,pd.DataFrame(columns=std)])
			  # df=pd.concat([df,pd.DataFrame(columns=norm)])

			  if df['open'].iloc[-1]>600 or symbol in black_list:
			    skips.append(symbol)
			  else:
			    total[symbol]=df

			symbols = [x for x in symbols if x not in skips]
			print("Total:",len(total),len(symbols),"skipping:",skips)

			#### AMEND THE DATA. if not presented.

			df = []

			for i in total.values():
			  if len(i)>len(df):
			    df = i

			days = df['day'].unique()

			for i in total.keys():
			  if len(total[i])!=len(days):
			    ndf = pd.DataFrame()
			    ndf['day'] = days
			    #ndf['symbol'] =  total[i]['symbol'].unique()[0]

			    total[i]  = ndf.merge(total[i], left_on='day', right_on='day',how='left')
			    total[i].loc[:,'symbol'] = i

			for i in total.values():

			  i['po'] = i['open'].shift(1)
			  i['pc'] = i['close'].shift(1)

			  i['log'] = np.log(i['open']) - np.log(i['pc'])
			  i['ret'] = np.log(i['close']) - np.log(i['open'])

			  # for j in symbols:
			  #   i['s/'+j] = 0
			  #   i['n/'+j] = 0

			all_logs = []

			for i in total.values():
			  l = i['log'].to_list()

			  all_logs.append(l)

			all_logs = np.array(all_logs)

			anchord_ret = total[anchord_symbol]['ret'].tolist()

			c=1
			for i in total.values():

			  r = i['log'].to_numpy() - all_logs

			  i['anchord_ret'] = i['ret'] - anchord_ret

			  for j in range(len(symbols)):
			    i[eval[j]] = r[j]

			  i['std_ret'] = i['ret'].rolling(30).std()
			  i['std_ret'] = i['std_ret'].shift(1)

			  i['result'] = i['ret']/i['std_ret']
			  for j in symbols:
			    i['s/'+j] = i['/'+j].rolling(30).std() #

			    i['n/'+j] = i['/'+j]/i['s/'+j] #

			  #print(i.shape,c)
			  c+=1
			  i.fillna(0)
			  i['strength'] = i[norm].sum(axis=1)/len(symbols)

			df = pd.concat(total.values())

			t = df.loc[df['day']=="Cur"].sort_values('strength',ascending=False)

			t['share'] = (20/(t['open']*t['std_ret'])).astype(int)

			print(t)
			output ={}
			for i,r in t.iloc[:10].iterrows():
			  symbol = r['symbol']+".NQ"
			  share = r['share']*-1
			  print(r['symbol'],r['share'],r['strength'])
			  #cmdstr1 += symbol+".NQ"+":"+str(share)+","

			  output[symbol]=share

			for i,r in t.iloc[-10:].iterrows():
			  symbol = r['symbol']+".NQ"
			  share = r['share']
			  print(r['symbol'],r['share'],r['strength'])
			  output[symbol]=share


			self.model = output
			self.model_initialized = True 
			print(self.name,":",self.model)

			super().model_init()
		except Exception as e:
			PrintException(e)
