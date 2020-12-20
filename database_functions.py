import requests 
import numpy as np

def fetch_high_low(symbol,data):
    req = symbol.split(".")[0]
    #print(symbol)
    postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=daily&period=14&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
    r= requests.post(postbody)
    r= r.text
    
    if r[:3] == "404":
        print(symbol,"Not found")

    else:
        O =1
        H =2
        L =3
        C =4
        V =5

        i = symbol
        a=data.symbol_data_openhigh_dis[i]
        b=data.symbol_data_openlow_dis[i]
        c=data.symbol_data_range_dis[i]

        for line in r.splitlines():
            lst=line.split(",")
            a.append(float(lst[H])-float(lst[L]))
            b.append(float(lst[H])-float(lst[O]))
            c.append(float(lst[O])-float(lst[L]))

        print(symbol,"Fetch range data complete:",len(a),"days")

        
        #set the var.
        data.symbol_data_openhigh_range[i].set(str(round(max(a),3))+"-"+str(round(min(a),3)))
        data.symbol_data_openlow_range[i].set(str(round(max(b),3))+"-"+str(round(min(b),3)))
        data.symbol_data_range_range[i].set(str(round(max(c),3))+"-"+str(round(min(c),3)))

        data.symbol_data_openhigh_val[i].set(round(np.mean(a),3))
        data.symbol_data_openlow_val[i].set(round(np.mean(b),3))
        data.symbol_data_range_val[i].set(round(np.mean(c),3))

        data.symbol_data_openhigh_std[i].set(round(np.std(a),3))
        data.symbol_data_openlow_std[i].set(round(np.std(b),3))
        data.symbol_data_range_std[i].set(round(np.std(c),3))

        data.symbol_loaded.append(i)