
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import Util_functions


#message creation
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


SINGLE = "S"
PAIR = "P"

BASKET  = "B"
# SINGLE 
# type_name = data["type_name"]
# algo_id = data["algo_id"]
# algo_name =  data["algo_name"]
# symbol = data["symbol"] 
# entryplan = data["entry_type"]
# support = data["support"]
# resistence =  data["resistence"]
# risk = data["risk"]
# stats = data["statistics"]
# status = data["immediate_deployment"]
# mana = data["management"]


# PAIR 

SYMBOL1 = "Symbol1="
SYMBOL2 = "Symbol2="
SYMBOL1SHARE = "Symbol1share="
SYMBOL2SHARE = "Symbol2share="
RISK =  "Risk="
MANAGEMENT = "Management="

# type_name = data["type_name"]
# algo_id = data["algo_id"]
# algo_name =  data["algo_name"]
# symbol1 = data["symbol1"] 
# symbol2 = data["symbol2"]
# symbol1_share = data["symbol1_share"]
# symbol2_share =  data["symbol2_share"]
# risk = data["risk"]
# symbol1_stats = data["symbol1_statistics"]
# symbol2_stats = data["symbol2_statistics"]
# mana = data["management"]


global algoids
algoids = []
#how do i take a pipe in? 
#uses global? 
def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

class S(BaseHTTPRequestHandler):
	def _set_response(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):

		self._set_response()
			#self.wfile.write("received".encode('utf-8'))

		try:
			stream_data = self.path[1:]

			#self.send_message(stream_data)

			if "%20" in stream_data:
				stream_data = stream_data.replace("%20"," ")

			self.process_msg(stream_data)
		except Exception as e:
			print("HTTP SERVER processing message failure",e)

	def do_POST(self):


		self._set_response()
		#self.wfile.write("received".encode('utf-8'))

		try:
			stream_data = self.path[1:]

			#self.send_message(stream_data)

			if "%20" in stream_data:
				stream_data = stream_data.replace("%20"," ")

			self.process_msg(stream_data)
		except Exception as e:
			print("HTTP SERVER processing message failure",e)


	def process_msg(self,stream_data):


		# 3 TYPES OF Msg. 1. TV broadcast cmd. 2. trade placement. 3. TV trade placement. 


			try:
				#print("receive:",stream_data)

				if "Command" in stream_data:

					cmd = find_between(stream_data,"Command=",",")
					basket = find_between(stream_data,"Basket=",",")

					if cmd == "FLATTEN":
						self.flatten_basket(basket)

				elif "Cancel" in stream_data:

					symbol = find_between(stream_data,"Cancel=",",")

					self.cancel_symbol(symbol)

				elif "Basket" in stream_data:


					basket = find_between(stream_data,"Basket=",",")

					orders = find_between(stream_data,"Order=*","*")

					# risk = int(find_between(stream_data,"Risk=",","))

					# aggresive = int(find_between(stream_data,"Aggresive=",","))


					d={}
					for i in orders.split(","):

						a,b = i.split(":")
						d[a] = int(b)

					info = {}

					if "Infos" in stream_data:
						infos = find_between(stream_data,"Infos=(",")") 
						for i in infos.split(","):

							if "=" in i:
								a,b = i.split("=")
								info[a] = int(b)

					# if "Profit=" in stream_data:
					# 	profit = find_between(stream_data,"Profit=",",")
					# 	info['Profit'] = int(profit)
					# if "Stop=" in stream_data:
					# 	stop = find_between(stream_data,"Stop=",",")
					# 	info['Risk'] = int(stop)

					# if "TA=" in stream_data:
					# 	TA = find_between(stream_data,"TA=",",")
					# 	info['TA'] = int(TA)


					self.send_basket(basket,d,info)

				elif "Pair" in stream_data:

					pair = find_between(stream_data,"Pair=",",")

					symbol1 = find_between(stream_data,"Symbol1=",",")
					symbol2 = find_between(stream_data,"Symbol2=",",")
					amount = find_between(stream_data,"Amount=",",")

					ratio = find_between(stream_data,"Ratio=",",")
					passive = find_between(stream_data,"Passive=",",")

					info = {}


					d={}
					d['pair'] = pair
					d['symbol1'] = symbol1
					d['symbol2'] = symbol2
					d['amount'] = int(amount)
					d['ratio'] = [int(i) for i in ratio.split(":")]
					d['passive'] = int(passive)


					if "Infos" in stream_data:
						infos = find_between(stream_data,"Infos=(",")") 
						for i in infos.split(","):

							if "=" in i:
								a,b = i.split("=")
								#info[a] = int(b)
								d[a] =int(b)
								
					self.send_pair(d)
			except Exception as e:
				print("HTTP SERVER processing message failure",e)

	def send_pair(self,info):
		pipec.send(['pair',info])

	def send_basket(self,basket_name,orders,info):
		pipec.send(["basket",basket_name,orders,info])

	def cancel_symbol(self,symbol):
		pipec.send(['cancel',symbol])

	def flatten_basket(self,basket_name):
		pipec.send(["flatten",basket_name])
	# def send_basket(self,basket_name,orders,risk,aggresive):

	# 	global pipec


	# 	print("HTTP sending:",basket_name,orders,risk,aggresive)

	# 	pipec.send(["basket",basket_name,orders,risk,aggresive])

	def send_cmd(self,msg):

		global pipec
		pipec.send(["cmd",msg])

	def send_pkg(self,msg):

		global pipec

		pipec.send(["pkg",[msg]])
		#pipe.send(msg)

		#msgid=xxx,Message=L1,MarketTime=14:24:38.206,Symbol=SNDL.NQ,BidPrice=0.828300,BidSize=13899,AskPrice=0.828400,AskSize=2364,Tick=?\n'

		# msgid = find_between(stream_data,"")
		# symbol = find_between(stream_data, "Symbol=", ",")
		# side = find_between(stream_data, "Side=", ",")
		# info = find_between(stream_data, "InfoText=", ",")

		# print("hello",str(self.path))
		# self._set_response()
		# self.wfile.write("received".encode('utf-8'))

		# content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
		# post_data = self.rfile.read(content_length) # <--- Gets the data itself
		# logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
		#         str(self.path), str(self.headers), post_data.decode('utf-8'))

		# self._set_response()
		# self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def httpserver(pipex):

	from http.server import BaseHTTPRequestHandler, HTTPServer
	import logging

	global pipec
	pipec = pipex
	server_class=HTTPServer
	handler_class=S
	port=4440

	logging.basicConfig(level=logging.INFO)
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	logging.info('Starting httpd...\n')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	logging.info('Stopping httpd...\n')


