# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 18:48:47 2018

@author: James
"""

import numpy as np
import pandas as pd
import itertools as it

rfile = np.loadtxt("data3.data")

n_rfile = rfile.shape[0]
n_trans = 1000
#t_len = 30
n_item = 1000
minsup = 80
minconf = 0.6
level = []

#data preprocessing
start =1
trans_list = []
trans_tmp = []
count_arr = np.zeros(n_item+1)

for i in range(n_rfile):
    if(start == rfile[i,0]):
        trans_tmp.append(rfile[i,2])
    else:
        if trans_tmp:
            trans_list.append(list(trans_tmp))
            trans_tmp = []
            start = start+1
            trans_tmp.append(rfile[i,2])
    count_arr[int(rfile[i,2])] = count_arr[int(rfile[i,2])] +1

trans_list.append(list(trans_tmp))


names = []
names.append("ID")
transac = []
for num in range(n_item):
    strr = "Item" + str(num)
    names.append(strr)
for num in range(n_trans):
    strr = "Trans" + str(num)
    transac.append(strr)
   
names = pd.DataFrame(names)
transac = pd.DataFrame(transac)

df = []
for rows in range(n_trans):
    df.append([None for _ in range(1000)])
    


for i in range(len(trans_list)):
    for j in range(n_item):
        df[i][j] = ""
    for items in trans_list[i]:
        items = int(items)
        df[i][items] = "yes"

  
df = pd.DataFrame(df)

droplist = []
for ind in range(n_item):
    count = False
    for tra in range(n_trans):
        if df.iloc[tra, ind] == "yes":
            count = True
            break
    if count == False:
        droplist.append(ind+1)

df = pd.concat([transac, df], axis=1)
df.columns = names

df = pd.DataFrame(df, columns=names)
df = df.drop(df.columns[droplist], axis=1)

df.to_csv('data3.csv', index=False)


