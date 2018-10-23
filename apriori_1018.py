# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import itertools as it
rfile = np.loadtxt("data3.data")
#rfile = pd.read_csv("dataset.csv")

#%%
print(rfile.shape)
#print(max(rfile[:,0]))
#%%
def powerset(iterable, item):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return it.chain.from_iterable(it.combinations(s, r) for r in range(item, item+1))



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
for i in range(n_rfile):
    if(start == rfile[i,0]):
        trans_tmp.append(rfile[i,2])
    else:
        if trans_tmp:
            trans_list.append(tuple(trans_tmp))
            trans_tmp = []
            start = start+1
            trans_tmp.append(rfile[i,2])
trans_list.append(tuple(trans_tmp))
print(len(trans_list))

l = [x for x in range(1,n_item+1)]
level.append(list(powerset(l, 1)))  ### first layer
#aa = [(1)]


#check support, if lower, remove
### considered to be function
def delete_lowsup(leveln):
    count = 0
    good_list = []
    for iii in range(len(leveln)):
        for jjj in range(len(trans_list)):
            if set(leveln[iii]).issubset(trans_list[jjj]):
                count = count +1
        print(leveln[iii], count, iii, len(leveln))
        #if count < minsup:
            #rm_list.append(leveln[iii])
        if count >= minsup:
            good_list.append(leveln[iii])
        count = 0
    #leveln = set(leveln) - set(rm_list)
    leveln = set(good_list)
    return leveln


#combine seperate tuples
def combine_tuple(leveln):
    for i in range(len(leveln)):
        tmp = tuple()
        for items in leveln[i]:
            tmp = tmp + items
        leveln[i] = tmp
    return leveln


level[0] = list(delete_lowsup(level[0]))
#%%
level.append(list(powerset(level[0], 2)))
#%%

combine_tuple(level[1])
#level[1] = sorted(level[1], key=lambda tup: tup[1])
#level[1] = sorted(level[1], key=lambda tup: tup[0])

level[1] = list(delete_lowsup(level[1]))

#%%


def powerset_leveln(leveln, leveln1, n):
    for i in range(len(leveln1)):
        for j in range(i,len(leveln1)):
            newlist = list(np.unique([leveln1[i], leveln1[j]]))
            if len(newlist) == n:
                newlist = list(powerset(newlist,n))
                for k in newlist:
                    leveln.append(k)
    return leveln


#%%
lastlevel = 0
for levelnum in range(2,1000):
    if len(level[levelnum-1])==0:
        break
    
    level.append([])
    level[levelnum] = powerset_leveln(level[levelnum], level[levelnum-1], levelnum+1)
    level[levelnum] = list(set(level[levelnum])) #remove duplicates
    level[levelnum] = list(delete_lowsup(level[levelnum]))
    lastlevel = levelnum
#%%



#%%

#save files
import csv


with open('sup80_02.csv','w') as out:
    csv_out=csv.writer(out)
    for row in level[0]:
        csv_out.writerow(row)
with open('sup80_12.csv','w') as out:
    csv_out=csv.writer(out)
    for row in level[1]:
        csv_out.writerow(row)
with open('sup80_22.csv','w') as out:
    csv_out=csv.writer(out)
    for row in level[2]:
        csv_out.writerow(row)        
#%%
#kk = pd.read_csv("sup50_2.csv")
#lastlevel = 3
def search_conf(left, landr):
    countl = 0
    countall = 0
    for j in range(len(trans_list)):
            if set(left).issubset(trans_list[j]):
                countl = countl +1
            if set(landr).issubset(trans_list[j]):
                countall = countall +1
    #print(countl, countall)
    confi = countall/countl
    return confi
    
result = []                
#calculate confidence
minconf = 0.6
for i in reversed(range(1,lastlevel)):
    for items in level[i]:
        newlist = list(set(items))
        combin_items = list(it.chain.from_iterable(it.combinations(newlist, r) for r in range(1,i+1)))
        for left in combin_items:
            confi = search_conf(left, newlist)
            print(left, newlist, confi)
            if confi >= minconf:
                right = tuple(set(newlist) - set(left))
                result.append([left, "->", right, confi])
       
with open('result802.csv','w') as out:
    csv_out=csv.writer(out)
    for row in result:
        csv_out.writerow(row)