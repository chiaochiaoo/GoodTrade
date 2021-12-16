class Near_high():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","Rel.V","Rg.Score","High","SO%","SC%","listed","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.total_len = len(self.labels)
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				near = row['rangescore']
				high = row['high']

				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,relv,near,high,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)

class Near_low():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","Rel.V","Rg.Score","Low","SO%","SC%","listed","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.root = root

		self.total_len = len(self.labels)
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				near = row['rangescore']
				high = row['low']

				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,relv,near,high,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		except Exception as e:
			print("TNV scanner construction near low:",e)

class Spread():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,8,4,4,4,8,6,8,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Pairs","CurSpread","Cur σ","PC σ","OP σ","Last5m σ","Ratio","R.Stability","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.total_len = len(self.labels)
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]
		# Index(['symbol1', 'symbol2', 'current_spread', 'date', 'ratio_mean',
		#        'ratio_stability', 'outlier', 'neg_tail997', 'pos_tail997',
		#        'neg_tail990', 'pos_tail990', 'neg_tail970', 'pos_tail970',
		#        'coefficient', 'intercept', 'std', 'pe', 'pr', 'avgr', 'stdr',
		#        'quality', 'current_sigma'],
		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		if 1:
			for index, row in df.iterrows():
				#print(row)
				#["Pairs","CurSpread","Cur σ","PC σ","OP σ","DayMax σ","DayLow σ","Ratio","R.Stability","Add"]
				#"current_sigma","close_sigma","open_sigma","max_sigma","min_sigma","last5_sigma"
				rank = index
				spread = round(row['current_spread'],2)
				sig = round(row['current_sigma'],2)

				pcsig = round(row['close_sigma'],2)
				opsig = round(row['open_sigma'],2)

				last5 = round(row['last5_sigma'],2)

				ratio = ratio_compute(row['coefficient'])
				ratio_stability = str(round((1-row['ratio_stability'])*100))+"%"


				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,spread,sig,pcsig,opsig,last5,ratio,ratio_stability]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)

class Premarket_pick():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,7,7,7,7,6,6,6,6,8,6]
		self.labels = ["Symbol","A.Vol","Rel.V","RR.ratio","Ex.Mmtm","Rg.SCORE","SC%","Listed","Add"]
		self.root = root
		self.recreate_labels(self.root)

		self.file = "signals/premarket_pick_"+datetime.now().strftime("%m-%d")+".csv"

		#self.update_entry([pd.read_csv("test2.csv",index_col=0)])

	def recreate_labels(self,frame):

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data
		#timestamp = data[1]

		#self.NT_stat["text"] = "Last update: "+timestamp

		#df.to_csv("tttt.csv")
		entry = 0

		if len(data)>1:
			try:
				for index, row in df.iterrows():
					#print(row)

					#["Symbol","Vol","Rel.V","Side","Re.SCORE","SC%","Listed","Since","Ignore","Add"]
					rank = index
					vol = row['Avg VolumeSTR']
					relv = row['rrvol']
					side = row['reversalside']
					rscore = row['rangescore']
					sc = row['SC']

					since = ts_to_min(row['reversal_timer'])

					row['Signal Time'] = since
					############ add since, and been to the thing #############

					if self.NT != None:
						if rank in self.NT.nasdaq_trader_symbols_ranking:
							listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
						else:
							listed = "No"
					else:
						listed = "No"
					#print(self.NT.nasdaq_trader_symbols)
					if 1: #score>0:	

						lst = [rank,vol,relv,side,rscore,sc,listed,since]

						for i in range(len(lst)):
							self.entries[entry][i]["text"] = lst[i]
						entry+=1
						if entry ==50:
							break

				while entry<50:
					#print("ok")
					for i in range(10):
						self.entries[entry][i]["text"] = ""
					entry+=1

				# keep = ['Symbol', "Signal Time", 'rrvol', 'SC', 'reversalside','reversal_score','Signal Time',]

				# for i in df.columns:
				# 	if i not in keep:
				# 		df.pop(i)
				#df.to_csv(self.file)
			except Exception as e:
				print("TNV scanner construction Premarket_pick:",e)

class Open_Break():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,5,5,6,6,6,6,8,6]
		self.labels = ["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		self.file = "signals/open_break_"+datetime.now().strftime("%m-%d")+".csv"
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.

		#["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		df = data


		#df.to_csv("open_break_out.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				vol = row['Avg VolumeSTR']
				relv = row['rrvol']
				brscore = row['score2']
				roc5 = row['5ROCP']
				so = row['SO']
				sc = row['SC']
				since = ts_to_min(row['since'])
				last = row['last']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,vol,relv,brscore,roc5,so,sc,listed,since,last]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(10):
					self.entries[entry][i]["text"] = ""
				entry+=1

		except Exception as e:
			print("TNV scanner construction open break:",e)

class CoreysPick():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,5,5,6,6,6,6,8,6]
		self.labels = ["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		self.file = "signals/Coreypick"+datetime.now().strftime("%m-%d")+".csv"
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1


	def update_entry(self,data):

		#at most 8.

		#["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		df = data


		#df.to_csv("open_break_out.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				vol = row['Avg VolumeSTR']
				relv = row['rrvol']
				brscore = row['score2']
				roc5 = row['5ROCP']
				so = row['SO']
				sc = row['SC']
				since = row['since']
				last = row['last']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,vol,relv,brscore,roc5,so,sc,listed,since,last]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(10):
					self.entries[entry][i]["text"] = ""
				entry+=1

		except Exception as e:
			print("TNV scanner construction open break:",e)

class Just_break():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,5,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","Rel.V","Side","Been","SO%","SC%","Rg eval","Vol eval","listed","Add"]
		self.root = root
		self.total_len = len(self.labels)
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				side = row['just_break']

				span = row['break_span']
				so = row['SO']
				sc = row['SC']

				tr =  row['tr_eval']
				vol = row['vol_eval']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,relv,side,span,so,sc,tr,vol,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		except Exception as e:
			print("TNV scanner construction voli:",e)

