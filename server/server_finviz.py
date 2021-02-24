import finviz
import pandas as pd
from finviz.screener import Screener
import time
import requests
#### Update the info from the Finviz ####

# a = pd.read_csv('nasdaq.csv', index_col=0)
# a = a.set_index('Ticker')

#takes 10 minutes. at least it works. 

def market_cap_identify(i):
    
    if i == '-' : return 0
    
    else:
        cap = i[-1]
        num = float(i[:-1])
        #print(cap,num)
        if cap =='B':
            if num >=10: return 4
            else:  return 3
        elif cap =='M':
            if num>1000:return 3
            if num<1000 and num>250:return 2
            if num<250:return 1
        else:
            print("Need help")

#Run at 6 PM? 
def update_data(pd,symbols):

	count=0
	not_found = []
	for i in symbols:
		try:
			a=finviz.get_stock(i)
			pd.loc[i,'ATR'] = a["ATR"]
			pd.loc[i,'Prev Close'] = a["Prev Close"]
			pd.loc[i,'Market Cap'] = market_cap_identify(a['Market Cap'])
			count+=1
			print("Process",count)
		except Exception as e:
			not_found.append(i)
			
	print("Not found:",not_found)
	pd.to_csv("test_update.csv") 
	print("saved")


#no go.
def update_data_batch():

	filters = ['exch_nasd']  # Shows companies in NASDAQ which are in the S&P500

	#stock_list = Screener(filters=filters, table='Custom',custom=['1','49','64'])  # Get the performance table and sort it by price ascending
	stock_list = Screener(filters=filters, table='Performance',signal='',order='')  # Get the performance table and sort it by price ascending
	time.sleep(5)
	#print(len(stock_list))
	print(stock_list)

	#stock_list.to_csv("testtest.csv")

# get_data(a,a.index)

#update_data()
###### Update the info from PPRO. ##################

a = pd.read_csv('nasdaq_ppro_live - nasdaq_ppro_live.csv', index_col=0)
#a = a.set_index('Ticker')


update_data(a,a.index)
while True:
	a=1
###################################



