# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 12:28:57 2023

@author: Ivan Gamma
"""

import xml.etree.ElementTree as ET
import csv
import ast
import pandas as pd

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
tree1=ET.parse(r'C:/Users/gamma/matsim/output/glazov_2/glazov_2.output_network.xml')
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

tree2=ET.parse(r'C:/Users/gamma/matsim/output/glazov_2/glazov_2.output_transitSchedule.xml')
root2=tree2.getroot()
# para_line={'id': None, 'description': None, 'links': []}
para_lines=[]
for child in root2:
    if child.attrib!={} and 'para' in child.attrib['id']:
        for child1 in child:
            # print(child1.attrib)
            para_line={'id': child1.attrib['id'], 'description': None, 'links': [], 'geom': None}
            for child2 in child1:
                # print(child2.text)
                if 'Plan' in child2.text:
                    para_line['description']=child2.text
                for child3 in child2:
                    if 'refId' in child3.attrib:
                        if 'awaitDeparture' not in child3.attrib:
                            # print(child3.attrib)
                            para_line['links'].append(links[child3.attrib['refId']])
            para_line['geom']=segments_into_line(para_line['links'])
            para_lines.append(para_line)
res=pd.DataFrame.from_dict(para_lines)
res.to_csv(r'C:/Users/gamma/matsim/output/glazov_2/glazov_2.output_transitSchedule.csv')
        
    # for child1 in child:
        # print(child1.attrib)