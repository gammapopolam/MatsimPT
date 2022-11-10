import xml.etree.ElementTree as ET
import csv
def to_wkt(coords):
    xy_from=coords[0]
    xy_to=coords[1]
    wkt=f'LINESTRING ({xy_from[0]} {xy_from[1]}, {xy_to[0]} {xy_to[1]})'
    return wkt

tree1=ET.parse(r'C:/Users/Ivan Gamma/glazov/output/glazov_0/glazov_0.output_network.xml')
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
                xy_rebuild=to_wkt([nodes[child1.attrib['from']], nodes[child1.attrib['to']]])
                links_xy.append(xy_rebuild)
links=dict(zip(links_id, links_xy))

events_keys=['time', 'type', 'link', 'vehicle']
events_time=[]
events_type=[]
events_link=[]
events_vehicle=[]
tree2=ET.parse(r'C:/Users/Ivan Gamma/glazov/output/glazov_0/glazov_0.output_events.xml')
root2=tree2.getroot()
for child in root2:
    #print(child.tag, child.attrib)
    if child.attrib['type']=='entered link' or child.attrib['type']=='left link':
        if child.attrib['vehicle']!='tr_0':
            events_time.append(child.attrib['time'])
            events_type.append(child.attrib['type'])
            events_link.append(links[child.attrib['link']])
            events_vehicle.append(child.attrib['vehicle'])
            #event={'time': , 'type': , 'link': , 'vehicle': }
events=dict(zip(events_keys, [events_time, events_type, events_link, events_vehicle]))

import pandas as pd
df=pd.DataFrame.from_dict(events) 
# with open(r'C:/Users/Ivan Gamma/glazov/output/glazov_0/glazov_0_events.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
#     w = csv.DictWriter(f, events_keys)
#     w.writeheader()
#     w.writerow(events)
df.to_csv(r'C:/Users/Ivan Gamma/glazov/output/glazov_0/glazov_0_events.csv', sep=';')