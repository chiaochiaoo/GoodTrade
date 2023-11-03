import tkinter as tk
from tkinter import ttk
# import pip


# try:
#     pip.main(['install', 'matplotlib'])
#     pip.main(['install', 'requests'])
#     pip.main(['install', 'python-matplotlib'])
#     pip.main(['install', 'pytz'])
#     pip.main(['install', 'pandas'])
#     pip.main(['install', 'numpy'])
# except:
#   pass

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
from models import *
import os
import traceback
global data 
data = {}


def PrintException(info,additional="ERROR"):
    # exc_type, exc_obj, tb = sys.exc_info()
    # f = tb.tb_frame
    # lineno = tb.tb_lineno
    # filename = f.f_code.co_filename
    # linecache.checkcache(filename)
    # line = linecache.getline(filename, lineno, f.f_globals)
    # log_print (info+'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(additional,info,exc_type, fname, exc_tb.tb_lineno,traceback.format_exc())


def data_update():

    global data 

    while True:


        try:
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

                data[i['ticker']]['bid'] = i['lastQuote']['p']
                data[i['ticker']]['ask'] = i['lastQuote']['P']

                # data[i['ticker']]['minute_open'] = i['min']['o'] 
                # data[i['ticker']]['minute_close'] = i['min']['c'] 
                # data[i['ticker']]['minute_high'] = i['min']['h'] 
                # data[i['ticker']]['minute_low'] = i['min']['l']
                # data[i['ticker']]['minute_volume'] = i['min']['v']

            time.sleep(5)
        except Exception as e:
            PrintException(e)


def create_tab(tab_name):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tab_name)

    # Sample Matplotlib chart
    fig = Figure(figsize=(5, 4), dpi=100)

    fig, axs = plt.subplots(2, 1, figsize=(10, 4), gridspec_kw={'height_ratios': [2, 1,]}) #'width_ratios': [2, 1,]

    #plot = fig.add_subplot(1, 1, 1)

    plot = axs[0]
    #plot.plot([i for i in range(570,960)],pnl)


    plot.set_title(f"{tab_name}")

    eval_plot = axs[1]
    eval_plot.set_title("Eval")
    canvas = FigureCanvasTkAgg(fig, master=tab)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


    if tab_name == "OBQ":
        model = obq_model()

    elif tab_name =="QFAANG":
        name = "QFAANG"
        model =  {'QQQ.NQ': 8, 'AAPL.NQ': -1, 'AMZN.NQ': -1, 'MSFT.NQ': -2, 'META.NQ': -3, 'GOOG.NQ': -1, }
        historical_plus = [0.031356,0.03812058,0.05]
        historical_minus =[-0.03046357,-0.03919835,-0.05]


        model =  quick_model(name,model,historical_plus,historical_minus)

    elif tab_name =="QEV":
        name = "QEV"
        model =  {'QQQ.NQ': 4, 'TSLA.NQ': -1, 'NIO.NY': -29, 'LCID.NQ': -33, 'RIVN.NQ': -5}
        historical_plus =[0.02769937,0.03559813,0.04095039]
        historical_minus =[-0.02457263,-0.0369145,-0.03967848]

        model =  quick_model(name,model,historical_plus,historical_minus)

    elif tab_name =="QBT":
        name = "QBT"
        model =  {'QQQ.NQ': 11, 'MARA.NQ': -20, 'RIOT.NQ': -22, 'COIN.NQ': -4, }
        historical_plus =[0.01054703,0.01527036,0.02186224]
        historical_minus =[-0.01193436,-0.01220059,-0.01666259]

        model =  quick_model(name,model,historical_plus,historical_minus)
    # LabelFrame for vertical buttons

    # info_frame = ttk.LabelFrame(tab, text="Infos")
    # info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

    button_frame = ttk.LabelFrame(tab, text="Buttons")
    button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

    row =1
    button1 = ttk.Button(button_frame, text="Load model",command=model.model_init)
    button1.grid(sticky="w",column=1,row=row) 

    row +=1
    button1 = ttk.Button(button_frame, text="Load Earlier",command=model.model_early_load)
    button1.grid(sticky="w",column=1,row=row) 

    row +=1
    tk.Label(button_frame,text="Profit:").grid(sticky="w",column=1,row=row) 
    tk.Entry(button_frame,textvariable=model.profit,width=8).grid(sticky="w",column=2,row=row) 

    row +=1
    tk.Label(button_frame,text="Stop:").grid(sticky="w",column=1,row=row) 
    tk.Entry(button_frame,textvariable=model.stop,width=8).grid(sticky="w",column=2,row=row) 


    row +=1
    button1 = ttk.Button(button_frame, text="Buy 1 Total",command=model.model_buy)
    button1.grid(sticky="w",column=1,row=row) 

    row +=1
    button2 = ttk.Button(button_frame, text="Short 1 Total",command=model.model_sell)
    button2.grid(sticky="w",column=1,row=row) 

    # row +=1
    # button1 = ttk.Button(button_frame, text="Buy 1 Long Only")
    # button1.grid(sticky="w",column=1,row=row) 


    # row +=1
    # button1 = ttk.Button(button_frame, text="Short 1 Long Only")
    # button1.grid(sticky="w",column=1,row=row) 


    # row +=1
    # button1 = ttk.Button(button_frame, text="Buy 1 Short Only")
    # button1.grid(sticky="w",column=1,row=row) 


    # row +=1
    # button1 = ttk.Button(button_frame, text="Sell 1 Short Only")
    # button1.grid(sticky="w",column=1,row=row) 



    d = threading.Thread(target=update_chart, args=(model,plot,eval_plot,canvas),daemon=True)
    d.start()

def update_chart(model,plot,eval_plot,canvas):

    global data 
    # Generate new data for the chart

    #model.model_init()

    while True:
        #//
        # Clear the previous plot
        try:
            plot.clear()
            # Plot the new data

            model.model_update(data)
            plot.plot(model.get_ts(),model.get_pnl(), label='Line 1')


            categories = ['long', 'short']
            values = [model.get_long(), model.get_short()]

            # Create a bar plot
            eval_plot.bar(categories, values,color=["green","red"])

            if model.model_early_chart:
                plot.plot(model.get_early_ts(),model.get_early_pnl(), label='Line 2')

            if model.historical_computed:

                # if up, if down.

                str_ = ""

                levels = ["90%: ","95%: ","99%: "]

                for i in range(len(model.historical_plus)):
                    str_+=levels[i]+str(int(model.historical_plus[i]*model.historical_fixpoint))+"\n"
                str_ = str_[:-1]
                legend = plot.legend(loc='upper right')
                legend.get_texts()[0].set_text(str_)
                #plot.legend(handles=[], labels=['1','90%:','2'])

                # comment_text = "Top Right Comment"
                # plot.annotate(comment_text, xy=(1, 1), xytext=(-5, -5), ha='right', va='top', textcoords='axes fraction', fontsize=10)

                # for i in model.historical_plus:
                #     print(i*model.historical_fixpoint)
                    #plot.axhline(i*model.historical_fixpoint,linestyle="--")
                # if model.cur>0:
                #     #print("HHIIIIII U")
                #     for i in model.historical_plus:
                #         #print(i*model.historical_fixpoint)
                #         plot.axhline(i*model.historical_fixpoint,linestyle="--")
                #     plot.set_ylim([0,-10])
                #     #plot.set_ylim([min(model.pnl), max(model.pnl)*2])
                # else:
                #     #print("HHIIIIII D")
                #     for i in model.historical_minus:
                #         print(i*model.historical_fixpoint)
                #         plot.axhline(i*model.historical_fixpoint,linestyle="--")


                #    # plot.set_ylim([-10,])
                #     print(min(model.pnl)*2, max(model.pnl))
                    #plot.set_ylim([min(model.pnl)*2, max(model.pnl)])
                    #plt.xlim([max(model.pnl), model.historical_plus[-1]*model.historical_fixpoint])
            now = datetime.now()#tz=pytz.timezone('US/Eastern')
            ts = now.hour*60 + now.minute

            plot.set_title("Updated Chart:"+now.strftime("%H:%M:%S")+"     SPREAD:" + model.get_spread()+"  CUR:"+model.get_price())

            # Redraw the canvas
            canvas.draw()

            time.sleep(5)
            print("chart updated:",ts)
        except Exception as e:
            PrintException(e)

root = tk.Tk()
root.title("Tabbed Application")


d = threading.Thread(target=data_update, args=(),daemon=True)
d.start()



try:
    notebook = ttk.Notebook(root)

    # Create 5 tabs
    tabs = [ "QFAANG","QEV","QBT","OBQ"]# "Last Minute", "Tab 5"#"MRQ1", "MRQ2", #"OBQ", #"OBQ"

    for tab_name in tabs:
        create_tab(tab_name)

    notebook.pack(expand=True, fill="both")


    #data_update
    root.title("SelectTrade Model Viewer")
    root.geometry("1280x720")
    root.mainloop()
except Exception as e:
    PrintException(e)