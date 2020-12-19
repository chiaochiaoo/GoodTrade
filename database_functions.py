import requests 

def fetch_high_low(symbol,Range,Openhigh,Openlow):
    symbol = symbol.split(".")[0]
    #print(symbol)
    postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=daily&period=14&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
    r= requests.post(postbody)
    r= r.text
    
    #print(r)
    # Range=[]
    # Openhigh=[]
    # Openlow=[]
    
    if r[:3] == "404":
        print(symbol,"Not found")

    else:
        O =1
        H =2
        L =3
        C =4
        V =5

        for line in r.splitlines():
            lst=line.split(",")
            Range.append(float(lst[H])-float(lst[L]))
            Openhigh.append(float(lst[H])-float(lst[O]))
            Openlow.append(float(lst[O])-float(lst[L]))

        print(symbol,"Fetch range data complete:",len(Range),"days")