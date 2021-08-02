import socket
import requests
from os import path
import csv

def get_sec(time_str):
	"""Get Seconds from time."""
	h, m, s = time_str.split(':')
	return int(h) * 3600 + int(m) * 60 + int(s)

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data
	
postbody = "http://localhost:8080/SetOutput?symbol=SPY.AM&feedtype=L1&output=4141&status=on"
r= requests.post(postbody)

# postbody = "http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=4139&status=on"
# r= requests.post(postbody)

UDP_IP = "localhost"
UDP_PORT = 4141

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

file_name = "tos_test.csv"
if not path.exists(file_name):
	with open(file_name, 'w',newline='') as csvfile:
		writer = csv.writer(csvfile)
		#writer.writerow(['timestamp', 'price','size'])

i = 0
print("start")
with open(file_name, 'a',newline='') as csvfile:
	writer = csv.writer(csvfile)
	while True:
		data, addr = sock.recvfrom(1024)
		stream_data = str(data)
		time = find_between(stream_data, "MarketTime=", ",")
		t1 = get_sec(time[:-4])
		size = int(find_between(stream_data, "Size=", ","))
		price = float(find_between(stream_data, "Price=", ","))

		writer.writerow([t1,size,price])
		i+=1
		if i%50==0:
			print(stream_data)