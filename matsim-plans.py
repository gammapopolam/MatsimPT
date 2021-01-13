
import matsim
#import json
import random
import pandas as pd
from collections import defaultdict
def read_network(network):
    net = matsim.read_network(network)
    geo = net.as_geo()  # combines links+nodes into a Geopandas dataframe with LINESTRINGs
    geo.plot()
    
    
def randomize_home(features):
    homelist=[]
    for i in range(len(features)):
        if features[i]['properties']["building"]=="apartments" or features[i]['properties']["building"]=="house" or features[i]['properties']["building"]=="semidetached_house":
            home={'id':features[i]['properties']["osm_id"], "geometry": (features[i]["geometry"]["coordinates"][1], features[i]["geometry"]["coordinates"][0])}
            homelist.append(home)
    return homelist

def randomize_study(features):
    studylist=[]
    for i in range(len(features)):
        if features[i]['properties']["building"]=="school" or features[i]['properties']["building"]=="university" or features[i]['properties']["amenity"]=="college":
            study={'id':features[i]['properties']["osm_id"], "geometry": (features[i]["geometry"]["coordinates"][1], features[i]["geometry"]["coordinates"][0])}
            studylist.append(study)
    return studylist

def randomize_office(features):
    officelist=[]
    for i in range(len(features)):
        if features[i]['properties']["building"]=="office" or features[i]['properties']["amenity"]=="marketplace":
            office={'id':features[i]['properties']["osm_id"], "geometry": (features[i]["geometry"]["coordinates"][1], features[i]["geometry"]["coordinates"][0])}
            officelist.append(office)
    return officelist

def write_plans(plans_file, person_id, buildingslist):
    homes=buildingslist[0]
    unique_home=random.choice(homes)
    print(unique_home)
    nextact=buildingslist[random.randint(1,2)]
    unique_nextact=random.choice(nextact)
    print(unique_nextact)
    writer.start_person(person_id)
    writer.start_plan(selected=True)
    writer.add_activity(type='home', x=unique_home["geometry"][1], y=unique_home["geometry"][0], end_time=8*3600)
    writer.add_leg(mode="pt")
    writer.add_activity(type='work', x=unique_nextact["geometry"][1], y=unique_nextact["geometry"][0], end_time=18*3600)
    writer.add_leg(mode="pt")
    writer.add_activity(type='home', x=unique_home["geometry"][1], y=unique_home["geometry"][0])
    writer.end_plan()
    writer.end_person()
    
    
network=r'C:\Users\gamma\Downloads\output_network.xml.gz'
net = matsim.read_network(network)
geo = net.as_geo()  # combines links+nodes into a Geopandas dataframe with LINESTRINGs
geo.plot()

events=matsim.event_reader(r'C:\Users\gamma\Downloads\output_events.xml.gz', types='entered link, left link')
link_counts=defaultdict(float)
for event in events:
    if event['type']=='entered link':
        link_counts[event['link']]+=1
link_counts=pd.DataFrame.from_dict(link_counts, orient='index', columns=['count']).rename_axis('link_id')
volumes=geo.merge(link_counts, on='link_id')
volumes.plot(column='count', figsize=(10,10))


#buildings_file=json.load(open(r'C:\Users\gamma\Documents\matsim\matsim-12.0\examples\pt_yus\buildings_4326.geojson', encoding='utf-8'))
#print(len(buildings_file['features']))
#features=buildings_file['features']
#buildingslist=[randomize_home(features), randomize_study(features), randomize_office(features)]
#
#file=r"C:\Users\gamma\Documents\matsim\matsim-12.0\minibus-12.0\minibus-12.0-SNAPSHOT\yus\input\population.xml"
#with open(file, 'wb+') as f_write:
#    writer = matsim.writers.PopulationWriter(f_write)
#    writer.start_population()
#    write_plans(file, "person_id1", buildingslist)
#    write_plans(file, "person_id2", buildingslist)
#    write_plans(file, "person_id3", buildingslist)
#    write_plans(file, "person_id4", buildingslist)
#    write_plans(file, "person_id5", buildingslist)
#    write_plans(file, "person_id6", buildingslist)
#    writer.end_population()
