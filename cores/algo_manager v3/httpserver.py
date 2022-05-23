
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

		global algoids
		self._set_response()
		#self.wfile.write("received".encode('utf-8'))

		stream_data = self.path[1:]

		#self.send_message(stream_data)
		print(stream_data)
		
		if "%20" in stream_data:
			stream_data = stream_data.replace("%20"," ")

		if TRADETYPE in stream_data:


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

					self.send_message(data)

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

					self.send_message(data)
					# data["symbol1_statistics"]
					# data["symbol2_statistics"]


		# if type_!="TEST":
		# 	self.send_message(msg)



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

	def do_POST(self):

		#self.send_message(stream_data)
		#print(stream_data)
		global algoids

		stream_data = self.rfile.read(int(self.headers['Content-Length'])).decode()


		#algo_id:TEST1,type_name:Single,algo_name:TEST,entry_type:MarketAction,symbol:SPY.AM,support:413,resistence:414,risk:50.0,immediate_deployment:True,management:HoldXSecond,


		type_ = find_between(stream_data,TRADETYPE,",")
		algo_id = find_between(stream_data,ALGOID,",")

		data = {}

		print(stream_data,type_,algo_id,algoids)

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

				self.send_message(data)

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

				self.send_message(data)
				# data["symbol1_statistics"]
				# data["symbol2_statistics"]
		else:
			print("already contained")
		self._set_response()
		#self.wfile.write("received".encode('utf-8'))

		#print(self.path[1:])

	def send_message(self,msg):

		global pipec
		#print("sending",msg,pipec)

		print("receiving:",msg)

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