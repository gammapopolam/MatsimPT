# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 12:28:57 2023

@author: Ivan Gamma
"""

import xml.etree.ElementTree as ET
import csv
import ast
import pandas as pd
import copy
def wkt_linestring_to_pointxy(wkt):
    coords=wkt[12:-1]
    xy1=coords.split(',')[0].split(' ')
    xy2=coords.split(',')[1].split(' ')
    return [xy1, xy2]
def to_wkt_point(xy):
    return f'POINT ({xy[0]} {xy[1]})'

def to_wkt_linestring(coords):
    xy_from=coords[0]
    xy_to=coords[1]
    wkt=f'LINESTRING ({xy_from[0]} {xy_from[1]}, {xy_to[0]} {xy_to[1]})'
    return wkt
def segments_into_line(wkt_links):
    wkt=f'LINESTRING ('
    for i in range(len(wkt_links)):
        wkt+=wkt_links[i][12:-1]+', '
    return wkt+(')')
def parse_net(net_xml):
    tree1=ET.parse(net_xml)
    root1=tree1.getroot()
    nodes_id=[]
    nodes_xy=[]

    for child in root1:
        for child1 in child:
            if child1.tag=='node':
                # if 'pt' not in child1.attrib['id']:
                nodes_id.append(child1.attrib['id'])
                nodes_xy.append([child1.attrib['x'], child1.attrib['y']])
    nodes=dict(zip(nodes_id, nodes_xy))

    links_id=[]
    links_xy=[]
    for child in root1:
        for child1 in child:
            if child1.tag=='link':
                # if 'pt' not in child1.attrib['id']:
                links_id.append(child1.attrib['id'])
                xy_rebuild=to_wkt_linestring([nodes[child1.attrib['from']], nodes[child1.attrib['to']]])
                links_xy.append(xy_rebuild)
    links=dict(zip(links_id, links_xy))
    return links

def parse_sched(sched, network):
    tree2=ET.parse(sched)
    root2=tree2.getroot()
    para_lines=[]
    for child in root2:
        if child.attrib!={}:
            for child1 in child:
                # print(child1.attrib)
                para_line={'id': child1.attrib['id'], 'description': None, 'links': [], 'geom': None, 'occupancy': None}
                for child2 in child1:
                    # print(child2.tag)
                    if child2.tag=='description':
                        para_line['description']=child2.text
                    elif child2.tag=='route':
                        for child3 in child2:
                            # print(child3.tag)
                            if 'link' in child3.tag:
                                # if 'awaitDeparture' not in child3.attrib:
                                para_line['links'].append(network[child3.attrib['refId']])
                para_line['geom']=segments_into_line(para_line['links'])
                para_lines.append(para_line)
    return para_lines
def parse_veh_all(veh): #null for occupancy, routes
    tree3=ET.parse(veh)
    root3=tree3.getroot()
    para_veh=[]
    nulls=[]
    for child in root3:
        if 'type' in child.attrib.keys():
            if 'para_' in child.attrib['type'] or 'pt' in child.attrib['type']:
                line_id=child.attrib['id']
                veh_id=child.attrib['id']
                if line_id not in para_veh:
                    para_veh.append(line_id)
                    nulls.append(0)
    return dict(zip(para_veh, nulls))

def parse_veh(veh): #null for occupancy, vehicles
    tree3=ET.parse(veh)
    root3=tree3.getroot()
    para_veh=[]
    nulls=[]
    for child in root3:
        if 'type' in child.attrib.keys():
            if 'para_' in child.attrib['id']:
                line_id=child.attrib['id']
                
                veh_id=child.attrib['id']
                # print(line_id, veh_id)
                para_veh.append(veh_id)
                nulls.append(0)
    return dict(zip(para_veh, nulls))
def paratransit_vehs_state(vehs, veh, state):
    if veh in vehs:
        if state:
            vehs[veh]+=1
        else:
            vehs[veh]-=1
    return vehs
def parse_events(events, vehs): #occupancy in time, for vehs
    tree=ET.parse(events)
    root=tree.getroot()
    eventlist=[]
    for child in root:
        if child.attrib['type']=='PersonEntersVehicle' and 'person' in child.attrib['person']:
            vehs=paratransit_vehs_state(vehs, child.attrib['vehicle'], True)
            veh1=copy.deepcopy(vehs)
            veh1['time']=child.attrib['time']
            eventlist.append(veh1)
        elif child.attrib['type']=='PersonLeavesVehicle' and 'person' in child.attrib['person']:
            vehs=paratransit_vehs_state(vehs, child.attrib['vehicle'], False)
            veh1=copy.deepcopy(vehs)
            veh1['time']=child.attrib['time']
            eventlist.append(veh1)
    return eventlist
def parse_events_all(events, vehs): #occupancy in time, for lines
    tree=ET.parse(events)
    root=tree.getroot()
    eventlist=[]
    for child in root:
        if child.attrib['type']=='PersonEntersVehicle' and 'person' in child.attrib['person']:
            vehs=paratransit_vehs_state(vehs, child.attrib['vehicle'], True)
            veh1=copy.deepcopy(vehs)
            veh1['time']=child.attrib['time']
            eventlist.append(veh1)
        # elif child.attrib['type']=='PersonLeavesVehicle' and 'person' in child.attrib['person']:
        #     vehs=paratransit_vehs_state(vehs, child.attrib['vehicle'][:-2], False)
        #     veh1=copy.deepcopy(vehs)
        #     veh1['time']=child.attrib['time']
        #     eventlist.append(veh1)
    return eventlist
network=parse_net(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_network.xml')
paratransit_lines=parse_sched(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_transitSchedule.xml', network)
paratransit_vehs=parse_veh(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_transitVehicles.xml')
paratransit_vehs_all=parse_veh_all(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_transitVehicles.xml')
occupancy_t=parse_events_all(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_events.xml', paratransit_vehs_all)
df_occupancy=pd.DataFrame.from_dict(occupancy_t)
df_transit_lines=pd.DataFrame.from_dict(paratransit_lines)
df_transit_lines.to_csv(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_transitlines.csv')
df_occupancy.to_csv(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_occupancy.csv')

occupancy_daily=parse_events_all(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_events.xml', paratransit_vehs_all)
df_occupancy_daily=pd.DataFrame.from_dict(occupancy_daily)
df_occupancy_daily.to_csv(r'C:/Users/gamma/matsim/output/glazov_with_pt_3/glazov_with_pt_3.output_occupancy_daily.csv')
# import seaborn as sns
'''
TODO: 
    доделать наполняемость - по линиям, по всей модели (энергозатратно)
    частоты хождения по transitSchedule'''
# for key in paratransit_vehs_all.keys():
# color2=sns.color_palette("Spectral", as_cmap=True)5
# sns.lineplot(data=df_occupancy, palette=sns.color_palette('coolwarm', n_colors=46))
# 
