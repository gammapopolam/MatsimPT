# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 13:53:24 2020

@author: gamma
"""

import transitfeed
import json
from os import listdir
from os.path import isfile, join
print('''
позиции:
[0] - путь сохранения GTFS_Dummy
[1] - x_y пара остановки №1
[2] - x_y пара остановки №2
по умолчанию время прибытия с остановки 1 на остановку 2 - 3 минуты, т.е. время 22:00:00 - 22:03:00
''')

inputdata=raw_input('Введите данные').split(' ')
print(inputdata)
time1='22:00:00'
time2='22:00:10'

path=inputdata[0]
schedule = transitfeed.Schedule()
schedule.AddAgency("Transmetrika Agency", "http://transmetrika.com","Russia/Dummygorsk")
service_period = schedule.GetDefaultServicePeriod()
service_period.SetStartDate("20200101")
service_period.SetEndDate("20200102")
service_period.SetWeekdayService(True)
#service_period.SetDateHasService('20070704', False)

stop1 = schedule.AddStop(lng=float(inputdata[1].split('_')[1]), lat=float(inputdata[1].split('_')[0]), name="D1_1")
stop2 = schedule.AddStop(lng=float(inputdata[2].split('_')[1]), lat=float(inputdata[2].split('_')[0]), name="D1_2")

route=schedule.AddRoute(short_name='D1', long_name='Dummy Line 1', route_type='Bus')
trip=route.AddTrip(schedule, headsign='D1')
trip.AddStopTime(stop1, stop_time=str(time1))
trip.AddStopTime(stop2, stop_time=str(time2))


schedule.Validate()
schedule.WriteGoogleTransitFeed(path+r'\\GTFS_dummy.zip')
print('Генерация завершена!')
print('Путь GTFS:')
print(path+r'\\GTFS_dummy.zip')
