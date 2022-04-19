
import threading
import pandas as pd
import time
#from datetime import datetime
import datetime
import requests
import numpy as np
import threading
#from pannel import *
#from modules.pannel import *



try:
	from scipy.stats import pearsonr
	#import numpy as np
except ImportError:
	import pip
	pip.main(['install', 'scipy'])
	from scipy.stats import pearsonr


try:
	import mplfinance as mpf
	#import numpy as np
except ImportError:
	import pip
	pip.main(['install', 'mplfinance'])
	import mplfinance as mpf




TRADETYPE = "Trade_type="
ALGOID ="Algo_id="
ALGONAME ="Algo_name="
SYMBOL = "Symbol="
ENTRYPLAN = "Entry_type="
SUPPORT = "Support="
RESISTANCE = "Resistance="
RISK =  "Risk="
SIDE =  "Side="
DEPLOY = "Deploy="
MANAGEMENT = "Management="


def request(req,symbol):
	try:
		r= requests.post(req)
		r= r.text

		if r[:3] == "404" or r[:3] =="405":
			print(symbol,"Not found")
			return ""
		else:
			return r

	except Exception as e:
		print(e)
		return ""

def ts_to_min(ts):
	ts = int(ts)
	m = ts//60
	s = ts%60

	return str(m)+":"+str(s)


def fetch_data_day(symbol1,symbol2):

    req = symbol.split(".")[0]
    i = symbol
    v= [38, 117, 115, 101, 114, 61, 115, 97, 106, 97, 108, 105, 50, 54, 64, 104, 111, 116, 109, 97, 105, 108, 46, 99, 111, 109, 38, 112, 97, 115, 115, 119, 111, 114, 100, 61, 103, 117, 117, 112, 117, 52, 117, 112, 117]

    postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=5&period="+str(day)+"&regularsession=1" +l(v)

    r= request(postbody, symbol)
    
    
    total = []
    keylevels = [{}]
    
    cur_date = []
    
    init = True
    x=[]
    le={}
    for i in r.splitlines():
        
        v  = i.split(",")
        
        if init==True:
            day = str(v[0])    
            init = False
            
        if day != str(v[0]):
            
            day = str(v[0])
            df = pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"],data=x)
            df["Date"] = pd.DatetimeIndex(df['Date'])
            df =df.set_index("Date")
            
            if len(total)>0:
                le["high"] = max(total[-1]["High"])
                le["low"] = min(total[-1]["Low"])
                keylevels.append(le)
                le={}
            total.append(df)

            x=[]
            
            
        t = [datetime.datetime.strptime(str(v[0])+" "+str(v[1]),'%m/%d/%Y %H:%M')]
        t.extend([float(i) for i in v[2:]])         
        x.append(t)
    
    df = pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"],data=x)
    df["Date"] = pd.DatetimeIndex(df['Date'])
    df =df.set_index("Date")

    if len(total)>0:
        le["high"] = max(total[-1]["High"])
        le["low"] = min(total[-1]["Low"])
        keylevels.append(le)
    total.append(df)

    return total,keylevels

def fetch_data_day_spread(symbol,interval,day):

	req = symbol.split(".")[0]
	i = symbol
	v= [38, 117, 115, 101, 114, 61, 115, 97, 106, 97, 108, 105, 50, 54, 64, 104, 111, 116, 109, 97, 105, 108, 46, 99, 111, 109, 38, 112, 97, 115, 115, 119, 111, 114, 100, 61, 103, 117, 117, 112, 117, 52, 117, 112, 117]

	postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval="+str(interval)+"&period="+str(day)+"&regularsession=1" +l(v)

	r= request(postbody, symbol)
	
	t=r
	with open("test.txt", "w",newline='') as text_file:
		text_file.write(t)
	#save to temp.txt
	
	return combine(r)

def pair_form_B(p,q):
	
	#take the join dates.

	d1 = p.keys()
	d2 = q.keys()
	
	dates = list(set(d1) & set(d2))#[0]
	
	dates = list(d1)#[:-1]
	#print(dates)
	
	ts = [i for i in range(570,960)]
	
	d = {}
	for day in dates:

		d[day]={}

		d[day]['p1'] = [0]
		d[day]['p2'] = [0]
		d[day]['rt'] = []
		
		p1_open=p[day]['opens'][0]
		p2_open=q[day]['opens'][0]
		p1=0
		p2=0
		for i in ts:
			#print(len(p[day]['opens']))
			if i in p[day]['ts']:
				
				idx = p[day]['ts'].index(i)
				p1 = abs( np.log(p[day]['opens'][idx])- np.log(p[day]['closes'][idx]))*100
				#print(p[day]['opens'][idx],p[day]['closes'][idx],p[day]['opens'][idx]-p[day]['closes'][idx],p1)
				
			if i in q[day]['ts']:
				
				idx = q[day]['ts'].index(i)
				p2 = abs( np.log(q[day]['opens'][idx])- np.log(q[day]['closes'][idx]))*100
				
			d[day]['p1'].append(p1)
			d[day]['p2'].append(p2)
			
			if p2!=0:
				d[day]['rt'].append(p1/p2)
			else:
				d[day]['rt'].append(0)
		
		d[day]['cor'] = pearsonr(d[day]['p1'], d[day]['p2'])[0]
		
	
	d[day]['p_price'] = p[day]['closes'][idx]
	d[day]['q_price'] = q[day]['closes'][idx]
	
	return d

def ratio_compute(a,b):
	a_=[]
	b_=[]
	turn = 0
	
	while True:
		if turn==0:
			a_.append(a)
			#print(a_)
		else:
			b_.append(b)
			#print(b_)

		#check differentce. who's losing, who's turn is it.
		ratio = (b*len(b_))/(a*len(a_))
		#print(ratio)
		if ratio>0.97 and ratio<1.03:
			break
		else:
			if ratio>1:
				turn=0
			else:
				turn=1

	return (len(a_),len(b_)),round(1-ratio,2)


def hedge(p,q,interval,days):
	
	u=fetch_data_day_spread(p,interval,days)
	d=fetch_data_day_spread(q,interval,days)

	#print(u)
	da = pair_form_B(u,d)
	
	total_rt = []
	days = list(da.keys())
	cors = []
	for k in days:
		total_rt.extend(da[k]['rt'])
		cors.append(da[k]['cor'])

	q75, q25 = np.percentile(total_rt, [75 ,25])
	
	total_rt = np.array(total_rt)
	
	new = np.mean(total_rt[np.where((total_rt>=q25) & (total_rt<=q75))])
	correlation = np.mean(np.array(cors))
	
	### WHERE I WANT TO OUTPUT. RT. and Correlations. 
	d = {}
	
	d["hedge_ratio"] = new
	d["correlation"] = correlation
	d["p_price"] = da[k]['p_price']
	d["q_price"] = da[k]['q_price']
	
	return d



def compute_volatility(p,q,ratio,correlation):
	
	p=fetch_data_day_spread(p,15,5)
	q=fetch_data_day_spread(q,15,5)
	
	pr = ratio[0]
	qr = ratio[1]
	
	d1 = p.keys()
	d2 = q.keys()
	dates = list(set(d1) & set(d2))#[0]
	dates = list(d1)
	
	ts = [i for i in range(570,960)]
	
	d = {}
	coefficient = 1
	
	if correlation>0:
		coefficient = 1
	else:
		coefficient = -1
	
	diff = []
	for day in dates:
		for i in ts:
			if i in p[day]['ts'] and i in q[day]['ts']:
				
				idx1 = p[day]['ts'].index(i)
				idx2 = p[day]['ts'].index(i)
				

				l = (p[day]['closes'][idx1] -p[day]['opens'][idx2])*pr
				s = coefficient*(q[day]['opens'][idx1] -q[day]['closes'][idx2]) *qr
				
				diff.append(abs(l+s))
				
	q75, q25 = np.percentile(diff, [75 ,25])
	diff = np.array(diff)
	new = round(np.mean(diff[np.where((diff>=q25) & (diff<=q75))]),2)
	
	return new
	
	
def hedge_ratio(p,q):
	
	x1 = hedge(p,q,5,5)
	x2 = hedge(p,q,10,5)
	x3 = hedge(p,q,15,5)

	p_price,q_price = x1["p_price"],x1["q_price"]
	lst = [x1,x2,x3]
	
	hedge_ratio = [i["hedge_ratio"] for i in lst]
	correlation = [i["correlation"] for i in lst]
	

	data = {}
	#data["hedgeratio"] = round(np.mean(hedge_ratio),2)
	#print(p_price,q_price)
	hedge_ratio = np.mean(hedge_ratio)
	#print(hedge_ratio)
	if hedge_ratio >=1:
		ratio,coverage = ratio_compute(p_price*hedge_ratio,q_price)
	else:
		ratio,coverage = ratio_compute(p_price,q_price*(1/hedge_ratio))
	data["hedgeratio"] = ratio
	data["coverage_imbalance"] = coverage
	## COMPUTE THE DIRECT RATIO
	
	
	data["hedgeratio_stability"] = round(1-(np.std(hedge_ratio)/np.mean(hedge_ratio)),2) #ACROSS MULTIPLE TIME FRAME
	
	data["correlation_score"] =   round(np.mean(correlation),2)  
	data["correlation_stability"] = round(1-(np.std(hedge_ratio)/np.mean(correlation)),2)
	   
	data["15M_expected_risk"] = compute_volatility(p,q,ratio,data["correlation_score"])
#     data["hedge_sigma"] = 

	return data

def l(v):
	z=[]
	for i in v:
		z.append(chr(i))

	return (''.join(map(str, z)))

def combine(f):

	#dic = {}

	symbol = f#file.split(".")[1][:-4]

	dic = {}

	all_dates = []
	magnitude = []
	volume = []

	#f = open(file+".txt",'r')
	lastdate=0

	for x in f.splitlines():

		lst=x.split(",")
		#print(x)
		date = lst[0]
		if date not in dic:
			dic[date] = {}
			dic[date]['symbol'] = symbol
			dic[date]['date'] = date

			dic[date]['open'] = 0
			dic[date]['close'] = 0

			dic[date]['pvolume'] = 0
			dic[date]['volume'] = 0
			dic[date]['magnitude'] = 0
			dic[date]['expected_magnitude'] = 0
			dic[date]['yrelv'] = 0

			dic[date]['ph'] = 0
			dic[date]['pl'] = 0

			#init_historical(dic[date])

			dic[date]["highs"]=[]
			dic[date]["lows"]=[]
			dic[date]["opens"]=[]
			dic[date]["closes"]=[]
			dic[date]["volumes"]=[]
			dic[date]["ts"]=[]


			all_dates.append(date)

		try:
			ts = get_min(lst[1])

		except Exception as e:
			print(e,x)
			break

		if ts>=570 and ts<=960:
			open_ =  float(lst[2])
			high = float(lst[3])
			low = float(lst[4])
			close_ =  float(lst[5])
			vol = int(lst[6])

			dic[date]["opens"].append(open_)
			dic[date]["closes"].append(close_)
			dic[date]["highs"].append(high)
			dic[date]["lows"].append(low)

			# dic[date]["highs"].append(max(dic[date]["highs"]))
			# dic[date]["lows"].append(min(dic[date]["lows"]))

			dic[date]["ts"].append(ts)
			# dic[date]["time"].append(lst[1])
			dic[date]["volumes"].append(vol)
			if ts>=570 and dic[date]['open']==0:
				dic[date]['open'] = open_
				#prev_close = dic[dic[date]['lastdate']]['close']

			if ts>=959 and ts<= 960:
				dic[date]['close'] = close_



	return dic

def get_min(time_str):
	"""Get Seconds from time."""

	h, m= time_str.split(':')

	ts = int(h) * 60 + int(m)

	return ts

if __name__ == '__main__':


	# symbol1 = "JETS.AM"
	# symbol2 = "SPY.AM"
	# print(hedge_ratio(symbol1,symbol2))


	d,k=fetch_data_day("USO",3)
	mpf.plot(d[0],type='candle',figscale=1.2)

	plt.show()