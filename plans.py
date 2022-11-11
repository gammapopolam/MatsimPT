# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 00:16:22 2022

@author: Ivan Gamma
"""

import xml.etree.ElementTree as ET
import csv
import ast

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

tree1=ET.parse(r'C:/Users/Ivan Gamma/glazov/output/glazov_3/glazov_3.output_network.xml')
root1=tree1.getroot()
nodes_id=[]
nodes_xy=[]

for child in root1:
    for child1 in child:
        if child1.tag=='node':
            if 'pt' not in child1.attrib['id']:
                nodes_id.append(child1.attrib['id'])
                nodes_xy.append([child1.attrib['x'], child1.attrib['y']])
nodes=dict(zip(nodes_id, nodes_xy))

links_id=[]
links_xy=[]
for child in root1:
    for child1 in child:
        if child1.tag=='link':
            if 'pt' not in child1.attrib['id']:
                links_id.append(child1.attrib['id'])
                xy_rebuild=to_wkt_linestring([nodes[child1.attrib['from']], nodes[child1.attrib['to']]])
                links_xy.append(xy_rebuild)
links=dict(zip(links_id, links_xy))
plans_keys=['person_id', 'departure', 'travel_time', 'start_point', 'end_point']
persons=[]
deps=[]
travs=[]
xys_from=[]
xys_to=[]
tree2=ET.parse(r'C:/Users/Ivan Gamma/glazov/output/glazov_3/glazov_3.output_plans.xml')
root2=tree2.getroot()
for child in root2:
    person=str(child.attrib)[8:-2] #костыль
    for child1 in child:
        if 'selected' in child1.attrib:
            if child1.attrib['selected']=='yes':
                for child2 in child1:
                    if child2.tag=='leg' and child2.attrib['mode']=='pt':
                        departure=child2.attrib['dep_time']
                        trav_time=child2.attrib['trav_time']
                        for child3 in child2:
                            # print(child3.tag, child3.attrib, child3.text)
                            if 'start_link' in child3.attrib and 'end_link' in child3.attrib:
                                start=child3.attrib['start_link']
                                end=child3.attrib['end_link']
                                attribs=ast.literal_eval(child3.text)
                                # print(attribs)
                                transitroute=attribs['transitRouteId']
                                
                                persons.append(person)
                                deps.append(departure)
                                travs.append(trav_time)
                                xy_from=to_wkt_point(wkt_linestring_to_pointxy(links[start])[0])
                                xys_from.append(xy_from)
                                xy_to=to_wkt_point(wkt_linestring_to_pointxy(links[end])[0])
                                xys_to.append(xy_to)
                                # xy_to=links[end]
plans=dict(zip(plans_keys, [persons, deps, travs, xys_from, xys_to]))
import pandas as pd
df=pd.DataFrame.from_dict(plans) 

df.to_csv(r'C:/Users/Ivan Gamma/glazov/output/glazov_3/glazov_3_output_plans.csv', sep=';')