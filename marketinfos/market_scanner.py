import tkinter as tk
from tkinter import ttk


class market_scanner:

	def __init__(self,root):

		self.setting = ttk.LabelFrame(root,text="Market Heatmap Setting") 
		self.setting.place(x=10,y=10,height=80,width=780)



		self.market = tk.StringVar(self.setting)
		self.choices_m = {'All Markets','Nasdaq','NYSE','AMEX'}
		self.market.set('Nasdaq') 

		self.om = tk.OptionMenu(self.setting, self.market, *sorted(self.choices_m))
		self.menu2 = ttk.Label(self.setting, text="Market").grid(row = 1, column = 1)
		self.om.grid(row = 2, column =1)

		self.sector = tk.StringVar(self.setting)
		self.choices2 = {'All Sectors','Consumer Defensive','Financial','Industrials','Technology','Healthcare','Communication Services','Utilities','Real Estate','Energy','Basic Materials','Consumer Cyclical'}
		self.sector.set('Technology') 

		self.om2 = tk.OptionMenu(self.setting, self.sector, *sorted(self.choices2))
		self.menu2 = ttk.Label(self.setting, text="Sector").grid(row = 1, column = 2)
		self.om2.grid(row = 2, column =2)

		self.country = tk.StringVar(self.setting)
		self.choices = {'All countries','US','Canada','China','UK'}
		self.country.set('All countries') 

		self.om3 = tk.OptionMenu(self.setting, self.country, *sorted(self.choices))
		self.menu1 = ttk.Label(self.setting, text="Country").grid(row = 1, column = 3)
		self.om3.grid(row = 2, column =3)

		self.relv = tk.StringVar(self.setting)
		self.relv_choice = {'0.5 above','1 above','2 above','Any'}
		self.relv.set('Any') 

		self.om3 = tk.OptionMenu(self.setting, self.country, *sorted(self.relv_choice))
		self.menu1 = ttk.Label(self.setting, text="Min Rel.Volume").grid(row = 1, column = 4)
		self.om3.grid(row = 2, column =4)


		self.setting = ttk.LabelFrame(root,text="Market Heatmap") 
		self.setting.place(x=10,y=85,height=800,width=780)

		self.tabControl = ttk.Notebook(self.setting)
		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)
		self.tab3 = tk.Canvas(self.tabControl)
		self.tab4 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Prev Close') 
		self.tabControl.add(self.tab2, text ='High-Low') 
		self.tabControl.add(self.tab3, text ='Open-High') 
		self.tabControl.add(self.tab4, text ='Open-Low') 



root = tk.Tk() 
root.title("GoodTrade") 
root.geometry("800x400")
root.minsize(800, 700)
root.maxsize(1800, 900)

view = market_scanner(root)
root.mainloop()