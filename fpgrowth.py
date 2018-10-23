# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 16:31:48 2018

@author: James
"""

import numpy as np
import pandas as pd
import itertools as it
import copy

rfile = np.loadtxt("data3.data")
#rfile = np.loadtxt("data_mate.txt")
#print(rfile.shape)

#rfile = [[1,1,1],[1,1,2],[1,1,3],[2,2,2],[2,2,4],[3,3,2],[3,3,5],[4,4,1],[4,4,2],[4,4,4],[5,5,1],[5,5,5],[6,6,2],[6,6,5],[7,7,1],[7,7,5],[8,8,1],[8,8,2],[8,8,3],[8,8,5],[9,9,1],[9,9,2],[9,9,5]]
#rfile = np.array(rfile, dtype=float)
#%%
class FPTree(object):
    def __init__(self):
        self.data = None
        self.parent = None
        self.children = []
        self.prefix = []
        self.count = 1

class TableNode(object):
    def __init__(self):
        self.key = None
        self.value = None
        self.nodes = []
        
n_rfile = rfile.shape[0]
n_trans = 1000
n_item = 1000
minsup = 80
minconf = 0.5
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


fp_list = copy.deepcopy(trans_list)

#check support, if lower, remove
### considered to be function
def powerset(iterable, item):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return it.chain.from_iterable(it.combinations(s, r) for r in range(1, item+1))


#%%
dict_l = []
dict_r = []
for i in range(n_item+1):
    if count_arr[i] >= minsup:
        dict_l.append(i)
        dict_r.append(count_arr[i])

table = dict(zip(dict_l, dict_r))
table = sorted(table.items(), key=lambda x: x[1], reverse=True)

#%%

map_table = copy.deepcopy(table)
#to negative, in order to rid of non frequent set
indexneg = 0
for i in range(len(table)):
    indexneg = indexneg-1
    a = []
    c = []
    a.append(indexneg)
    c.append(map_table[i][0])
    map_table[i] = tuple(c) + tuple(a)

for i in range(n_trans):
    for j in range(len(fp_list[i])):
        for check in range(len(table)):
            if(fp_list[i][j] == map_table[check][0]):
                fp_list[i][j] = map_table[check][1]
                break
#%%
for i in range(n_trans):
    fp_list[i] = [item for item in fp_list[i] if item < 0]
    fp_list[i].sort(reverse=True)
    
for i in range(n_trans):
    for j in range(len(fp_list[i])):
        for check in range(len(table)):
            if(fp_list[i][j] == map_table[check][1]):
                fp_list[i][j] = map_table[check][0]
                break


#%%
#BUILD TREE LA

#bulid table
root_table = TableNode()
for i in range(len(table)):
    newnode = TableNode()
    newnode.key = table[i][0]
    newnode.value = table[i][1]
    root_table.nodes.append(newnode)

#%%
#build fp tree
#aaa = root_table.nodes
debuglist = []

root_fp = FPTree()
for i in range(len(fp_list)):
    nodept = root_fp
    debuglist.append("G")
    for items in fp_list[i]:
        found = False
        for nodes_inchild in nodept.children:
            if nodes_inchild.data == items:
                nodes_inchild.count = nodes_inchild.count + 1
                found = True
                nodept = nodes_inchild
                debuglist.append(nodept.data)
                break
        if found == False:
            newnode = FPTree()
            newnode.data = items
            newnode.parent = nodept
            list1 = nodept.prefix
            list2 = [nodept.data]
            newnode.prefix = list(list1+list2)
            nodept.children.append(newnode)
            debuglist.append(newnode.data)
            for tablept in root_table.nodes:
                if newnode.data == tablept.key:
                    tablept.nodes.append(newnode)
                    break
            nodept = newnode
        
print("BUILD FINISH")        
#%%
aaa = root_fp.children  #debug use
ttt = root_table.nodes
#%%
def recursive_find(firstind, tablept, level, levelnum, realprefix):
    tmpset = []
    pdset = []
    pdcount = []
    weight = []
    addset = []
    reverseprefix = []
    runnext = False

    for leaffunc in tablept.nodes:
        single_count = leaffunc.count
        runnext = False
        reverseprefix = list(reversed(realprefix))
        reverseprefix = reverseprefix[1:]
        for findind in reverseprefix:
            while leaffunc.data != findind:
                leaffunc = leaffunc.parent
                if leaffunc.data == None:
                    runnext = True
                    break
            if runnext == True:
                break
        if runnext == True:
            continue
        
        prefix = leaffunc.prefix
        prefix = list(filter(None.__ne__, prefix))
        tmpset.append(prefix)
        weight.append(single_count)
            
    pdset = np.zeros((len(tmpset), n_item+1))
    for i in range(len(tmpset)):
        pdset[i, tmpset[i]] = pdset[i, tmpset[i]] + weight[i]
    pdset =  pd.DataFrame(pdset)
    pdcount = pdset.sum()
    pdcount = pdcount[pdcount >= minsup]

    if pdcount.empty:
        return level
    
    #recursive starts here
    for ind in pdcount.index:
        addset = list(realprefix)
        level[levelnum].append(list(list([ind])+addset))
        level = recursive_find(ind, tablept, level, levelnum+1, list(list([ind])+addset))
        
    return level

#%%
#generate frequent dataset
root_table.nodes = list(reversed(root_table.nodes))
ttt = root_table.nodes #debug


tmpset = []
pdset = []
pdcount = []
weight = []
for i in range(15):
    level.append([])


for x in table:
    level[0].append(x[0])
    
    
for tablept in root_table.nodes:
    tmpset = []
    pdcount = []
    weight = []
    for leaf in tablept.nodes:
        single_count = leaf.count
        prefix = leaf.prefix
        prefix = list(filter(None.__ne__, prefix))
        tmpset.append(prefix)
        weight.append(single_count)
            
    pdset = np.zeros((len(tmpset), n_item+1))
    for i in range(len(tmpset)):
        pdset[i, tmpset[i]] = pdset[i, tmpset[i]] + weight[i]
    pdset =  pd.DataFrame(pdset)
    pdcount = pdset.sum()

    pdcount = pdcount[pdcount >= minsup]
    #recursive starts here?
    for ind in pdcount.index:
        addset = [tablept.key]
        level[1].append(list(list([ind])+addset))
        level = recursive_find(ind, tablept, level, 2, list(list([ind])+addset))
        
     

#%%
import csv


with open('sup80_0.csv','w') as out:
    csv_out=csv.writer(out)
    csv_out.writerow(level[0])
with open('sup80_1.csv','w') as out:
    csv_out=csv.writer(out)
    for row in level[1]:
        csv_out.writerow(row)
with open('sup80_2.csv','w') as out:
    csv_out=csv.writer(out)
    for row in level[2]:
        csv_out.writerow(row)        
#%%
lastlevel = 0
def search_conf(left, landr):
    countl = 0
    countall = 0
    for j in range(len(trans_list)):
            if set(left).issubset(trans_list[j]):
                countl = countl +1
            if set(landr).issubset(trans_list[j]):
                countall = countall +1

    confi = countall/countl
    return confi
    
result = []

for i in range(15):
    if len(level[i])==0:
        lastlevel = i
        break
              
#calculate confidence

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
       
with open('result800.5.csv','w') as out:
    csv_out=csv.writer(out)
    for row in result:
        csv_out.writerow(row)
