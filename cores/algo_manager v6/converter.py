import json
import os
import csv
dates = {}
with open('2022_10.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    c = 0
    for row in spamreader:
        if c>=1:
            k = ', '.join(row).split(",")
            print(', '.join(row).split(","))
            
            d = k[0]
            a = k[2]
            r = k[3]
            
            if d not in dates:
                dates[d] = {}
                dates[d]["algos"] = {}
            else:
                dates[d]["algos"][a] = r
        c+=1
with open('2022_11.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    c = 0
    for row in spamreader:
        if c>=1:
            k = ', '.join(row).split(",")
            print(', '.join(row).split(","))
            
            d = k[0]
            a = k[2]
            r = k[3]
            
            if d not in dates:
                dates[d] = {}
                dates[d]["algos"] = {}
            else:
                dates[d]["algos"][a] = r
        c+=1
        
for i in dates.keys():
    with open(i+'.json', 'w') as f:
        json.dump(dates[i], f)