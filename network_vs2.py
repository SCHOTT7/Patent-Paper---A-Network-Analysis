# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 15:37:40 2022

@author: Victo
"""

import pandas as pd
import numpy as np
import re
import tqdm as tq

from pyvis.physics import Physics
from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt

pd.read_csv('C:\\Users\\Victo\\Desktop\\pro (1)\\M2\Cours\\dashboard\\patents_topics2.csv')
digital_patents = pd.read_csv('C:\\Users\\Victo\\Desktop\\pro (1)\\M2\Cours\\dashboard\\digital_patents.csv')
data_wos = pd.read_csv('C:\\Users\\Victo\\Desktop\\pro (1)\\M2\Cours\\dashboard\\data_wos_up.csv')


count_digit_patents = digital_patents.groupby(['country']).size().reset_index(name ="counts")


data_wos['affiliation'] = data_wos['C1'].str.replace(r"[\(\[].*?[\)\]]",'',regex=True).astype(str)

#data_wos['affiliation_2'] = data_wos['affiliation'].str.search(r'(?<=\,)(.*?)(?=\;)').astype(str)

x = re.findall('(?<=\,)(.*?)(?=\;)',data_wos['affiliation'][1])

data_wos['affiliation_splited']= data_wos['affiliation'].str.split(',')
data_wos['affiliation_last'] = ""

for i in tq.tqdm(range(len(data_wos))):
    if 'USA' in data_wos['affiliation_splited'][i][-1]:
        data_wos['affiliation_last'][i] = 'USA'
    else:
        data_wos['affiliation_last'][i] = data_wos['affiliation_splited'][i][-1]
    
    
data_wos['affiliation_others'] = ''
for i in tq.tqdm(range(len(data_wos))):
    aff = []
    length = len(data_wos['affiliation_splited'][i])
    for l in range(length):
        if ";" in data_wos['affiliation_splited'][i][l]:
            x = data_wos['affiliation_splited'][i][l]
            x = x.split(';')[0]
            if 'USA' in x:
                x = 'USA'
            aff.append(x)
    data_wos['affiliation_others'][i] = aff  

for i in tq.tqdm(range(len(data_wos))):
    data_wos['affiliation_others'][i].append(data_wos['affiliation_last'][i])
    
country_list= []
for i in range(len(data_wos)):
    for l in range(len(data_wos['affiliation_others'][i])):
        x = re.sub(' ','',data_wos['affiliation_others'][i][l]).lower()
        country_list.append(x)
    
unique_country = set(country_list)
print(unique_country)


                          
#TOPICS PROCESSING
data_wos['topics'] = data_wos['SC'].str.split(';')
topic_list = []
for i in range(len(data_wos)):
    if type(data_wos['topics'][i]) != float:
        for l in range(len(data_wos['topics'][i])):
            data_wos['topics'][i][l] = data_wos['topics'][i][l].lower()
            if data_wos['topics'][i][l][0] == ' ':
                data_wos['topics'][i][l] = data_wos['topics'][i][l][1:]
            topic_list.append(data_wos['topics'][i][l])
unique_topics = list(set(topic_list))
unique_topics = [topic.lower() for topic in unique_topics]


res_topic = pd.DataFrame()
data_wos['PY'] = data_wos['PY'].fillna('0')
data_wos = data_wos.fillna('')
from collections import Counter

counter = Counter(data_wos['topics'][0])
for i in data_wos['topics'][1:]: 
    counter.update(i)

c_r_tokeep = [x[0] for x in counter.most_common(25)]

data_wos['PY'] =(data_wos['PY']).astype(int, errors = 'ignore')



list_topics = pd.DataFrame(data_wos['topics'].to_list())

    

#TOPICS NETWORK
year = 2017
data_wos1 = data_wos[data_wos['PY']==year]
list_topics = pd.DataFrame(data_wos1['topics'].to_list())
u = (pd.get_dummies(list_topics, prefix ='', prefix_sep = '')
         .groupby(level = 0, axis=1)
         .sum())
    
v=u.T.dot(u)
    
#links = v.drop(columns = ['458bb','705oj','em5zq','en9vx','er9we','ez4ju'])
#links = links.drop(index = ['458bb','705oj','em5zq','en9vx','er9we','ez4ju'])
    

    
v.values[(np.r_[:len(v)], ) * 2] = 0 
    
links = v[c_r_tokeep]
links = links[links.index.isin(c_r_tokeep)]

topic_node_size = {}
for topi in  links.index.tolist():
    topic_node_size[topi] = sum(links[topi])
    #print(topi)
    #print(sum(links[topi]))





nx_graph = nx.from_pandas_adjacency(links)
scale = 0.05
#d = dict(nx_graph.degree)

topic_node_size.update((x, scale*y) for x, y in topic_node_size.items())
nx.set_node_attributes(nx_graph,topic_node_size,'size')
#nx.set_edges_attributes()



combi_rc = []
#Calcul edge width:
for r  in links.index:
    for c in links.columns:
        combi_rc.append(links.loc[r][c])

#nx.draw_networkx_edges(nx_graph, pos=nx.spring_layout(nx_graph), alpha=0.3, width=combi_rc, edge_color="m")
#nx.draw_networkx_nodes(nx_graph, pos=nx.spring_layout(nx_graph), node_color="#210070", alpha=0.9)

#nx.get_node_attributes(nx_graph, 'size')
nt = Network(height="850px", width="100%",bgcolor="#222222",font_color="white",directed=True)
nt.from_nx(nx_graph)
nt.toggle_physics(True)
nt.show_buttons(filter_ ='physics')
nt.force_atlas_2based(gravity = -1000,
                      spring_strength = 0.002,
                      spring_length=100)
nt.barnes_hut(spring_strength=0.006)
                     
nt.show('nx.html')




#G2 = Network(height="100px", width="75%",bgcolor="#222222",font_color="white",directed=True)
#G2.from_nx(nx_graph)
#G2.show("network_map.html")

#COUNTRY PROCESSING

for i in tq.tqdm(range(len(data_wos))):
    data_wos['affiliation_others'][i] = list(dict.fromkeys(data_wos['affiliation_others'][i]))


list_countries = pd.DataFrame(data_wos['affiliation_others'].to_list())
u = (pd.get_dummies(list_countries, prefix ='', prefix_sep = '')
    .groupby(level = 0, axis=1)
    .sum())

v=u.T.dot(u)

v.values[(np.r_[:len(v)], ) * 2] = 0




ctry_links = v.drop(columns =['',' *','nan'])
ctry_links = ctry_links.drop(index = ['',' *','nan'])


x = ctry_links.sum()

ctry_to_drop = []
for i in range(len(x)):
    if x[i] <= 25:
        ctry_to_drop.append(x.index[i])

ctry_links = ctry_links.drop(columns = ctry_to_drop, index = ctry_to_drop)
    
ctry_nodes = pd.DataFrame(data = ctry_links.index)
ctry_nodes['size'] = ctry_links.sum().tolist()


 


counter = Counter(data_wos['affiliation_others'][0])
for i in data_wos['affiliation_others'][1:]: 
    counter.update(i)

c_r_tokeep = [x[0] for x in counter.most_common(25)]

#COUNTRIES NETWORKS




for i in tq.tqdm(range(len(data_wos))):
        data_wos['affiliation_others'][i] = list(dict.fromkeys(data_wos['affiliation_others'][i]))
        
 
    
 
ctry_links = v[c_r_tokeep]
ctry_links = ctry_links[ctry_links.index.isin(c_r_tokeep)]
      
country_node_size = {}
for ctry in ctry_links.index.tolist():
    country_node_size[ctry]  = sum(ctry_links[ctry])

 
#ctry_to_drop = []
#for i in range(len(x)):
    #if x[i] <= 25:
    #   ctry_to_drop.append(x.index[i])
    
#ctry_links = ctry_links.drop(columns = ctry_to_drop, index = ctry_to_drop)
        
ctry_nodes = pd.DataFrame(data = ctry_links.index)
ctry_nodes['size'] = ctry_links.sum().tolist()
nx_graph = nx.from_pandas_adjacency(ctry_links)
scale = 0.03
    #d = dict(nx_graph.degree)
country_node_size.update((x, scale*y) for x, y in country_node_size.items())
nx.set_node_attributes(nx_graph, country_node_size,'size')
    #nx.set_edges_attributes()
    #nx.draw_networkx_labels(nx_graph,pos = nx.spring_layout(nx_graph), font_size = 40)
    
    
    #nx.get_node_attributes(nx_graph, 'size')
nt = Network(height="1500px", width="85%",bgcolor="white",font_color="black",directed=True)
nt.from_nx(nx_graph)
nt.toggle_physics(True)
nt.show_buttons()
nt.force_atlas_2based(gravity = -1000,
                        spring_strength = 0.002,
                        spring_length=100)
nt.barnes_hut(spring_strength=0.006)
                         
nt.show('country_network'+'all_'+'.html')

 
    
 
    
      



def country_networks(data_w1, year):

    data_w = data_w1[data_w1['PY']==year]

    list_countries = pd.DataFrame(data_w['affiliation_others'].to_list())
    u = (pd.get_dummies(list_countries, prefix ='', prefix_sep = '')
        .groupby(level = 0, axis=1)
        .sum())
    
    v=u.T.dot(u)
    
    v.values[(np.r_[:len(v)], ) * 2] = 0
    
    #ctry_links = v.drop(columns =['',' *','nan'])
    #ctry_links = ctry_links.drop(index = ['',' *','nan'])
    
    
    counter = Counter(data_wos['affiliation_others'][0])
    for i in data_wos['affiliation_others'][1:]: 
        counter.update(i)
    c_r_tokeep = [x[0] for x in counter.most_common(25)]
    ctry_links = v[c_r_tokeep]
    ctry_links = ctry_links[ctry_links.index.isin(c_r_tokeep)]
          
    country_node_size = {}
    for ctry in ctry_links.index.tolist():
        country_node_size[ctry]  = sum(ctry_links[ctry])
    
    testing = data_w['affiliation_others']
    ctry_size2 = {}
    for cty in tq.tqdm(v.index.tolist()):
        ctry_size2[cty] = len(testing[testing.str.join(' ').str.contains(cty)])
    #ctry_to_drop = []
    #for i in range(len(x)):
        #if x[i] <= 25:
        #   ctry_to_drop.append(x.index[i])
        
    #ctry_links = ctry_links.drop(columns = ctry_to_drop, index = ctry_to_drop)
            
    ctry_nodes = pd.DataFrame(data = ctry_links.index)
    ctry_nodes['size'] = ctry_links.sum().tolist()
    nx_graph = nx.from_pandas_adjacency(ctry_links)
    scale = 0.03
        #d = dict(nx_graph.degree)
    ctry_size2.update((x, scale*y) for x, y in ctry_size2.items())
    nx.set_node_attributes(nx_graph, ctry_size2,'size')
        #nx.set_edges_attributes()
        #nx.draw_networkx_labels(nx_graph,pos = nx.spring_layout(nx_graph), font_size = 40)
        
       
        #nx.get_node_attributes(nx_graph, 'size')
    
    nt = Network(height="850px", width="100%",bgcolor="#222222",font_color="white",directed=False)
    nt.from_nx(nx_graph)
    nt.toggle_physics(True)
    #nt.show_buttons()
    nt.force_atlas_2based(gravity = -1000,
                            spring_strength = 0.002,
                            spring_length=100)
    nt.barnes_hut(spring_strength=0.006)
                             
    
    file = 'C:\\Users\\Victo\\Desktop\\pro (1)\\M2\\Cours\\dashboard\\my_networks\\ctry_per_years\\'
                    
    nt.show(file + 'country_network '+str(year)+'.html')





for year in range(2000,2019):
    country_networks(data_wos, year)
    
    
    
  
    
  
  
def topic_networks(data_w1,year):
    data_w = data_w1[data_w1['PY']==year]
    list_topics = pd.DataFrame(data_w['topics'].to_list())
    u = (pd.get_dummies(list_topics, prefix ='', prefix_sep = '')
         .groupby(level = 0, axis=1)
         .sum())
    
    v=u.T.dot(u)
    
    #links = v.drop(columns = ['458bb','705oj','em5zq','en9vx','er9we','ez4ju'])
    #links = links.drop(index = ['458bb','705oj','em5zq','en9vx','er9we','ez4ju'])
        
    counter = Counter(data_wos['topics'][0])
    for i in data_wos['topics'][1:]: 
        counter.update(i)
    
    
    
    c_r_tokeep = [x[0] for x in counter.most_common(25)]
        
    v.values[(np.r_[:len(v)], ) * 2] = 0 
        
    links = v[c_r_tokeep]
    links = links[links.index.isin(c_r_tokeep)]
    
    topic_node_size = {}
    for topi in  links.index.tolist():
        topic_node_size[topi] = sum(links[topi])
        #print(topi)
        #print(sum(links[topi]))
    
    
    
    
    
    nx_graph = nx.from_pandas_adjacency(links)
    scale = 0.05
    #d = dict(nx_graph.degree)
    
    topic_node_size.update((x, scale*y) for x, y in topic_node_size.items())
    nx.set_node_attributes(nx_graph,topic_node_size,'size')
    #nx.set_edges_attributes()
    
    
    
    combi_rc = []
    #Calcul edge width:
    for r  in links.index:
        for c in links.columns:
            combi_rc.append(links.loc[r][c])
    
    #nx.draw_networkx_edges(nx_graph, pos=nx.spring_layout(nx_graph), alpha=0.3, width=combi_rc, edge_color="m")
    #nx.draw_networkx_nodes(nx_graph, pos=nx.spring_layout(nx_graph), node_color="#210070", alpha=0.9)
    
    #nx.get_node_attributes(nx_graph, 'size')
    nt = Network(height="850px", width="100%",bgcolor="#222222",font_color="white",directed=False)
    nt.from_nx(nx_graph)
    nt.toggle_physics(True)
    #nt.show_buttons(filter_ ='physics')
    nt.force_atlas_2based(gravity = -1000,
                          spring_strength = 0.002,
                          spring_length=100)
    nt.barnes_hut(spring_strength=0.006)
    
    file = 'C:\\Users\\Victo\\Desktop\\pro (1)\\M2\\Cours\\dashboard\\my_networks\\topics_per_years\\'
                    
    nt.show(file + 'main_topics '+str(year)+'.html')
    
for year in range(2000,2019):
    topic_networks(data_wos, year)  
  
    
#Create several network-plots about top country-topics combinations


def in_ctry_ntw(data,ctry):
    data_w = data[data['AF'].str.contains(str(ctry), case = False)]
    data_w = data[(data['affiliation_others'].str.join(' ')).str.contains(ctry, case =False)]

        
    list_topics = pd.DataFrame(data_w['topics'].to_list())
    u = (pd.get_dummies(list_topics, prefix ='', prefix_sep = '')
         .groupby(level = 0, axis=1)
         .sum())
    
    v=u.T.dot(u)
    
    #links = v.drop(columns = ['458bb','705oj','em5zq','en9vx','er9we','ez4ju'])
    #links = links.drop(index = ['458bb','705oj','em5zq','en9vx','er9we','ez4ju'])
        
    counter = Counter(data_w['topics'][data_w['topics'].index.tolist()[0]])
    for i in data_w['topics'][data_w['topics'].index.tolist()[0]:]: 
        counter.update(i)
    
    c_r_tokeep = [x[0] for x in counter.most_common(25)]
    #print(ctry+' ')
    #print(c_r_tokeep)    
    v.values[(np.r_[:len(v)], ) * 2] = 0 
        
    links = v[c_r_tokeep]
    links = links[links.index.isin(c_r_tokeep)]
    
    topic_node_size = {}
    for topi in  links.index.tolist():
        topic_node_size[topi] = sum(links[topi])
        #print(topi)
        #print(sum(links[topi]))
    
    
    
    
    
    nx_graph = nx.from_pandas_adjacency(links)
    scale = 0.05
    #d = dict(nx_graph.degree)
    
    topic_node_size.update((x, scale*y) for x, y in topic_node_size.items())
    nx.set_node_attributes(nx_graph,topic_node_size,'size')
    #nx.set_edges_attributes()
    
    
    
    combi_rc = []
    #Calcul edge width:
    for r  in links.index:
        for c in links.columns:
            combi_rc.append(links.loc[r][c])
    
    #nx.draw_networkx_edges(nx_graph, pos=nx.spring_layout(nx_graph), alpha=0.3, width=combi_rc, edge_color="m")
    #nx.draw_networkx_nodes(nx_graph, pos=nx.spring_layout(nx_graph), node_color="#210070", alpha=0.9)
    
    #nx.get_node_attributes(nx_graph, 'size')
    nt = Network(height="850px", width="100%",bgcolor="#222222",font_color="white",directed=False)
    nt.from_nx(nx_graph)
    nt.toggle_physics(True)
    #nt.show_buttons(filter_ ='physics')
    nt.force_atlas_2based(gravity = -1000,
                          spring_strength = 0.002,
                          spring_length=100)
    nt.barnes_hut(spring_strength=0.006)
    
    file = 'C:\\Users\\Victo\\Desktop\\pro (1)\\M2\\Cours\\dashboard\\my_networks\\ctry_topics\\'

    nt.show(file+'main topics network in '+str(ctry)+' (2000-2018).html')  




for cty in ctry_links.index.tolist():
    try:
        in_ctry_ntw(data_wos, ctry=cty) 
    except:
        pass 
    
 
    

testing = data_wos['affiliation_others']
ctry_size2 = {}
for cty in tq.tqdm(v.index.tolist()):
    ctry_size2[cty] = len(testing[testing.str.join(' ').str.contains(cty)])
