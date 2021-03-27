# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 15:32:15 2021

@author: Administrator
"""

import matsim
import math
import json
import random
# import pandas as pd
# from collections import defaultdict

def some_extra_cords(extra): #экстра-точки в которых могут быть большие скопления за день 
    extra_list=[]
    f=json.load(open(extra, encoding='utf-8'))
    for i in range(len(f['features'])):
        # if features[i]['properties']["building"]=="apartments" or features[i]['properties']["building"]=="house" or features[i]['properties']["building"]=="semidetached_house":
        home={'count':f['features'][i]['properties']["count"], "geometry": (f['features'][i]["geometry"]["coordinates"][1], f['features'][i]["geometry"]["coordinates"][0])}
        extra_list.append(home)
    return extra_list

def apartments_list(file):
    apartments_list=[]
    f=json.load(open(file, encoding='utf-8'))
    for i in range(len(f['features'])):
        # if features[i]['properties']["building"]=="apartments" or features[i]['properties']["building"]=="house" or features[i]['properties']["building"]=="semidetached_house":
        home={'id':f['features'][i]['properties']["osm_id"], "geometry": (f['features'][i]["geometry"]["coordinates"][1], f['features'][i]["geometry"]["coordinates"][0])}
        apartments_list.append(home)
    return apartments_list

def acts_list(file):
    acts_list=[]
    f=json.load(open(file, encoding='utf-8'))
    for i in range(len(f['features'])):
        count=int(f['features'][i]['properties']['count_empl'])
#        print(features[i]['properties']["ID"], count)
#        print(features[i]["geometry"])
        if count!=0 and f['features'][i]["geometry"]!=None:
            # print(f['features'][i])
            act={'id':f['features'][i]['properties']["ID"], "count_empl":count, "geometry": (f['features'][i]["geometry"]["coordinates"][1], f['features'][i]["geometry"]["coordinates"][0])}
            acts_list.append(act)
    return acts_list


def length(x1, y1, x2, y2):
    length=math.sqrt((x2-x1)**2+(y2-y1)**2)
    return length


def random_time():
    endtime_h=random.randrange(6*3600, 17*3600)
    endtime_w=random.randrange(endtime_h+2*3600, 21*3600)
    return endtime_h, endtime_w

def write_plans(plans_file, person_id, buildingslist):
    nak=0
    for i in range(len(buildingslist[1])):
        unique_nextact=buildingslist[1][i]
        # print(unique_nextact['count_empl'])
        nak=nak+unique_nextact['count_empl']
        for ctr in range(unique_nextact['count_empl']):
            unique_home=random.choice(buildingslist[0])
            hx, hy = unique_home["geometry"][1], unique_home["geometry"][0]
            ax, ay = unique_nextact["geometry"][1],  unique_nextact["geometry"][0]
            endtime_h, endtime_w = random_time()
            checker=length(hx, hy, ax, ay)
            while checker<2000:
                unique_home=random.choice(buildingslist[0])
                hx, hy = unique_home["geometry"][1], unique_home["geometry"][0]
                checker=length(hx, hy, ax, ay)
            else:
                writer.start_person(person_id+'_'+str(i)+'_'+str(ctr))
                writer.start_plan(selected=True)
                writer.add_activity(type='home', x=hx, y=hy, end_time=endtime_h)
                writer.add_leg(mode="pt")
                writer.add_activity(type='work', x=ax, y=ay, end_time=endtime_w)
                writer.add_leg(mode="pt")
                writer.add_activity(type='home', x=hx, y=hy)
                writer.end_plan()
                writer.end_person()
    print(nak)
def write_extra(plans_file, person_id, buildingslist):
    nak=0
    for i in range(len(buildingslist[2])):
        unique_nextact=buildingslist[2][i]
        # print(unique_nextact['count'])
        nak=nak+unique_nextact['count']
        for ctr in range(unique_nextact['count']):
            unique_home=random.choice(buildingslist[0])
            hx, hy = unique_home["geometry"][1], unique_home["geometry"][0]
            ax, ay = unique_nextact["geometry"][1],  unique_nextact["geometry"][0]
            endtime_h, endtime_w = random_time()
            checker=length(hx, hy, ax, ay)
            while checker<2000:
                unique_home=random.choice(buildingslist[0])
                hx, hy = unique_home["geometry"][1], unique_home["geometry"][0]
                checker=length(hx, hy, ax, ay)
            else:
                writer.start_person(person_id+'_'+str(i)+'_'+str(ctr))
                writer.start_plan(selected=True)
                writer.add_activity(type='home', x=hx, y=hy, end_time=endtime_h)
                writer.add_leg(mode="pt")
                writer.add_activity(type='work', x=ax, y=ay, end_time=endtime_w)
                writer.add_leg(mode="pt")
                writer.add_activity(type='home', x=hx, y=hy)
                writer.end_plan()
                writer.end_person()
    print(nak)
    
    

acts=r'C:/Users/gammapopolam/Google Диск/Южно-Сахалинск MATsim/популяция/acts_32655_2_centroid.geojson'
act_features=json.load(open(acts, encoding='utf-8'))['features']
apartments=r'C:/Users/gammapopolam/Google Диск/Южно-Сахалинск MATsim/популяция/apartments_32655.geojson'
extra=r'C:/Users/gammapopolam/Google Диск/Южно-Сахалинск MATsim/популяция/extra_acts.geojson'
extra_features=json.load(open(extra, encoding='utf-8'))['features']
print(len(extra_features), len(extra_features)+len(act_features))
buildingslist=[apartments_list(apartments), acts_list(acts), some_extra_cords(extra)]

file=r"C:\matsim\gen2\input_2\population.xml"
with open(file, 'wb+') as f_write:
    writer = matsim.writers.PopulationWriter(f_write)
    writer.start_population()
    personid='person_id'+'0'
    write_plans(file, personid, buildingslist) #без экстра точек
    personid='person_id'+'1'
    write_extra(file, personid, buildingslist)
    writer.end_population()
