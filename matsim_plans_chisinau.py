# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 02:34:54 2021

@author: gamma
"""

# import geojson
import json
import random
import matsim
import math

def random_time():
    endtime_h=random.randrange(6*3600, 17*3600)
    endtime_w=random.randrange(endtime_h+2*3600, 21*3600)
    return endtime_h, endtime_w
def length(hx, hy, wx, wy):
    length=math.sqrt((wx-hx)**2+(wy-hy)**2)
    return length


writer = matsim.writers.PopulationWriter(open("C:/Users/gamma/chisinau/chisinau_plans.xml", 'wb+'))
writer.start_population()
working_ppl = r'C:/Users/gamma/chisinau/working_ppl_points.geojson'
working_slots = r'C:/Users/gamma/chisinau/working_slots_points.geojson'
working_ppl_fet=json.load(open(working_ppl, encoding='utf-8'))['features']
working_slots_fet=json.load(open(working_slots, encoding='utf-8'))['features']

for i in range(len(working_ppl_fet)): #заполняем по одному человеку
    endtime_h, endtime_w=random_time()
    
    random_work = random.choice(working_slots_fet)
    
    hx, hy = working_ppl_fet[i]['geometry']['coordinates'][0], working_ppl_fet[i]['geometry']['coordinates'][1]
    wx, wy = random_work['geometry']['coordinates'][0], random_work['geometry']['coordinates'][1]
    checker=length(hx, hy, wx, wy)
    while checker<2000:
        if checker<2000 or checker>11000:
            random_work = random.choice(working_slots_fet)
            hx, hy = working_ppl_fet[i]['geometry']['coordinates'][0], working_ppl_fet[i]['geometry']['coordinates'][1]
            wx, wy = random_work['geometry']['coordinates'][0], random_work['geometry']['coordinates'][1]
            checker=length(hx, hy, wx, wy)
    else:
        working_slots_fet.pop(working_slots_fet.index(random_work))
        writer.start_person(f"person_id_{i}")
        writer.start_plan(selected=True)
        writer.add_activity(type='h', x=hx, y=hy, end_time=endtime_h)
        writer.add_leg(mode="pt")
        writer.add_activity(type='w', x=wx, y=wy, end_time=endtime_w)
        writer.add_leg(mode="pt")
        writer.add_activity(type='h', x=hx, y=hy)
        writer.end_plan()
        writer.end_person()
writer.end_population()
    