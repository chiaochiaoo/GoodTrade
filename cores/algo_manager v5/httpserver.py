
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

				elif "Basket" in stream_data:

					basket = find_between(stream_data,"Basket=",",")

					infos = find_between(stream_data,"Order=*","*")

					# risk = int(find_between(stream_data,"Risk=",","))

					# aggresive = int(find_between(stream_data,"Aggresive=",","))

					#print(stream_data)
					d={}
					for i in infos.split(","):

						a,b = i.split(":")
						d[a] = int(b)

					info = {}

					if "Profit" in stream_data:
						profit = find_between(stream_data,"Profit=",",")
						info['Profit'] = int(profit)
					if "Stop" in stream_data:
						stop = find_between(stream_data,"Stop=",",")
						info['Risk'] = int(stop)

					if "TA" in stream_data:
						TA = find_between(stream_data,"TA=",",")
						info['TA'] = int(TA)


					self.send_basket(basket,d,info)

				elif "Pair" in stream_data:

					pair = find_between(stream_data,"Pair=",",")

					symbol1 = find_between(stream_data,"Symbol1=",",")
					symbol2 = find_between(stream_data,"Symbol2=",",")
					amount = find_between(stream_data,"Amount=",",")

					ratio = find_between(stream_data,"Ratio=",",")
					passive = find_between(stream_data,"Passive=",",")

					print(amount,ratio,passive)

					d={}
					d['pair'] = pair
					d['symbol1'] = symbol1
					d['symbol2'] = symbol2
					d['amount'] = int(amount)
					d['ratio'] = [int(i) for i in ratio.split(":")]
					d['passive'] = int(passive)

					self.send_pair(d)
			except Exception as e:
				print("HTTP SERVER processing message failure",e)

	def send_pair(self,info):
		pipec.send(['pair',info])

	def send_basket(self,basket_name,orders,info):
		pipec.send(["basket",basket_name,orders,info])

	def flatten_basket(self,basket_name):
		pipec.send(["flatten",basket_name])
	# def send_basket(self,basket_name,orders,risk,aggresive):

	# 	global pipec
	# 	#print("sending",msg,pipec)

	# 	print("HTTP sending:",basket_name,orders,risk,aggresive)

	# 	pipec.send(["basket",basket_name,orders,risk,aggresive])

	def send_cmd(self,msg):

		global pipec
		#print("sending",msg,pipec)

		print("HTTP sending:",msg)

		pipec.send(["cmd",msg])

	def send_pkg(self,msg):

		global pipec
		#print("sending",msg,pipec)

		print("HTTP sending:",msg)

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



# stream_data = "Basket=MRQQQ,Risk=200,Order=*PDD.NQ:-3,ZM.NQ:-2,JD.NQ:-4,NTES.NQ:-3,CSCO.NQ:-8,ATVI.NQ:-8,AMD.NQ:-2,NVDA.NQ:-1,OKTA.NQ:-2,AMZN.NQ:-1,MCHP.NQ:-2,ADSK.NQ:-1,GOOGL.NQ:-2,EBAY.NQ:-6,PYPL.NQ:-2,INTC.NQ:-7,CRWD.NQ:-1,GOOG.NQ:-2,WDAY.NQ:-1,BIDU.NQ:-1,SIRI.NQ:-57,META.NQ:-1,DDOG.NQ:-1,EA.NQ:-2,CTSH.NQ:-4,ADI.NQ:-1,ABNB.NQ:-1,AZN.NQ:-6,CSX.NQ:-9,AAPL.NQ:-1,KHC.NQ:13,XEL.NQ:4,PCAR.NQ:3,AEP.NQ:2,CEG.NQ:2,EXC.NQ:6,SGEN.NQ:2,VRSK.NQ:1,PEP.NQ:1,DLTR.NQ:2,FAST.NQ:3,KDP.NQ:9,MDLZ.NQ:6,FISV.NQ:2,ADP.NQ:1,DXCM.NQ:1,NXPI.NQ:1,AMGN.NQ:1,VRSN.NQ:1,GILD.NQ:5,HON.NQ:1,ROST.NQ:2,SBUX.NQ:2,SWKS.NQ:1,CMCSA.NQ:7,MNST.NQ:2,PAYX.NQ:2,MTCH.NQ:3,CPRT.NQ:2,CDNS.NQ:1*Aggresive=0,"
# basket = find_between(stream_data,"Basket=",",")

# infos = find_between(stream_data,"Order=*","*")

# risk = int(find_between(stream_data,"Risk=",","))

# aggresive = int(find_between(stream_data,"Aggresive=",","))

# print(stream_data)
# d={}
# for i in infos.split(","):

# 	a,b = i.split(":")
# 	d[a] = int(b)