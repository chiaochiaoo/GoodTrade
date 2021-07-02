import pandas as pd
import numpy as np

def ts_to_min(ts):
	ts = int(ts)
	m = ts//60
	s = ts%60

	return str(m)+":"+str(s)


s = pd.read_csv("tttt.csv")

st = []


for index, row in s.iterrows():
    st.append(str(int(row["reversal_timer"]//60)) + ":" + str(int(row["reversal_timer"]%60)))

s.loc[:,"Signal Time"] = np.array(st)

keep = ['Symbol', "Signal Time", 'rel vol', 'SC', 'reversalside','reversal_score',
       'Signal Time',]

for i in s.columns:
	if i not in keep:
		s.pop(i)
print(s.head)
s.to_csv("test.csv")