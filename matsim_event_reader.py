# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 14:17:14 2021

@author: gamma
"""

import matsim
import pandas as pd
from collections import defaultdict
# -------------------------------------------------------------------
# 1. NETWORK: Read a MATSim network:
net = matsim.read_network('output_network.xml.gz')

net.nodes
# Dataframe output:
#           x        y node_id
# 0  -20000.0      0.0       1
# 1  -15000.0      0.0       2
# 2    -865.0   5925.0       3
# ...

net.links
# Dataframe output:
#      length  capacity  freespeed  ...  link_id from_node to_node
# 0   10000.0   36000.0      27.78  ...        1         1       2
# 1   10000.0    3600.0      27.78  ...        2         2       3
# 2   10000.0    3600.0      27.78  ...        3         2       4
# ...

geo = net.as_geo()  # combines links+nodes into a Geopandas dataframe with LINESTRINGs
geo.plot()    # try this in a notebook to see your network!

# -------------------------------------------------------------------
# 2. EVENTS: Stream through a MATSim event file.

# The event_reader returns a python generator function, which you can then
# loop over without loading the entire events file in memory.
# In this example let's sum up all 'entered link' events to get link volumes.
#
# NEW! Now supports .xml.gz and protobuf .pb.gz event file formats!

events = matsim.event_reader('output_events.xml.gz', types='entered link,left link')

link_counts = defaultdict(int) # defaultdict creates a blank dict entry on first reference

for event in events:
    if event['type'] == 'entered link':
        link_counts[event['link']] += 1

# convert our link_counts dict to a pandas dataframe,
# with 'link_id' column as the index and 'count' column with value:
link_counts = pd.DataFrame.from_dict(link_counts, orient='index', columns=['count']).rename_axis('link_id')

# attach counts to our Geopandas network from above
volumes = geo.merge(link_counts, on='link_id')
volumes.plot(column='count', figsize=(10,10), cmap='Wistia') #cmap is colormap