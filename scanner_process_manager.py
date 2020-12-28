import threading
import multiprocessing

try:
    from finviz.screener import Screener
except ImportError:
    pip.main(['install', 'finviz'])
    from finviz.screener import Screener

# A mini thread of the main thread. 
# Sleep normally.


class scanner_process_manager:
	def __init__(self,request_pipe):
		#if a downloading request is already sent. 
		self.downloading = False
		self.request = request_pipe
		self.pannel = None

	def set_pannel(self,scanner_pannel):
		self.pannel = scanner_pannel


	def adding_comlete(self):
		self.downloading = False

	def send_request(self,cond,market_,type_,cap):
		if(self.downloading == True):
			self.pannel.status_change("Downloading in progress")
			#print("Already downloading")
		else:
			self.downloading = True
			self.pannel.status_change("Downloading in progress")
			self.request.send([cond,market_,type_,cap])
			#when success, put it False. ... Put on a thread to receive it. 
			#HERE,.... seperate a thread to run it. 
			receive = threading.Thread(name="Reiceive info",target=self.receive_request, daemon=True)
			receive.start()


	def receive_request(self):
		d = self.request.recv()

		self.pannel.add_labels(d)

def multi_processing_scanner(pipe_receive):

	print("Database online")
	while True:
		receive_things = pipe_receive.recv()
		#unpack. 
		cond, market_, type_, cap = receive_things[0],receive_things[1],receive_things[2],receive_things[3]

		print(cond, market_, type_, cap)
		d = refreshstocks(cond, market_, type_, cap)
		#send back.
		pipe_receive.send(d)

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