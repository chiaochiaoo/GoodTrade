
from finviz.screener import Screener
import json
import pandas as pd


a = pd.read_csv('nasdaq.csv')

for i in a["Ticker"]:
	print(i)



# filters = ['exch_nyse','']  # Shows companies in NASDAQ which are in the S&P500
# signal = ''
# stock_list = Screener(filters=filters, table='Overview', signal=signal)  # Get the performance table and sort it by price ascending

# # print(stock_list[0].keys())
# l=[]

# label_list = ['Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Market Cap']

# for i in range(len(stock_list)):
# 	l.append([])
# 	for j in label_list:
# 		if j == 'Ticker':
# 			l[i].append(stock_list[i][j]+".NY")
# 		else:
# 			l[i].append(stock_list[i][j])

# #print(l)

# labels = ['Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Market Cap']
# d = pd.DataFrame(data=l,columns=labels)
# d.to_csv("nyse.csv")

#print(d)
# Export the screener results to .csv
#stock_list.to_csv("NASDAQ_stock.csv")

