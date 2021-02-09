import threading
import multiprocessing
import time
import re
import pip
import socket
import pickle

try:
    from finviz.screener import Screener
except ImportError:
    pip.main(['install', 'finviz'])
    from finviz.screener import Screener


HOST = '10.29.10.132'  # Standard loopback interface address (localhost)
PORT = 65423        # Port to listen on (non-privileged ports are > 1023)

# Now . I need to connect it. what do i do.
# 1. connect to the database. 



class scanner_process_manager:
	def __init__(self,request_pipe):
		#if a downloading request is already sent. 
		self.downloading = False
		self.downloading2 = False
		self.request = request_pipe
		self.pannel = None

		#bond the port

		#start receiving. nonstop. 
		receive = threading.Thread(name="Reiceive info",target=self.receive_request, daemon=True)
		receive.start()

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


	def receive_request(self):

		while True:
			print("manager reciving....:")
			d = self.request.recv()
			print("manager info received",d)

		#print(d)
		#check if it is normal type?
		# if d[0]=="Nasdaq":
		# 	self.pannel.add_nasdaq_labels(d)
		# else:
		# 	self.pannel.add_labels(d)

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

		elif order_type =="terminate":
			try:
				driver.quit()
			except:
				pass
			pipe_receive.send("termination successful")


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



###client just indefinitely fetch the package. ###
def client_scanner(pipe):

	k=""
	while True:

		HOST = '10.29.10.132'  # The server's hostname or IP address
		PORT = 65423       # The port used by the server

	
		print("Trying to connect to the Scanner server")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connected = False

		while not connected:
			try:
				s.connect((HOST, PORT))
				connected = True
			except:
				#pipe.send(["msg","Cannot connected. Try again in 2 seconds."])
				print("Cannot connect Scanner server. Try again in 2 seconds.")
				time.sleep(2)


		connection = True
		pipe.send(["msg","Connection Successful"])
		print("Scanner server Connection Successful")
		while connection:
			# try:
			# 	s.sendall(b'Alive check')
			# except:
			# 	connection = False
			# 	break
			data = []
			print("Scanner client: taking data")
			while True:
				try:
					part = s.recv(2048)
				except:
					connection = False
					break
				#if not part: break
				print("Scanner, hello")
				data.append(part)
				if len(part) < 2048:
					#try to assemble it, if successful.jump. else, get more. 
					try:
						k = pickle.loads(b"".join(data))
						#k = pd.read_pickle(b"".join(data))
						break
					except:
						pass
			#k is received. 
			print("Scanner client: taking data success",k[:5])
			pipe.send(["pkg",k])
		print("Server disconnected")
		pipe.send(["msg","Server disconnected"])
		# except Exception as e:
		# 	pipe.send(["msg",e])
		# 	print(e)
		#restarted the whole thing 


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