# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 12:52:07 2023

Пролазить в XML мне показалось ненадежным, поэтому написал скрипт,
который по образцу делает строки для MATSim TransitSchedule. Вручную они
добавляются в расписание и список техники.


@author: gamma
"""

start='05:45'
finish='21:43'

start_h, start_m=start.split(':')
start_m=int(start_m)
start_m+=int(start_h)*60


finish_h, finish_m=finish.split(':')
finish_m=int(finish_m)
finish_m+=int(finish_h)*60
ctr=0
additions=[]
vehs=[]
while finish_m>=start_m:
    # print(finish_m)
    step_h=finish_m//60
    step_m=finish_m%60
    finish_m-=5
    # print(step_h, step_m)
    if step_h<=9:
        if step_m<=9:
            additions.append(f'				<departure id="a1_5_{ctr}" departureTime="0{step_h}:0{step_m}:00" vehicleRefId="a1_5_{ctr}"/>')
        else:
            additions.append(f'				<departure id="a1_5_{ctr}" departureTime="0{step_h}:{step_m}:00" vehicleRefId="a1_5_{ctr}"/>')
    else:
        if step_m<=9:
            additions.append(f'				<departure id="a1_5_{ctr}" departureTime="{step_h}:0{step_m}:00" vehicleRefId="a1_5_{ctr}"/>')
        else:
            additions.append(f'				<departure id="a1_5_{ctr}" departureTime="{step_h}:{step_m}:00" vehicleRefId="a1_5_{ctr}"/>')

    vehs.append(f'	<vehicle id="a1_5_{ctr}" type="vehicletype1"/>')
    ctr+=1
with open(r"C:\Users\gamma\glazov_ver2\input_gl\add.txt", 'w') as file:
        for row in additions:
            file.write(row+'\n')
with open(r"C:\Users\gamma\glazov_ver2\input_gl\add_vehs.txt", 'w') as file:
        for row in vehs:
            file.write(row+'\n')