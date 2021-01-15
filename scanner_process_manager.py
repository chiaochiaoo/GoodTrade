import threading
import multiprocessing
import time
import re
import pip

try:
    from finviz.screener import Screener
except ImportError:
    pip.main(['install', 'finviz'])
    from finviz.screener import Screener

try:
    from bs4 import BeautifulSoup
except ImportError:
    pip.main(['install', 'BeautifulSoup4'])
    from bs4 import BeautifulSoup

try:
    from selenium import webdriver
except ImportError:
    pip.main(['install', 'selenium'])
    from selenium import webdriver
# A mini thread of the main thread. 
# Sleep normally.


class scanner_process_manager:
	def __init__(self,request_pipe):
		#if a downloading request is already sent. 
		self.downloading = False
		self.downloading2 = False
		self.request = request_pipe
		self.pannel = None

	def set_pannel(self,scanner_pannel):
		self.pannel = scanner_pannel


	def adding_comlete(self):
		self.downloading = False

	def updating_comlete(self):
		self.downloading2 = False

	def send_request(self,cond,market_,type_,cap):
		if(self.downloading == True):
			self.pannel.status_change("Downloading in progress")
			#print("Already downloading")
		else:
			self.downloading = True
			self.pannel.status_change("Downloading in progress")
			self.request.send(["f",cond,market_,type_,cap])
			#when success, put it False. ... Put on a thread to receive it.
			#HERE,.... seperate a thread to run it.
			receive = threading.Thread(name="Reiceive info",target=self.receive_request, daemon=True)
			receive.start()

	def refresh_nasdaq_trader(self):

		if(self.downloading2 == True):
			self.pannel.status_nasdaqchange("Updating in progress")

		else:
			self.downloading2 = True
			self.request.send(["n"])

			receive = threading.Thread(name="Reiceive info",target=self.receive_request, daemon=True)
			receive.start()


	def receive_request(self):
		d = self.request.recv()

		#print(d)
		#check if it is normal type?
		if d[0]=="Nasdaq":
			self.pannel.add_nasdaq_labels(d)
		else:
			self.pannel.add_labels(d)

def multi_processing_scanner(pipe_receive):

	sucess = False

	while not sucess:

		try:
			PATH = "./network/chromedriver.exe"
			driver = webdriver.Chrome(PATH)
			driver.get('http://www.nasdaqtrader.com/')
			# driver.find_element_by_id('tab4').click()
			# time.sleep(1)
			# driver.find_element_by_id('ahButton').click()
			time.sleep(1)
			sucess= True
			print("Database online")
		except:
			#self.pannel.status_nasdaqchange("Problem accessing server")
			sucess= False

	#self.pannel.status_nasdaqchange("Ready")

	while True:
		receive_things = pipe_receive.recv()

		order_type = receive_things[0]

		if order_type == "f":
			#unpack.
			cond, market_, type_, cap = receive_things[1],receive_things[2],receive_things[3],receive_things[4]

			print(cond, market_, type_, cap)
			d = refreshstocks(cond, market_, type_, cap)
			#send back.
			pipe_receive.send(d)

		elif order_type =="n":
			driver.find_element_by_id('tab4').click()
			time.sleep(1)
			driver.find_element_by_id('ahButton').click()
			time.sleep(1)
			sucess = False

			while not sucess:
				try:
					soup = BeautifulSoup(driver.page_source, 'html.parser')

					t = soup.find(text=re.compile('Last updated*'))

					data = []
					table = soup.find('div', attrs={'id':'asGrid'})

					try:

						table = table.find('div')
						table_body = table.findAll('tbody')[1]

						for i in table_body.findAll('tr'):
						    col =i.find_all('td')
						    cols = [ele.text.strip() for ele in col]
						    data.append(cols)
					except:
						data = []

					data2 = []

					try:
						table = soup.find('div', attrs={'id':'ahGrid'})

						table = table.find('div')
						table_body = table.findAll('tbody')[1]

						for i in table_body.findAll('tr'):
						    col =i.find_all('td')
						    cols = [ele.text.strip() for ele in col]
						    data2.append(cols)
					except:
						data2 = []

					pipe_receive.send(["Nasdaq",data,data2,str(t)])
					#self.pannel.status_nasdaqchange("Fetching complete")
					sucess= True
				except:
					#self.pannel.status_nasdaqchange("Problem fetching data")
					sucess = False



def refreshstocks(cond,market_,type_,cap):

	market = ''
	cond2 = ''
	signal = ''

	if market_ == 'Nasdaq':
		market = 'exch_nasd'

	elif market_ =='NYSE':
		market = 'exch_nyse'

	elif market_ =='AMEX':
		market = 'exch_amex'

	if type_ == 'Most Active':
		signal = 'ta_mostactive'

	elif type_ =='Top Gainner':
		signal = 'ta_topgainers'

	elif type_ =='New Highs':
		signal = 'ta_newhigh'

	elif type_ =='Unusual Volume':
		signal = 'ta_unusualvolume'


	if cap =='Any':
		cond2 = ''
	elif cap == 'Mega':
		cond2 = 'cap_mega'
	elif cap =='Large':
		cond2 = 'cap_large'
	elif cap == 'Mid':
		cond2 = 'cap_mid'
	elif cap =='Small':
		cond2 = 'cap_small'
	elif cap =='Large+':
		cond2 = 'cap_largeover'
	elif cap =='Mid+':
		cond2 = 'cap_midover'
	elif cap =='Small+':
		cond2 = 'cap_smallover'

	#self.markcap.set('Any') 

	filters = [market,cond,cond2]  # Shows companies in NASDAQ which are in the S&P500

	print(filters)

	try:
		stock_list = Screener(filters=filters, table='Performance', signal=signal)  # Get the performance table and sort it by price ascending
	except:
		return []

	print(len(stock_list))

	return list(stock_list)

	# pannel.add_labels(stock_list)

	# pannel.status.set("Download compelted")
	# pannel.downloading = False
	# print("Scanner download complete")



#main part.

# if __name__ == '__main__':

# 	multiprocessing.freeze_support()
# 	request_pipe, receive_pipe = multiprocessing.Pipe()
# 	p = multiprocessing.Process(target=multi_processing_scanner, args=(receive_pipe,),daemon=True)
# 	p.daemon=True
# 	p.start()

# 	t = scanner_process_manager(None,request_pipe)
# 	t.send_request()

# 	while True:
# 		a = 1
# 		