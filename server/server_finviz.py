import finviz
import pandas as pd
from finviz.screener import Screener
import time
import requests
#### Update the info from the Finviz ####

# a = pd.read_csv('nasdaq.csv', index_col=0)
# a = a.set_index('Ticker')

#takes 10 minutes. at least it works. 

#Run at 6 PM? 
def update_data(pd,symbols):

	count=0
	not_found = []
	for i in symbols:
		try:
			a=finviz.get_stock(i)
			pd.loc[i,'ATR'] = a["ATR"]
			pd.loc[i,'Prev Close'] = a["Prev Close"]
			count+=1
			print("Process",count)

		except Exception as e:
			not_found.append(i)
			
	print("Not found:",not_found)
	pd.to_csv("test.csv") 


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




###################################

a = pd.read_csv('nasdaq_ppro_live - nasdaq_ppro_live.csv', index_col=0)

ticks = a.index

for i in ticks:
	try:
		p="http://localhost:8080/Register?symbol="+i+".NQ&feedtype=L1"
		c= requests.get(p,timeout=0.01)
		print(i,"Good")
	except:
		try:
			print(i,"no good try again")
			c= requests.get(p,timeout=0.05)
			print(i,"good now")
		except:
			print("still no good")






