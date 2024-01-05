from datetime import date
import pandas as pd
import numpy as np
import requests

from datetime import datetime
import pytz
import time
import pandas as pd

import threading
import json
try:
	from util_functions import *
	#from core_models import *
except:
	from core_server.util_functions import *
	#from core_server.core_models import *

import sys

if sys.version_info[0] < 3:
		from StringIO import StringIO
else:
		from io import StringIO

import os
import io
import warnings
#import StringIO
warnings.simplefilter('error', RuntimeWarning)


SERVER = "logs_server"
ALGO ="logs_algo"
MAIN_FRAME = "Main"

global market 
market = {}


pmr_timer = 900

def drop_columns(df,drops):

	drop = []
	for i in df.columns:
		for x in drops:
			if x in i:
				drop.append(i)

	return df.drop(drop, axis=1)

def create_market():

	global market 

	date_ = date.today().strftime("%Y-%m-%d")

	try:
		with open('market/'+date_+'.json') as json_file:
			market = json.load(json_file)
		return 1 
	except:
		pass

	postbody = "https://financialmodelingprep.com/api/v3/available-traded/list?apikey=a901e6d3dd9c97c657d40a2701374d2a"
	r= requests.get(postbody)
	# print(r.text)

	d = json.loads(r.text)

	# d
	check = {}
	check["NYSE"] = ".NY"
	check["NASDAQ"] = ".NQ"
	check["AMEX"] =  ".AM"

	total = {}
	total[".AM"] = []
	total[".NQ"] = []
	total[".NY"] = []

	for i in d:
		if i['exchangeShortName'] in check:
			total[check[i['exchangeShortName']]].append(i['symbol'])

	# Directly from dictionary
	with open('market/'+date_+'.json', 'w') as outfile:
			json.dump(total, outfile)

	market = total 

	# read  ##########################################################################################################

def create_database_model(symbol,folder_path):


	### check if it's there.

	try:
		# Open and read the JSON file
		with open(folder_path+'/'+symbol+'.json', 'r') as file:
				data = json.load(file)

		return data
	except:
		pass

	try_attemp = 0
	while try_attemp<3:

		try:

			postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval="+str(1)+"&period="+str(10)+"&regular=0&user=sajali26@hotmail.com&password=guupu4upu"

			r= requests.post(postbody)
			df  = pd.read_csv(StringIO(r.text),names=["day","time","open","high","low","close","volume"])

			df['ts'] = df['day'] + ' '+df['time']
			df['ts'] = pd.to_datetime(df['ts'])
			df['day'] = df['ts'].dt.strftime('%Y-%m-%d')

			df['ts'] = df['ts'].dt.hour*60+df['ts'].dt.minute
			days = df['day'].unique()

			for day in days:
				slice_ = df.loc[df['day']==day]
				df.loc[df['day']==day,'day_high'] = slice_['high'].max()
				df.loc[df['day']==day,'day_low'] = slice_['low'].min()

				df.loc[df['day']==day,'day_open'] = slice_['open'].iloc[0]
				df.loc[df['day']==day,'day_close'] = slice_['close'].iloc[-1]

			df['range'] = ( df['open']-df['day_low']) / ( df['day_high']-df['day_low'])
			df['log_return'] = np.log(df['close']) - np.log(df['open'])

			d = df.loc[(df["ts"]>590)&(df["ts"]<950)]

			avg_gain = d["log_return"].dropna().abs().mean()
			avg_vol = d["volume"].dropna().mean()

			d = d.groupby('day').first()

			atr1 = (d['day_close'] - d['day_open']).abs().mean()
			atr2 = (d['day_high'] - d['day_low']).mean()
			atr = (atr1+atr2)/2

			d= {}

			d['symbol'] = symbol
			d['average_gain_1m'] = avg_gain
			d['average_volume_1m'] = avg_vol 
			d['atr'] = atr 
			d['db_processed'] = 1


			h,l = grab_pmb_hl(symbol)

			d['pm_high'] = h
			d['pm_low'] = l


			print(symbol,d)
			with open(folder_path+'/'+symbol+'.json', 'w') as file:
				json.dump(d, file)

			return d
		except Exception as e:
			try_attemp+=1
			PrintException(SERVER,symbol,symbol+"CANNOT PROCESS")

	d= {}

	d['symbol'] = symbol
	d['average_gain_1m'] = 0
	d['average_volume_1m'] = 0 
	d['atr'] = 0 
	d['db_processed'] = 0

	return d

def symbol_duplicate_check(server,symbols):

	#### check if there's file. if not create. 

	date_ = date.today().strftime("%Y-%m-%d")

	try:
		with open('symbols/'+date_+'.json') as json_file:
			total = json.load(json_file)
	except:
		total = {}
		print("File not located")

	total[server] = []
	total_existed = [item for sublist in list(total.values()) for item in sublist]

	selected = []


	skips = []
	# for symbol in symbols:
	# 	if symbol not in total_existed:
	# 		total[server].append(symbol)
	# 	else:
	# 		skips.append(symbol)

	# with open('symbols/'+date_+'.json', 'w') as outfile:
	# 		json.dump(total, outfile)


	return total[server],skips


def init_asset_server(name,symbols):

	global market

	today = date.today()

	keys = ['symbol','ts','day_open','day_current','day_high','day_low','day_volume','pm_high','pm_low','pm_range']

	keys.extend(['log_gain','vol_gain','minute_open','minute_close','minute_high','minute_low','minute_volume','minute_update'])
	keys.extend(['db_processed','relv','average_gain_1m','average_volume_1m','atr'])
	keys.extend(['side','gain_signal','vol_signal','final_combine','combined_signal'])
	#df = pd.DataFrame(columns=keys)
	block_list = ['BKNG','FISV','MELI','BKR.B','BF-A','BF-B']

	total = []

	for symbol in symbols:
		for ts in range(510,961):
			t = [symbol,ts]
			t.extend([0 for i in range(len(keys)-2)])
			total.append(t)

	df = pd.DataFrame(columns=keys,data=total)

	### PROBLEM : takes forever to create a df.

	ret = ''

	c=0

	today = date.today()

	folder_path = "asset_servers/assets/"+name
	isExist = os.path.exists(folder_path)
	if not isExist:
	 # Create a new directory because it does not exist
		os.makedirs(folder_path)

	filename = folder_path+'/'+name+"_"+today.strftime("%Y-%m-%d")+'.csv'

	try:
		df.to_csv(filename)
	except:
		pass

	log_print(SERVER,name,"asset server updated")
	return df


def server_program(servers):

	### SINCE THIS MAY BE A SUBSERVER. SO. USE Different file for CSV.
	### BUT SAME LOG , name everywhere else.


	# servers: [ {}]
	# i['server_name']
	# i['df'] 
	# i['symbols']
	# i['algos'] 
	# {server name :[symbols],[algos]} 

	global market 

	reset = True 
	cur_ts = 0
	cur_day = ""
	lts = 0
	while True:
		now = datetime.now(tz=pytz.timezone('US/Eastern'))
		ts = now.hour*60 + now.minute
		today = date.today()
		

		if ts>500 and today!=cur_day: ###

			create_market()

			log_print(SERVER,MAIN_FRAME,"new day detected,",today)


			valid = []
			for i in market.values():
				valid.extend(i)

			for server in servers:

				### CHECK FOR VALID SYMBOLS
				valid_symbols = []

				server_name = server['server_name']

				for symbol in server['symbols']:
					if symbol in valid:
						valid_symbols.append(symbol)

				############################## DUPLICATES CHECK  ##############################################
				#valid_symbols,skips = symbol_duplicate_check(server_name,valid_symbols)
				skips = []
				server['symbols'] = valid_symbols

				log_print(SERVER,MAIN_FRAME,server_name,"Symbols Skipping:",skips,"total symbol count:",len(valid_symbols))
			###############################################################################################

				# try:

				# 	file_path = "asset_servers/assets/"+server_name+'/'+server_name+"_"+today.strftime("%Y-%m-%d")+'.csv'
				# 	df = pd.read_csv(file_path)
				# 	# if not override:
				# 	#   df = pd.read_csv(file_path)
				# 	# else:
				# 	#   df = init_asset_server(file_name,valid_symbols)

				# except Exception as e:
				# 	log_print(SERVER,MAIN_FRAME,server_name,"init new file")

				# 	try:
				# 		df = init_asset_server(server_name,valid_symbols)
				# 	except Exception as e:
				# 		PrintException(SERVER,server_name,"df init error",e)

				df = init_asset_server(server_name,valid_symbols)

				print(df)
				df = drop_columns(df,['Unnamed'])

				log_print(SERVER,server_name,server_name,"df refreshed,",today)

				db = threading.Thread(target=database_program, args=(server_name,df,valid_symbols),daemon=True)
				db.start()
				
				symbols=''
				df['suffix'] = ""
				for i in valid_symbols:
					symbols+=str(i)
					symbols+=','

					added = False 
					for key,val in market.items():
						if i in val:

							df.loc[df['symbol']==i,'suffix'] = key 

				symbols=symbols[:-1]
				log_print(SERVER,MAIN_FRAME,server_name,"model updated on ",today,symbols)
				cur_day = today


				server['df'] = df 
				server['file_path'] = ""


		if ts>=500 and ts<=960:
			try:

				process = False 
				
				#log_print(SERVER,MAIN_FRAME, "processing ",ts)

				r = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?include_otc=false&apiKey=ezY3uX1jsxve3yZIbw2IjbNi5X7uhp1H"

				r = requests.get(r)
				# print(r.text)

				d = json.loads(r.text)

				last_min_stamp = []

				for i in d['tickers']:
					last_min_stamp.append(i['min']['t']//1000)

				cur_ts = max(last_min_stamp)

				if lts!=cur_ts:
					lts = cur_ts
					process = True 
					
				### MAKE SURE IT IS A NEW. 

			except Exception as e :
				PrintException(SERVER,MAIN_FRAME,e)

			if process: 

				### BUILD A DICTIONARY. 

				dic ={}

				a = cur_ts - 3600*5
				mts  =a%(3600*24)//3600*60 + a%(3600)//60

				for i in d['tickers']:

					dic[i['ticker']] = {}

					dic[i['ticker']]['ts'] = mts 
					dic[i['ticker']]['day_open'] = i['day']['o'] 
					dic[i['ticker']]['day_current'] = i['day']['c'] 
					dic[i['ticker']]['day_high'] = i['day']['h'] 
					dic[i['ticker']]['day_low'] = i['day']['l'] 
					dic[i['ticker']]['day_volume'] = i['day']['v'] 

					dic[i['ticker']]['minute_open'] = i['min']['o'] 
					dic[i['ticker']]['minute_close'] = i['min']['c'] 
					dic[i['ticker']]['minute_high'] = i['min']['h'] 
					dic[i['ticker']]['minute_low'] = i['min']['l']
					dic[i['ticker']]['minute_volume'] = i['min']['v']

					if i['min']['t']//1000==cur_ts:
						dic[i['ticker']]['minute_update'] = True 
					else:
						dic[i['ticker']]['minute_update'] = False 


				for server in servers:
					try:
						df = server['df']
						server_name = server['server_name']
						# obtain the right slice. 

						slice_ = df.loc[df['ts']==mts]['symbol']

						l = len(slice_)
						index = slice_.index
						val = list(slice_.values)

						day_open = [0 for i in range(l)]
						day_current = [0 for i in range(l)]
						day_high = [0 for i in range(l)]
						day_low = [0 for i in range(l)]
						day_volume = [0 for i in range(l)]
						minute_open = [0 for i in range(l)]
						minute_close = [0 for i in range(l)]
						minute_high = [0 for i in range(l)]
						minute_low = [0 for i in range(l)]
						minute_volume = [0 for i in range(l)]

						d = {}
						c = 0
						for i in val:
							d[i] = c
							c+=1

						for i in d.keys():
							symbol = i

							#print(symbol,d[symbol],d[symbol] in day_open,symbol in dic,dic.keys())

							if symbol in dic:
								day_open[d[symbol]] = dic[symbol]['day_open'] 
								day_current[d[symbol]] = dic[symbol]['day_current'] 
								day_high[d[symbol]] = dic[symbol]['day_high']  
								day_low[d[symbol]] = dic[symbol]['day_low'] 
								day_volume[d[symbol]] = dic[symbol]['day_volume'] 

								minute_open[d[symbol]] = dic[symbol]['minute_open']
								minute_close[d[symbol]] = dic[symbol]['minute_close']
								minute_high[d[symbol]] = dic[symbol]['minute_high'] 
								minute_low[d[symbol]] = dic[symbol]['minute_low'] 
								minute_volume[d[symbol]] = dic[symbol]['minute_volume'] 
							else:
								day_open[d[symbol]] = 0
								day_current[d[symbol]] = 0
								day_high[d[symbol]] = 0
								day_low[d[symbol]] = 0
								day_volume[d[symbol]] = 0

								minute_open[d[symbol]] = 0
								minute_close[d[symbol]] = 0
								minute_high[d[symbol]] = 0
								minute_low[d[symbol]] = 0
								minute_volume[d[symbol]] = 0

						#print(vol_)
						df.loc[index,'day_open'] = day_open 
						df.loc[index,'day_current'] = day_current
						df.loc[index,'day_high'] = day_high
						df.loc[index,'day_low'] = day_low
						df.loc[index,'day_volume'] = day_volume
						df.loc[index,'minute_open'] = minute_open
						df.loc[index,'minute_close'] = minute_close
						df.loc[index,'minute_high'] = minute_high
						df.loc[index,'minute_low'] = minute_low
						df.loc[index,'minute_volume'] = minute_volume

						if mts<pmr_timer:

							# df.loc[index,'pm_high'] = day_high 
							# df.loc[index,'pm_low'] = day_low
							df.loc[index,'pm_range'] = (df.loc[index,'minute_close']-df.loc[index,'pm_low'])/(df.loc[index,'pm_high'] -df.loc[index,'pm_low'])

						try:
							# VOL GAIN
							all_last_minute = df.loc[(df['ts']==mts-1)&(df['day_volume']!=0)].index

							df.loc[all_last_minute+1,'vol_gain'] =  df.loc[all_last_minute+1]['day_volume'].to_numpy() - df.loc[all_last_minute]['day_volume'].to_numpy()

							#LOG GAIN
							all_last_minute_valid = df.loc[(df['ts']==mts)&(df['minute_close']!=0)&(df['minute_open']!=0)].index
							df.loc[all_last_minute_valid,'log_gain'] = np.abs(np.log(df.loc[all_last_minute_valid]['minute_close'].to_numpy()) - np.log(df.loc[all_last_minute_valid]['minute_open'].to_numpy()))

							all_last_minute = df.loc[df['ts']==mts].index
			
							df.loc[all_last_minute,'side'] = 1
							df.loc[(df['ts']==mts)&(df.loc[all_last_minute]['minute_open']>df.loc[all_last_minute]['minute_close']),'side'] = -1

							# GAIN SIGNAL
							all_last_minute_valid = df.loc[(df['ts']==mts)&(df['log_gain']!=0)&(df['average_gain_1m']!=0)].index
							df.loc[all_last_minute_valid,'gain_signal'] = np.log(df.loc[all_last_minute_valid]['log_gain']/df.loc[all_last_minute_valid]['average_gain_1m'])

							# VOL SIGNAL
							all_last_minute_valid = df.loc[(df['ts']==mts)&(df['vol_gain']>0)&(df['average_volume_1m']!=0)].index

							df.loc[all_last_minute_valid,'vol_signal'] = np.log(df.loc[all_last_minute_valid]['vol_gain']/df.loc[all_last_minute_valid]['average_volume_1m'])

							# FINAL COMBINE SIGNAL
							df.loc[all_last_minute,'combined_signal'] = df.loc[all_last_minute]['gain_signal'] + df.loc[all_last_minute]['vol_signal'] #df['vol_signal']
						except Exception as e:
							PrintException(SERVER,MAIN_FRAME,server_name,"PROCESSING ERROR:",e)

						df['combined_signal_p1'] = df['combined_signal'].shift(1)
						df['combined_signal_p2'] = df['combined_signal'].shift(2)
						df['combined_signal_p3'] = df['combined_signal'].shift(3)
						df['combined_signal_p4'] = df['combined_signal'].shift(4)
						df['combined_signal_p5'] = df['combined_signal'].shift(5)


						### HWO DO I TAKE THE LAST 5? HM 
						df.loc[df['combined_signal']<0,'combined_signal'] = 0

						df['final_combine']  = df['combined_signal'] - (df['combined_signal_p1']*0.4+df['combined_signal_p2']*0.3+df['combined_signal_p3']*0.2+df['combined_signal_p4']*0.2+df['combined_signal_p5']*0.2)

						df.replace([np.inf, -np.inf], 0, inplace=True)

						#df.to_csv(server['file_path'])

						log_print(SERVER,MAIN_FRAME,server_name,'updated at ',mts)

						# for algo in server['algos']:
						# 	algo(server['df'],server['server_name'],mts)


						filter_ = df.loc[(df['day_volume']>800000)&(df['ts']==mts)&(df['final_combine']>3)&(df['gain_signal']>1)]
						log_print(SERVER,MAIN_FRAME,'updated at \n',filter_.sort_values(by=['final_combine'], ascending=False)[['symbol','suffix','final_combine','gain_signal','vol_signal','side','minute_open','minute_close']].iloc[:10].to_string())

						cur_ = df.loc[df['ts']==mts]
						if mts<pmr_timer:

							log_print(SERVER,MAIN_FRAME,df.loc[index].to_string())
							log_print(SERVER,MAIN_FRAME,"PMB top range:",cur_.sort_values(by=['final_combine'], ascending=False)[['symbol','suffix','pm_range','pm_high','pm_low','minute_open','minute_close']].iloc[:10].to_string())
							log_print(SERVER,MAIN_FRAME,"PMB bot range:",cur_.sort_values(by=['final_combine'], ascending=True)[['symbol','suffix','pm_range','pm_high','pm_low','minute_open','minute_close']].iloc[:10].to_string())
					except Exception as e:
						PrintException(SERVER,MAIN_FRAME,server_name,["Caculation error:",e,mts])

					log_print(SERVER,MAIN_FRAME,'All servers updated at ',mts)
			
			# else:
			# 	log_print(SERVER,MAIN_FRAME,"WAIT.",ts)
		else:
			time.sleep(1)

def grab_pmb_hl(symbol):
  today = date.today()
  # print("Today's date:", today)

  r = "https://api.polygon.io/v2/aggs/ticker/"+symbol+"/range/1/hour/"+str(today)+"/"+str(today)+"?adjusted=true&sort=asc&limit=2000&apiKey=ezY3uX1jsxve3yZIbw2IjbNi5X7uhp1H"

  r = requests.get(r)
  # print(r.text)

  d = json.loads(r.text)

  try:
	  h = d['results'][-1]['h']
	  l = d['results'][-1]['l']
	  for i in d['results'][-4:]:
	    if i['h'] > h:
	      h = i['h']
	    if i['l'] < l:
	      l = i['l']
  except:
  	print(r.text)
  	h,l =0,0
  return h,l

def database_program(name,df,symbols):

	today = date.today()

	folder_path = "database/"+today.strftime("%Y-%m-%d")
	isExist = os.path.exists(folder_path)


	#symbols = list(df['symbol'].unique())

	if not isExist:
	 # Create a new directory because it does not exist
		os.makedirs(folder_path)

	#filename = folder_path+'/'+today.strftime("%Y-%m-%d")+'.csv'


	#database
	c = 0
	for symbol in symbols:
		try:

			### CAN THREAD ###
			if df.loc[(df['symbol']==symbol)&(df['ts']==570)]['db_processed'].values[0]==0:

				log_print(SERVER,name,"Database:",symbol,c,"/",len(symbols))
				d = create_database_model(symbol,folder_path)


				print("!!!!!!!!!!!!!!!!!!!!",d)
				for key,val in d.items():
					df.loc[df['symbol']==d['symbol'],key] = val

				if d['db_processed']==0:
					log_print(SERVER,name," NO DATA:",symbol)
			# else:
			#   log_print(SERVER,name,"skipping",symbol)
			c+=1
			if c%10==0:
				log_print(SERVER,name,c)
		except Exception as e:
			PrintException(SERVER,name,[e,symbol])

	log_print(SERVER,name,name,"DB program completed:",len(symbols))

	#### get the df ####
	#### create folders. ###

symbols = []

#symbols = ["AAPL"]
postbody = "https://financialmodelingprep.com/api/v3/sp500_constituent?apikey=a901e6d3dd9c97c657d40a2701374d2a"
r= requests.get(postbody)
d = json.loads(r.text)
for i in d:
  symbols.append(i['symbol'])

total = {}
total['server_name'] = "Server"
total['symbols']  = symbols

total['algos'] = []



for s in symbols:

	print(s,grab_pmb_hl(s))


#total['symbols'] =["SPY","QQQ","AAPL"]
print(total["symbols"])
servers= [total]

server_program(servers)

