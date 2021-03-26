# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 13:53:24 2020

@author: gamma
"""

from __future__ import absolute_import
import transitfeed
import json
from os import listdir
from os.path import isfile, join
from io import open
import math
def time_between_stops(id1, id2, projected_file):
    stop_features=projected_file['features']
    x1=stop_features[int(id1)]['geometry']['coordinates'][0]
    y1=stop_features[int(id1)]['geometry']['coordinates'][1]
    x2=stop_features[int(id2)]['geometry']['coordinates'][0]
    y2=stop_features[int(id2)]['geometry']['coordinates'][1]
    #print math.sqrt((x2-x1)**2+(y2-y1)**2)//5
    return math.sqrt((x2-x1)**2+(y2-y1)**2)//5
def one_route(name, dictionary, stop_features, schedule):
    import datetime
    time=3600*7
    stop=[]
    route=schedule.AddRoute(short_name=name, long_name=name+'_route', route_type='Bus')
    for i in dictionary.keys():
        stops=dictionary[i].split('-')
        for st in range(len(stops)):
            x1=stop_features[int(stops[st])]['geometry']['coordinates'][0]
            y1=stop_features[int(stops[st])]['geometry']['coordinates'][1]
            stop.append(schedule.AddStop(lng=x1, lat=y1, name=stops[st]))
        for t in range(3600*7, 3600*22, 600):
            time=t
            #veh_for_dir=num_of_veh[i]
            #print(stops)
            trip=route.AddTrip(schedule)
            for st in range(len(stops)-1):
                trip.AddStopTime(stop[st], stop_time=str(datetime.timedelta(seconds=time)))
                time+=time_between_stops(int(stops[st]), int(stops[st+1]), projected)
    print(schedule)
    
M1={'M1_0':'216-217-218-219-220-221-222-223-84-195-196-85-129-13-136-137-138-139-140-141-142-143-144-145-146-147-148-149-150-151-152-337-338-339', 'M1_1':
    '28-29-30-31-32-33-34-35-36-37-38-39-40-41-42-85-129-43-44-161-162-163-187-188-189-190-191-250'}
M2={'M2_0':'309-100-101-102-1-2-103-104-105-106-11-12-13-107-108-109-110-61-347', 'M2_1':
    '347-65-66-67-68-69-70-71-41-42-95-96-97-98-47-48-49-50-51-52-234-99'}
M3={'M3_0':'129-43-44-161-162-293-294-295-267-268-269-270-10-11-12-85-129','M3_1':
    '129-95-96-242-74-75-76-77-78-79-80-81-82-83-84-195-196-85-129'}
M4={'M4_0':'84-45-46-272-273-78-79-274-247-248-271-222-223-84','M4_1':
    '161-162-163-164-3-266-267-318-340-324-325-161'}
M5={'M5_0':'308-212-213-214-101-102-1-2-103-104-105-106-16-17-18-19-20-21-22-23-252-296-151-152-337-338-339','M5_1':
    '339-253-297-298-299-300-301-302-303-304-305-306-97-98-47-48-49-50-51-52-53-54-55-226-307-308'}
M6={'M6_0':'221-222-223-84-195-196-85-129-13-14-15-72-73-243-244-245-246-263-232-0-221', 'M6_1':
    '187-227-278-4-5-6-7-8-9-258-259-260-261-41-42-85-129-43-44-161-162-163-187'}

num_of_veh={'M1_0': 8, 'M1_1': 8, 'M2_0': 6, 'M2_1': 6, 'M3_0': 3, 'M3_1': 3, 'M4_0': 3, 'M4_1': 3, 'M5_0': 9, 'M5_1': 9, 'M6_0': 5, 'M6_1': 5}

stops=json.load(open(r'C:\matsim\gen2\platforms.geojson', encoding='utf-8'))
projected=json.load(open(r'C:\matsim\gen2\platforms_32655.geojson', encoding='utf-8'))
#print(stops['features'])

schedule = transitfeed.Schedule()
schedule.AddAgency("MATSim interpreted routes", u"http://transmetrika.com", "Russia/Yuzhno-Sakhalinsk")
service_period = schedule.GetDefaultServicePeriod()
service_period.SetStartDate(u"20200101")
service_period.SetEndDate(u"20200102")
service_period.SetWeekdayService(True)
service_period.SetDateHasService('20070704', False)

one_route('M1', M1, projected['features'], schedule)
one_route('M2', M2, projected['features'], schedule)
one_route('M3', M3, projected['features'], schedule)
one_route('M4', M4, projected['features'], schedule)
one_route('M5', M5, projected['features'], schedule)
one_route('M6', M6, projected['features'], schedule)
#schedule.Validate()
schedule.WriteGoogleTransitFeed('C:\matsim\gen2\matsim_results_gtfs_2.zip')
