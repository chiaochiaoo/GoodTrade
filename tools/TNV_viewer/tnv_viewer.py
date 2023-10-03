import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import time 
import threading
import requests 
import json
import numpy as np
import pytz
from datetime import datetime
from datetime import date
import pandas as pd 

global data 
data = {}



def data_update():

    global data 

    while True:

        r = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?include_otc=false&apiKey=ezY3uX1jsxve3yZIbw2IjbNi5X7uhp1H"

        r = requests.get(r)
        # print(r.text)

        d = json.loads(r.text)

        last_min_stamp = []

        for i in d['tickers']:
            last_min_stamp.append(i['lastTrade']['t']//1000000000)

        cur_ts = max(last_min_stamp)

        data['timestamp'] = cur_ts

        for i in d['tickers']:
            data[i['ticker']] = {}
            data[i['ticker']]['day_open'] = i['day']['o'] 
            data[i['ticker']]['day_current'] = i['day']['c'] 
            data[i['ticker']]['day_high'] = i['day']['h'] 
            data[i['ticker']]['day_low'] = i['day']['l'] 
            data[i['ticker']]['day_volume'] = i['day']['v'] 

            # data[i['ticker']]['minute_open'] = i['min']['o'] 
            # data[i['ticker']]['minute_close'] = i['min']['c'] 
            # data[i['ticker']]['minute_high'] = i['min']['h'] 
            # data[i['ticker']]['minute_low'] = i['min']['l']
            # data[i['ticker']]['minute_volume'] = i['min']['v']

        time.sleep(5)
        #print(cur_ts%(3600*24))
###

###




class model:

    def __init__(self):
        self.model_initialized = False 
        self.model = {}

        self.pnl = np.array([None for i in range(570,960)])
        self.ts  = np.array([i for i in range(570,960)])

        self.e_pnl = []
        self.e_ts  = []

    def model_init(self):

        self.model =  {'COST': 2, 'GOOGL': 6, 'ADSK': 4, 'WBA': 21, 'CSCO': 29, 'AMZN': 5, 'CRWD': 6, 'NVDA': 2, 'MSFT': 3, 'AAPL': 5, 'PDD': 7, 'ATVI': 61, 'ZS': 6, 'TSLA': 2, 'ROST': 10, 'ADBE': 2, 'FANG': -5, 'REGN': -2, 'BKR': -21, 'HON': -9, 'ORLY': -1, 'GILD': -25, 'ENPH': -8, 'KHC': -41, 'EXC': -33, 'XEL': -16, 'IDXX': -3, 'MAR': -4, 'BIIB': -5, 'AEP': -11, 'PAYX': -6, 'AZN': -22}
        self.model_initialized = True 
        self.model_early_chart = False 

 

    def model_early_load(self):

        d = threading.Thread(target=self.model_load_early_chart,daemon=True)
        d.start() 

    def model_load_early_chart(self):
        print("loading start")
        dic = {}

        now = datetime.now(tz=pytz.timezone('US/Eastern'))
        ts = now.hour*60 + now.minute

        for key in self.model.keys():
          postbody = "https://financialmodelingprep.com/api/v3/historical-chart/1min/"+key+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"
          r= requests.get(postbody)
          # print(r.text)

          d = json.loads(r.text)
          dic[key] = d 

        earlier_pnl = np.zeros((len(dic),ts-570))
        c = 0
        for symbol,share in self.model.items():

          df = pd.DataFrame.from_dict(dic[symbol])

          df['date']= pd.to_datetime(df['date']) 
          df = df.loc[df['date']>pd.Timestamp(date.today())]
          df['ts'] = df['date'].dt.hour*60 + df['date'].dt.minute-570

          idx = df['ts'].tolist()[:ts-570]
          p = df['open'].to_numpy()[:ts-570]

          diff = (p-p[0])*share
          earlier_pnl[c][idx] = diff
          mask = earlier_pnl[c]==0
          earlier_pnl[c][mask]= np.interp(np.flatnonzero(mask), np.flatnonzero(~mask),  earlier_pnl[c][~mask])

          c+=1


        self.e_pnl = np.sum(earlier_pnl,axis=0)
        self.e_ts  = [570+i for i in range(len(self.e_pnl))]


        self.model_early_chart = True 
        print("loading complete ")
    def model_update(self):
        c= 0

        if self.model_initialized:
            for key,share in self.model.items():

                if key in data:
                    c+=(data[key]['day_current'] - data[key]['day_open'])*share
                else:
                    print("no",key)

            now = datetime.now(tz=pytz.timezone('US/Eastern'))
            ts = now.hour*60 + now.minute
            idx = ts-570

            # before = np.where(self.pnl==None)[0]
            # self.pnl[before[before<idx]]=0

            self.pnl[idx] = c
        else:
            self.model_init()

    def get_ts(self):
        return self.ts 

    def get_pnl(self):
        return self.pnl 

    def get_early_ts(self):
        return self.e_ts 

    def get_early_pnl(self):
        return self.e_pnl 

    def model_today_data(self):
        pass 


def create_tab(tab_name):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tab_name)

    # Sample Matplotlib chart
    fig = Figure(figsize=(5, 4), dpi=100)
    plot = fig.add_subplot(1, 1, 1)

   
    #plot.plot([i for i in range(570,960)],pnl)


    plot.set_title(f"{tab_name}")

    canvas = FigureCanvasTkAgg(fig, master=tab)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    obq = model()

    # LabelFrame for vertical buttons
    button_frame = ttk.LabelFrame(tab, text="Buttons")
    button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

    button1 = ttk.Button(button_frame, text="Load model")
    button1.pack(side=tk.TOP, pady=5)

    button1 = ttk.Button(button_frame, text="Load model early data",command=obq.model_early_load)
    button1.pack(side=tk.TOP, pady=5)

    # update_button = ttk.Button(button_frame, text="Plot Earlier", command=lambda: earlier_plot(obq,plot,canvas))
    # update_button.pack(side=tk.TOP, pady=10)

    # Buttons on the right side (vertical)
    button1 = ttk.Button(button_frame, text="Buy 1")
    button1.pack(side=tk.TOP, pady=5)

    button2 = ttk.Button(button_frame, text="Short 1")
    button2.pack(side=tk.TOP, pady=5)


    
    d = threading.Thread(target=update_chart, args=(obq,plot,canvas),daemon=True)
    d.start()
    # update_button = ttk.Button(button_frame, text="Update Chart", command=lambda: update_chart(plot,canvas,pnl))
    # update_button.pack(side=tk.TOP, pady=10)

    # button3 = ttk.Button(button_frame, text="Flat 1")
    # button3.pack(side=tk.TOP, pady=5)

# def earlier_plot(model,plot,canvas,pnl):

#     plot.clear()
#     plot.plot(model.get_ts(),model.get_pnl())
#     canvas.draw()


def update_chart(model,plot,canvas):

    global data 
    # Generate new data for the chart

    model.model_init()

    while True:
        #//
        # Clear the previous plot
        try:
            plot.clear()
            # Plot the new data

            model.model_update()
            plot.plot(model.get_ts(),model.get_pnl(), label='Line 1')

            if model.model_early_chart:

                plot.plot(model.get_early_ts(),model.get_early_pnl(), label='Line 2')


            now = datetime.now(tz=pytz.timezone('US/Eastern'))
            ts = now.hour*60 + now.minute

            plot.set_title("Updated Chart:"+now.strftime("%H:%M:%S"))

            # Redraw the canvas
            canvas.draw()


            time.sleep(5)
            print("chart updated:",ts)
        except Exception as e:
            print(e)

root = tk.Tk()
root.title("Tabbed Application")


d = threading.Thread(target=data_update, args=(),daemon=True)
d.start()


notebook = ttk.Notebook(root)

# Create 5 tabs
tabs = ["OBQ", ]# "Last Minute", "Tab 5"#"MRQ1", "MRQ2",

for tab_name in tabs:
    create_tab(tab_name)

notebook.pack(expand=True, fill="both")


#data_update

root.geometry("1280x720")
root.mainloop()