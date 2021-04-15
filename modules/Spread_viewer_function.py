import pandas as pd
import numpy as np
from . import database as db
import json
import pandas as pd
from datetime import datetime
import requests


def SMA(lst,n):
	lst1= []
	if len(lst)>0:
		lst1.append(lst[0])
		for i in range(1,len(lst)):
			if i < n:
				lst1.append(mean(lst[:i+1]))
			else:
				lst1.append(mean(lst[i-n+1:i+1]))

		return np.array(lst1)
def mean(lst):
	return sum(lst)/len(lst)
def get_day(day_str):

	#09/28/2020
	m,d,y = day_str.split('/')

	return str(y)+str(m)+str(d)

def get_day_and_min(day_str,min_str):

	return int(get_day(day_str)+str(get_min(min_str)))

def get_min(time_str):
	"""Get Seconds from time."""
	h, m= time_str.split(':')
	#print(h,m)
	return int(h) * 60 + int(m)

def ts_to_str(timestamp):

	h= int(timestamp//60)
	m= int(timestamp%60)

	#chekc if they are 1 unit.

	if h//10 == 0:
		h = "0"+str(h)
	else:
		h = str(h)

	if m//10 == 0:
		m = "0"+str(m)
	else:
		m = str(m)

	return(h+":"+m)

def process_one(s):

	#STEP 1 . ADD timestamp.
	datehour = []
	timestamp = []
	for i in range(len(s)):
		timestamp.append(get_min(s["time"][i]))
		datehour.append(s["day"][i]+" "+s["time"][i])

	s.insert(2,"timestamp", timestamp, True)
	s.insert(2,"datehour", datehour, True)


	# STEP 1.1 Interpolate value.?  WORRY ABOUT THIS PART LATER.

	#1. Drop the first one before 9:30. 2. Drop the last one after 16:00.
	#Make up the missing values.


	#STEP 2. Add percentage counter.

	days = s.day.unique()

	for day in range(len(days)):
		#get the first value

		#print the first time 370.
		try:
			open_ = s.loc[s["datehour"]==(days[day] +" 09:30")]["open"].values[0]


			s.loc[(s["day"]==days[day])&(s["timestamp"]>=570),"open_"] = open_
			#tomorrow's, before 9:30.
			if day < len(days)-1:
				s.loc[(s["day"]==days[day+1])&(s["timestamp"]<570),"open_"] = open_
		except:
			print(days[day],"data corruption")

	percentage= []
	for i in range(len(s)):
		ratio = round((s["open"][i]-s["open_"][i])*100/s["open_"][i],4)
		percentage.append(ratio)


	s.insert(2,"change", percentage, True)

	#STEP 3. DROP not used colomn
	drop =["open_","high","low","close","volume"]

	s= s.dropna()

	return s.drop(drop,axis=1)

def process(S,Q):

	S = process_one(S)
	Q = process_one(Q)

	j = pd.merge(S,Q,on='datehour')

	pricegap = []
	for i in range(len(j)):
		pricegap.append(j["change_x"][i]-j["change_y"][i])

	j.insert(1,"price_gap", pricegap, True)

	return j.drop(["time_y","timestamp_y","day_y"],axis=1)

def sharp_change(pair,period,change_value):
	for i in range(period,len(pair)-1):
		if abs(pair[i] - pair[i-period])>change_value:
			return True

	return False

def change_distribution(pair,period):
    lst = []
    for i in (period,len(pair)-1):
        lst.append(pair[i] - pair[i-period])
    return lst

def change_min_max(pair):
    return (min(pair),max(pair))


def find_info(symbols):

	#Download the data.

	db.download(symbols,45,1)

	s= symbols

	x = s[0]
	y = s[1]

	s= pd.read_csv('data/'+x+'_45.txt',names=["day","time","open","high","low","close","volume"])
	q =pd.read_csv('data/'+y+'_45.txt',names=["day","time","open","high","low","close","volume"])
	p = process(s,q)

	days = p.day_x.unique()


	m_dis=[]
	for day in days:
		gap = p.loc[(p["day_x"]==day)]["price_gap"]
		if len(gap)>1:
			mi,ma=change_min_max(gap)
			m_dis.append(mi)
			m_dis.append(ma)

	w_dis=[]
	for day in days[-5:]:
		gap = p.loc[(p["day_x"]==day)]["price_gap"]
		if len(gap)>1:
			mi,ma=change_min_max(gap)
			w_dis.append(mi)
			w_dis.append(ma)

	roc1 = []
	for day in days:
		gap = p.loc[(p["day_x"]==day)]["price_gap"]
		if len(gap)>1:
			ls = change_distribution(gap.tolist(),1)
			mi,ma=change_min_max(ls)
			roc1.append(mi)
			roc1.append(ma)


	roc5 = []
	for day in days:
		gap = p.loc[(p["day_x"]==day)]["price_gap"]
		if len(gap)>1:
			ls = change_distribution(SMA(gap.tolist(),5),5)
			mi,ma=change_min_max(ls)
			roc5.append(mi)
			roc5.append(ma)


	roc15 = []
	for day in days:
		gap = p.loc[(p["day_x"]==day)]["price_gap"]
		if len(gap)>1:
			ls = change_distribution(SMA(gap.tolist(),15),15)
			mi,ma=change_min_max(ls)
			roc15.append(mi)
			roc15.append(ma)

	print("Distribution size:",len(m_dis))
	print(len(w_dis))
	print(len(roc1))
	print(len(roc5))
	print(len(roc15))

	return m_dis,w_dis,roc1,roc5,roc15

def fetch_data_yahoo(symbol):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-chart"

    querystring = {"region":"US","interval":"1m","symbol":symbol,"range":"1d"}

    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': "ecb76c89e1mshc1fe02b7259bd58p19ddf6jsnaad53d5c4ecb"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    res = json.loads(response.text)

    ts =[]
    for i in res['chart']['result'][0]['timestamp']:
        ts.append(datetime.fromtimestamp(i).strftime('%H:%M'))
        
    start = ts.index("09:30")
    
    op = res['chart']['result'][0]['indicators']['quote'][0]["open"][start:]
    ts = ts[start:]

    #clean the none type 

    for i in range(len(op)):
	    if op[i] ==None:
	        op[i] = op[i-1]
    
    #print(symbol+"missing data downloaded",ts,op)
    return ts,op

#find_info(["SPY.AM","QQQ.NQ"])
# symbols=["SPY.AM","QQQ.NQ"]
# m_dis,w_dis,roc1l,roc5l,roc15l = find_info(symbols)

# print(m_dis,"\n",w_dis,"\n",roc1l,"\n",roc5l,"\n",roc15l)

