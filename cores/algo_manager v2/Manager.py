from pannel import *
from tkinter import ttk
from Symbol import *
from TradingPlan import *
from UI import *

#May this class bless by the Deus Mechanicus.

class Manager:

	def __init__(self,root,port,goodtrade_pipe=None,order_pipe=None):

		self.symbols = []

		self.symbol_data = {}		
		self.tradingplan = {}

		self.ui = UI(root)
		self.add_new_tradingplan("AAPL")
		self.add_new_tradingplan("SDS")
		
	#data part, UI part
	def add_new_tradingplan(self,symbol):

		if symbol not in self.symbols:

			self.symbol_data[symbol]=Symbol(symbol)  #register in Symbol.
			self.tradingplan[symbol]=TradingPlan(self.symbol_data[symbol])

			self.ui.create_new_entry(self.tradingplan[symbol])
			
			#register in ppro

			#append it to, UI.
		else:
			print("symbols already exists, modifying current parameter.")

			
	def goodtrade_listener(self,d):

		#['id', 'QQQ.NQ', 'Breakout on Support on 0.0 for 0 sec', 'Short', 20, 20.0]
		#handle database. and add labels. 
		#id, symbol, type, status, description, position, shares, risk$

		if d!=None:

			message_type = d[0]

			if message_type =="New order": 

				self.order_creation(d)

				#self.order_confirmation(d)


if __name__ == '__main__':

	port =4609
	root = tk.Tk() 
	root.title("GoodTrade Algo Manager v2") 
	root.geometry("1800x800")

	Manager(root,port)
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()