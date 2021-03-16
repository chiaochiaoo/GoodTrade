import time
import requests 
import socket

# register a symbol.


# pipe out update .
def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0
def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data


### Take L1 quote,
### Track order status 

class order_listener:

	def __init__(self,pipe=None):

		self.pipe = pipe

		self.port = 4134

		self.symbols = []



	def register(self,symbol):
		if symbol not in self.symbols:
			self.symbols.append(symbol)
			self.register_to_ppro(symbol, True)
			

	def deregister(self,symbol):

		if symbol in self.symbols:
			self.symbols.remove(symbol)
			self.register_to_ppro(symbol, False)


	def register_to_ppro(self,symbol,status):

		if status == True:
			postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=on"
		else:
			postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=off"

		try:
			r= requests.get(postbody)
			if r.status_code==200:
				return True
			else:
				return False
		except:
			print("register failed")
			return False

	#process all the update and send to pipe.
	def listener(self):

		UDP_IP = "localhost"
		UDP_PORT = self.port

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((UDP_IP, UDP_PORT))

		print("Socket Created:",sock)
		
		while True:
			data, addr = sock.recvfrom(1024)
			stream_data = str(data)
			#print(stream_data+",")

			#symbol = find_between(stream_data, "Symbol=", ",")
			# time = find_between(stream_data, "MarketTime=", ",")[:-4]
			# ts = timestamp_seconds(time)
			# bid = find_between(stream_data, "BidPrice=", ",")
			# ask = float(find_between(stream_data, "AskPrice=", ","))

			price = float(find_between(stream_data, "Price=", ","))
			vol = int(find_between(stream_data,"Volume=",","))
			side = find_between(stream_data,"Side=",",")
			print(price,side,vol,".")

			# print([symbol,time,ts,bid,ask])
			#self.pipe.send([symbol,ts,bid,ask])


p=price_updator()
#p.deregister("AAPL.NQ")
p.listener()

