# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 00:29:38 2022

@author: Ivan
"""

import random
import json
import matsim
import math

def length(x1, y1, x2, y2):
    length=math.sqrt((x2-x1)**2+(y2-y1)**2)
    return length

def rebuild_data(j):
    act_list=[]
    for i in range(len(j['features'])):
        coord=j['features'][i]['geometry']['coordinates']
        props=j['features'][i]['properties']['shape_id']
        act_list.append({'coord':coord, 'shape_id':props})
    return act_list, unique_shape_id(act_list)

def unique_shape_id(act_list):
    shape_ids=[]
    for i in range(len(act_list)):
        act=act_list[i]
        shape_ids.append(act['shape_id'])
    return list(set(shape_ids))

def actlength(act_h, act_w):
    length=math.sqrt((act_h['coord'][0]-act_w['coord'][0])**2+(act_h['coord'][1]-act_w['coord'][1])**2)
    return length

def less(c):
    if c<=178:
        return True
    

file=r'C:/Users/gamma/glazov_ver2/agents/population.xml'
f_write=open(file, 'wb+')
writer = matsim.writers.PopulationWriter(f_write)
writer.start_population()

agents=json.load(open(r'C:/Users/gamma/glazov_ver2/agents_glazov.geojson', mode='r', encoding='utf-8'))
agents_r, unique_shape_ids=rebuild_data(agents)

c=len(agents_r)

while c>1:
    act_h=random.choice(agents_r)
    act_w=random.choice(agents_r)
    act_len=actlength(act_h, act_w)
    while act_len>=5500 or act_len<=1500:
        act_w=random.choice(agents_r)
        act_len=actlength(act_h, act_w)
    else:
        #куда без костылей
        if less(c):
            break
        else:
            agents_r.remove(act_h)
            agents_r.remove(act_w)
            endtime_h=random.randrange(6.5*3600, 11*3600)
            endtime_w=random.randrange((endtime_h+6*3600), (endtime_h+10*3600))
            writer.start_person(f'person_{c}')
            writer.start_plan(selected=True)
            writer.add_activity(type='home', x=act_h['coord'][0], y=act_h['coord'][1], end_time=endtime_h)
            writer.add_leg(mode="pt")
            writer.add_activity(type='work', x=act_w['coord'][0], y=act_w['coord'][1], end_time=endtime_w)
            writer.add_leg(mode="pt")
            writer.add_activity(type='home', x=act_h['coord'][0], y=act_h['coord'][1])
            writer.end_plan()
            writer.end_person()
            c=len(agents_r)
writer.end_population()