import tkinter as tk 
from tkinter import ttk 
class pannel:

	def __init__(self,frame):

		self.tickers = []
		self.label_count = 0
		self.ticker_count = 0
		self.tickers_labels = {}
		self.tickers_tracers = {}


		self.reverse = True
		self.tm = ttk.LabelFrame(frame) 
		self.tm.place(x=0, y=40, relheight=0.85, relwidth=1)

		self.canvas = tk.Canvas(self.tm)
		self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll2 = tk.Scrollbar(self.tm)
		self.scroll2.config(orient=tk.VERTICAL, command=self.canvas.yview)
		self.scroll2.pack(side=tk.RIGHT,fill="y")

		self.canvas.configure(yscrollcommand=self.scroll2.set)
		
		self.frame = tk.Frame(self.canvas)
		self.frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.canvas.create_window(0, 0, window=self.frame, anchor=tk.NW)


	def rebind(self,canvas,frame):
		canvas.update_idletasks()
		canvas.config(scrollregion=frame.bbox()) 
		
	def label_default_configure(self,label):
		label.configure(activebackground="#f9f9f9")
		label.configure(activeforeground="black")
		label.configure(background="#d9d9d9")
		label.configure(disabledforeground="#a3a3a3")
		label.configure(relief="ridge")
		label.configure(foreground="#000000")
		label.configure(highlightbackground="#d9d9d9")
		label.configure(highlightcolor="black")

	def status_change_color(self,text,label):

		try:

			if text.get() == "Connecting":
				label["background"] = "#ECF57C"
			elif text.get() == "Unfound":
				label["background"] = "red"
			elif text.get() == "Connected":
				label["background"] = "#97FEA8"
			elif text.get() == "Lagged":
				label["background"] = "#ECF57C"
			else:
				label["background"] = "red"

		except Exception as e:

			print("destroyed labels")


	def sort_cur_range(self,d=None):

		#get all range,put in a dictionary.
		if d!=None:
			l = self.data.get_list()
			rank= {}
			for symbol in l:
				rank[symbol] = d[symbol].get()

			self.reverse = False if self.reverse else True
			rank = sorted(rank.items(), reverse=self.reverse,key=lambda x: x[1])

			new_ranking = {}
			for i in range(len(rank)):
				new_ranking[rank[i][0]]=i

		else: #just sort alphabestcially 

			l = self.data.get_list()

			self.reverse = False if self.reverse else True
			l = sorted(l,reverse=self.reverse)

			new_ranking = {}
			for i in range(len(l)):
				new_ranking[l[i]]=i

		self.redraw(new_ranking)
			
	def redraw(self,symbol_list):
		#only change the grid position
		print(symbol_list)
		for key,value in symbol_list.items():
			for j in range(len(self.labels)):
				self.tickers_labels[key][j].grid(row=symbol_list[key]+2,column=j,padx=0)


	def labels_creator(self,frame,cmd=None):

		if cmd ==None:
			for i in range(len(self.labels)): #Rows
				self.b = tk.Button(frame, text=self.labels[i],width=self.width[i])#command=self.rank
				if self.labels[i]=="Ticker":
					self.b["command"]=lambda:self.sort_cur_range(None)
				self.b.configure(activebackground="#f9f9f9")
				self.b.configure(activeforeground="black")
				self.b.configure(background="#d9d9d9")
				self.b.configure(disabledforeground="#a3a3a3")
				self.b.configure(relief="ridge")
				self.b.configure(foreground="#000000")
				self.b.configure(highlightbackground="#d9d9d9")
				self.b.configure(highlightcolor="black")
				self.b.grid(row=1, column=i)
		else:
			for i in range(len(self.labels)): #Rows

				if self.labels[i] not in cmd:
					self.b = tk.Button(frame, text=self.labels[i],width=self.width[i])#command=self.rank
				else:
					self.b = tk.Button(frame, text=self.labels[i],width=self.width[i],command=cmd[self.labels[i]])#command=self.rank
				if self.labels[i]=="Ticker":
					self.b["command"]=lambda:self.sort_cur_range(None)
				self.b.configure(activebackground="#f9f9f9")
				self.b.configure(activeforeground="black")
				self.b.configure(background="#d9d9d9")
				self.b.configure(disabledforeground="#a3a3a3")
				self.b.configure(relief="ridge")
				self.b.configure(foreground="#000000")
				self.b.configure(highlightbackground="#d9d9d9")
				self.b.configure(highlightcolor="black")
				self.b.grid(row=1, column=i)


def timestamp(s):

	p = s.split(":")
	try:
		x = int(p[0])*60+int(p[1])
		return x
	except Exception as e:
		print(e)
		return 0


def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print(e)
		return 0

#print(timestamp_seconds("13:23:46"))

# a={}
# a["b"]=1
# a["a"]=2

# for v,k in a.items():
# 	print(v,k)