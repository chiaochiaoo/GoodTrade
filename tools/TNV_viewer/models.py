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
class model:

	def __init__(self):
		self.model_initialized = False 
		self.model = {}

		self.pnl = np.array([None for i in range(570,960)])
		self.ts  = np.array([i for i in range(570,960)])
		self.spread = 0
		self.e_pnl = []
		self.e_ts  = []

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

	def get_early_ts(self):
		return self.e_ts 

	def get_early_pnl(self):
		return self.e_pnl 

	def model_today_data(self):
		pass 

	def get_spread(self):

		return str(round(self.spread,2))

class obq_model(model):

	def __init__(self):
		self.model_initialized = False 
		self.model = {}

		self.pnl = np.array([None for i in range(570,960)])
		self.ts  = np.array([i for i in range(570,960)])
		self.spread = 0
		self.e_pnl = []
		self.e_ts  = []
		self.model_initialized = False 
		self.model_early_chart = False 

		self.name = "TEST_OBQ"

	def model_init(self):
		self.model =  {'JD': 53, 'ADP': 4, 'CSCO': 32, 'SGEN': 9, 'VRTX': 5, 'CTAS': 3, 'MU': 12, 'TSLA': 2, 'NFLX': 3, 'INTC': 23, 'WBA': 21, 'MRNA': 7, 'CSX': 39, 'AAPL': 6, 'PDD': 11, 'ATVI': 62, 'LULU': -3, 'TMUS': -11, 'MNST': -19, 'MDLZ': -31, 'DDOG': -6, 'CSGP': -18, 'RIVN': -15, 'ABNB': -5, 'ANSS': -3, 'EBAY': -20, 'AMGN': -5, 'SBUX': -17, 'ZS': -3, 'GFS': -12, 'ALGN': -2, 'CDNS': -4}
		self.model_initialized = True 
		self.model_early_chart = False 

	def model_early_load(self):

		d = threading.Thread(target=self.model_load_early_chart,daemon=True)
		d.start() 

	def model_buy(self):
		now = datetime.now(tz=pytz.timezone('US/Eastern'))
		ts = now.strftime("_%H:%M")
		cmdstr =  "https://tnv.ngrok.io/Basket="+self.name+"_L"+ts+",Order=*"
		for symbol,share in self.model.items():
			cmdstr += symbol+":"+str(share)+","

		cmdstr= cmdstr[:-1]
		cmdstr+="*"

		print(cmdstr)
		requests.get(cmdstr)
	def model_sell(self):
		now = datetime.now(tz=pytz.timezone('US/Eastern'))

		ts = now.strftime("_%H:%M")
		cmdstr =  "https://tnv.ngrok.io/Basket="+self.name+"_S"+ts+",Order=*"
		for symbol,share in self.model.items():
			cmdstr += symbol+":"+str(share*-1)+","

		cmdstr= cmdstr[:-1]
		cmdstr+="*"

		print(cmdstr)
		requests.get(cmdstr)

	def model_load_early_chart(self):
		print("loading start")
		dic = {}

		now = datetime.now(tz=pytz.timezone('US/Eastern'))
		ts = now.hour*60 + now.minute

		for key in self.model.keys():
		  postbody = "https://financialmodelingprep.com/api/v3/historical-chart/1min/"+key+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"
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



	def model_update(self,data):
		c= 0

		if self.model_initialized:
			spread = 0
			spreads = []
			for key,share in self.model.items():

				if key in data:
					c+=(data[key]['day_current'] - data[key]['day_open'])*share

					spread+= (data[key]['ask'] - data[key]['bid'])*abs(share)

					spreads.append((data[key]['ask'] - data[key]['bid'])*abs(share))
					#print(key,round( (data[key]['ask'] - data[key]['bid'])*abs(share),1))
				else:
					print("no",key)


			#print(np.mean(spreads))
			now = datetime.now(tz=pytz.timezone('US/Eastern'))
			ts = now.hour*60 + now.minute
			idx = ts-570

			# before = np.where(self.pnl==None)[0]
			# self.pnl[before[before<idx]]=0

			if c!=0:
				self.pnl[idx] = c
				self.spread = spread
		else:
			self.model_init()
