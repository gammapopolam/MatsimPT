# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 13:53:24 2020

@author: gamma
"""

import transitfeed
import json
from os import listdir
from os.path import isfile, join
schedule = transitfeed.Schedule()
schedule.AddAgency("Департамент Транспорта", "http://transmetrika.com",
                   "Russia/Yuzhno-Sakhalinsk")
service_period = schedule.GetDefaultServicePeriod()
service_period.SetStartDate("20200101")
service_period.SetEndDate("20200102")
service_period.SetWeekdayService(True)
#service_period.SetDateHasService('20070704', False)

def stops(file1, schedule): #обработка остановок и добавление их в словарь для доступа к их id и osmid
    print(len(file1['features']))
    dict_stops_loc={}
    dict_stops_id={}
    dict_stops_name={}
    for i in range(0, len(file1['features'])):
        feature=file1['features'][i]
        geometry=(feature['geometry']['coordinates'][0], feature['geometry']['coordinates'][1])
        yid=feature['properties']['yid']
        platform_name=feature['properties']['platform_name']
        
        dict_stops_loc[yid]=geometry
        dict_stops_name[yid]=platform_name
        stop=schedule.AddStop(geometry[1], geometry[0], name=yid)
        dict_stops_id[yid]=stop
    dictlist=[dict_stops_id, dict_stops_loc, dict_stops_name]
    return dictlist


def route(schedule, json_sched, dictlist):
    opened=json.load(open(json_sched))
    route=schedule.AddRoute(short_name=opened['name'], long_name=opened['directions'][0]['name'], route_type="Bus")
    for i in range(len(opened['directions'])): #направления
        for t in range(len(opened['directions'][i]['stops'][0]['comings'])):
            head=opened['directions'][i]['endName']
            trip=route.AddTrip(schedule, headsign=head)
            for j in range(len(opened['directions'][i]['stops'])): #остановки одного направления
                info=opened['directions'][i]['stops'][j]
                lng=float(info['zones'][0]['location'][0])
                lat=float(info['zones'][0]['location'][1])
                time=info['comings'][t]['time'][-8:]
                stop=dictlist[0][info['zones'][0]['id']]
                trip.AddStopTime(stop, stop_time=str(time))
                #print opened['name'], opened['directions'][0]['name'], head, info['zones'][0]['name'], time
            

#rt=r'C:\Users\gamma\Documents\matsim\matsim-12.0\examples\pt_yus\rts\1.json'
dictlist = stops(json.load(open(r'C:\Users\gamma\Documents\matsim\matsim-12.0\examples\pt_yus\stops_4326.geojson')), schedule)
mypath=r'C:\Users\gamma\Documents\matsim\matsim-12.0\examples\pt_yus\rts\few'
inputlist = [f for f in listdir(mypath) if isfile(join(mypath, f)) and '.json' in f]
for i in range(len(inputlist)):
    rt=mypath+'\\'+inputlist[i]
    route(schedule, rt, dictlist)
schedule.Validate()
schedule.WriteGoogleTransitFeed('C:\\Users\\gamma\\Documents\\matsim\\matsim-12.0\\examples\\pt_yus\\GTFS_few.zip')
