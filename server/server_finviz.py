import finviz
import pandas as pd


#### Update the info from the Finviz ####

a = pd.read_csv('nasdaq.csv', index_col=0)
a = a.set_index('Ticker')

#takes 10 minutes
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


get_data(a,a.index)

###### Update the info from PPRO. ##################





