import pandas as pd
import time

def get_min(time_str):
	"""Get Seconds from time."""
	h, m= time_str.split(':')
	#print(h,m)
	return int(h) * 60 + int(m)

def ts_to_str(timestamp):
	
	h= int(timestamp//60)
	m= int(timestamp%60)

		
	#chekc if they are 1 unit.
	
	if h//10 == 0:
		h = "0"+str(h)
	else:
		h = str(h)
		
	if m//10 == 0:
		m = "0"+str(m)
	else:
		m = str(m)
		

	return(h+":"+m)


		
	return x

def pair_gap(s,q):
    timestamps = []
    timestampq = []
    
    for i in range(len(s)):
        timestamps.append(s["day"][i]+" "+s["time"][i])
                                            
    for i in range(len(q)):
        timestampq.append(q["day"][i]+" "+q["time"][i])
                                            
            
    s.insert(2,"timestamp", timestamps, True) 
    q.insert(2,"timestamp", timestampq, True) 
    
    
    #drop all needed rows. 
    
    drop =["open","high","low","volume","day","time"]
    
    s = s.drop(drop,axis=1)
    q = q.drop(drop,axis=1)
    
                                            
    j = pd.merge(s,q,on='timestamp')
    
    pricegap = []
    for i in range(len(j)):
        pricegap.append(j["close_x"][i]-j["close_y"][i])
        
    j.insert(1,"price_gap", pricegap, True) 
    
    return j 

def spread_extractor(argv):
	if len(argv)!=4:
		print("Spread Extractor: 2 files and 2 names")
		return []
		#os._exit(1)
	
	else:
		start = time.time() 
		S =pd.read_csv(argv[0],names=["day","time","open","high","low","close","volume"])
		Q= pd.read_csv(argv[1],names=["day","time","open","high","low","close","volume"])


		k = pair_gap(S, Q)

		file = "data/"+argv[2]+argv[3]+"pair.csv"
		k.to_csv(file)
		end = time.time()

		return file




