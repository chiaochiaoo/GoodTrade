
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

		stream_data = self.path[1:]

		#self.send_message(stream_data)

		if "%20" in stream_data:
			stream_data = stream_data.replace("%20"," ")

		self.process_msg(stream_data)


	def do_POST(self):


		self._set_response()
		#self.wfile.write("received".encode('utf-8'))

		stream_data = self.path[1:]

		#self.send_message(stream_data)

		if "%20" in stream_data:
			stream_data = stream_data.replace("%20"," ")

		self.process_msg(stream_data)


	def process_msg(self,stream_data):


		# 3 TYPES OF Msg. 1. TV broadcast cmd. 2. trade placement. 3. TV trade placement. 

		if "Strategy" in stream_data:

			data = {}

			data["algo_id"] = "algo_id"
			data["type_name"] = "Tradingview"
			data["Strategy"] = find_between(stream_data,"Strategy=",",")
			data["Symbol"] = find_between(stream_data,"Symbol=",",")
			data["Side"] = find_between(stream_data,"Side=",",")
			data["Share"] = find_between(stream_data,"Shares=",",")

			self.send_pkg(data)
			#print(data)


		elif "Basket" in stream_data:

			basket = find_between(stream_data,"Basket=",",")

			infos = find_between(stream_data,"Order=*","*")

			risk = find_between(stream_data,"Risk=",",")

			print(stream_data)
			d={}
			for i in infos.split(","):

				a,b = i.split(":")
				d[a] = int(b)

			self.send_basket(basket,d,risk)


		elif "Command" in stream_data:

			Command = find_between(stream_data,"Command=",",")

			self.send_cmd(Command)
			print(Command)


		elif TRADETYPE in stream_data:

			#print(stream_data)
			type_ = find_between(stream_data,TRADETYPE,",")
			algo_id = find_between(stream_data,ALGOID,",")

			data = {}

			if algo_id not in algoids:
				if type_=="Single"  :
					algoids.append(algo_id)

					data["type_name"] = type_
					data["algo_id"] = algo_id
					data["algo_name"] = find_between(stream_data,ALGONAME,",")
					data["symbol"] = find_between(stream_data,SYMBOL,",")
					data["entry_type"] = find_between(stream_data,ENTRYPLAN,",")
					data["support"] = find_between(stream_data,SUPPORT,",")
					data["resistence"] = find_between(stream_data,RESISTANCE,",")
					data["risk"] = find_between(stream_data,RISK,",")
					#data["statistics"] = find_between(stream_data,ALGOID,",")

					if find_between(stream_data,DEPLOY,",")=="T":
						data["immediate_deployment"] = True
					else:
						data["immediate_deployment"] = False


					data["management"] = find_between(stream_data,MANAGEMENT,",")

					self.send_pkg(data)

				if type_ =="Pair":

					data["type_name"] = type_
					data["algo_id"] = algo_id
					data["algo_name"] = find_between(stream_data,ALGONAME,",")
					data["symbol1"]  = find_between(stream_data,SYMBOL1,",")
					data["symbol2"]  = find_between(stream_data,SYMBOL2,",")
					data["symbol1_share"] = find_between(stream_data,SYMBOL1SHARE,",")
					data["symbol2_share"] =  find_between(stream_data,SYMBOL2SHARE,",")
					data["risk"] =find_between(stream_data,RISK,",")

					data["management"] = find_between(stream_data,MANAGEMENT,",")

					self.send_pkg(data)
					# data["symbol1_statistics"]
					# data["symbol2_statistics"]

	def send_basket(self,basket_name,orders,risk):

		global pipec
		#print("sending",msg,pipec)

		print("sending:",basket_name,orders,risk)

		pipec.send(["basket",basket_name,orders,risk])
	def send_cmd(self,msg):

		global pipec
		#print("sending",msg,pipec)

		print("sending:",msg)

		pipec.send(["cmd",msg])

	def send_pkg(self,msg):

		global pipec
		#print("sending",msg,pipec)

		print("sending:",msg)

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
	port=4441

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



# stream_data="Basket=koko,Order=AAPL.NQ:5,AMD.NQ*"
# basket = find_between(stream_data,"Basket=",",")

# infos = find_between(stream_data,"Order=","*")

# print(basket,infos)

# d={}
# for i in infos.split(","):
# 	print(i)
# 	a,b = i.split(":")
# 	d[a] = int(b)

# print(d)






# s=" /Trade_type=Single,Algo_id=Manual_LCID.NQ944,Algo_name=Manual%20Trade,Symbol=LCID.NQ,Entry_typeInstant%20Short,Support0,Resistance22.0,Risk=3.0,Side=Short,Deploy=T,Management=FullManual"


# s.replace("%20"," ")
# print(s.replace("%20"," "))
#httpserver("GEGE")


# TRADETYPE = "Trade_type="
# ALGOID ="Algo_id="
# ALGONAME ="Algo_name="
# SYMBOL = "Symbol="
# ENTRYPLAN = "Entry_type"
# SUPPORT = "Support"
# RESISTANCE = "Resistance"
# RISK =  "Risk="
# SIDE =  "Side="
# DEPLOY = "Deploy="
# MANAGEMENT = "Management="

# a = [DEPLOY,TRADETYPE,ALGOID,ALGONAME,SYMBOL,ENTRYPLAN,SUPPORT,RESISTANCE,RISK,SIDE,MANAGEMENT]

# b = [i for i in range(len(a))]
# b[0] = True

# print(b)

# msg = ""
# for i in range(len(a)):

# 	msg+= str(a[i])+str(b[i])+","

# print(msg)

#s = "Algo_id=TEST1,Trade_type=Single,Algo_name=TEST,Entry_type=MarketAction,Symbol=SPY.AM,Support=413,Resistance=414,Side=Long,Risk=50.0,Deploy=T,Management=HoldXSecond"

#Algo_id=TEST1,Trade_type=Single,Algo_name=TEST,Entry_type=MarketLong,Symbol=SPY.AM,Support=413,Resistance=414,Side=Long,Risk=5.0,Deploy=T,Management=HoldXSecond,
#Algo_id=TEST1,Trade_type=Single,Algo_name=TEST,Entry_type=MarketShort,Symbol=SPY.AM,Support=413,Resistance=414,Side=Short,Risk=5.0,Deploy=T,Management=HoldXSecond,


# stream_data="Basket=koko,Risk=10,Order={SPY.AM:0,QQQ.NQ:0}"

# basket = find_between(stream_data,"Basket=",",")
# infos = find_between(stream_data,"Order={","}")
# risk = find_between(stream_data,"Risk=",",")
# print(basket,infos,risk)