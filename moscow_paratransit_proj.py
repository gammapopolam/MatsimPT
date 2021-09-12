# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 16:27:11 2021
MOSCOW PARATRANSIT project
@author: Ivan
"""
import matsim
import random
import json
ctr=0
file=r'C:\Users\Ivan\moscow_paratransit\population.xml'
f_write=open(file, 'wb+')
writer = matsim.writers.PopulationWriter(f_write)
writer.start_population()
prokshino=[401286.899008200212847, 6161141.824788508936763]
popul=json.load(open(r'C:/Users/Ivan/moscow_paratransit/popul_2.geojson', mode='r', encoding='utf-8'))
for ft in range(len(popul['features'])):
    point=popul['features'][ft]['geometry']['coordinates'][0][0][0]
    agents=popul['features'][ft]['properties']['avg_popul']
    for i in range(agents//10):
        ctr+=1
        endtime_home=random.randrange(6.5*3600, 12*3600, 600)
        endtime_work=random.randrange(17*3600, 23*3600, 600)
        writer.start_person(f'person_{ctr}')
        writer.start_plan(selected=True)
        writer.add_activity(type='home', x=point[0], y=point[1], end_time=endtime_home)
        writer.add_leg(mode="pt")
        writer.add_activity(type='work', x=prokshino[0], y=prokshino[1], end_time=endtime_work)
        writer.add_leg(mode="pt")
        writer.add_activity(type='home', x=point[0], y=point[1])
        writer.end_plan()
        writer.end_person()
writer.end_population()
