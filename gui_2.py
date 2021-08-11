# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 12:31:18 2021

@author: Ivan
"""
from subprocess import run, check_output, Popen, PIPE
from os import listdir, rename, makedirs
from os.path import isfile, join, isdir, abspath, basename, dirname, realpath, exists
import sys
import matsim
import math
import json
import geojson
import xml.etree.ElementTree as ET
import psycopg2
import random
from pyproj import Proj, transform
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QPushButton, QComboBox, QMessageBox, QFileDialog, QInputDialog, QGridLayout, QLabel
class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        self.block1_text=QLabel('Название города')
        self.block1_line=QComboBox()
        self.block1_line.addItems(self.get_city_ids().keys())
        self.block1_line.activated[str].connect(self.onActivated)
        
        self.block2_text=QLabel('Количество итераций')
        self.block2_line=QLineEdit()
        
        self.block3_line=QLineEdit()
        self.block3_text=QLabel('Количество операторов паратранзита')
        # self.block4_text=QLabel('Файл населения .xml')
        # self.block4_line=QLineEdit()
        # self.block4_btn=QPushButton('Нажми для выбора файла')
        # self.block4_btn.clicked.connect(self.select_file_block4)
        # self.block5_text=QLabel('Get workplaces for city')
        # self.block5_btn=QPushButton('push')
        # self.block5_btn.clicked.connect(self.get_workplaces_overpass)
        self.block6_text=QLabel('EPSG код')
        self.block6_line=QLineEdit()
        self.start_btn=QPushButton('Нажми для старта работы')
        self.start_text=QLabel('Начать моделирование.\nЛоги будет на сайте')
        self.start_btn.clicked.connect(self.send_request)
        grid.addWidget(self.block1_text,1,0)
        grid.addWidget(self.block1_line,1,1)
        grid.addWidget(self.block2_text,2,0)
        grid.addWidget(self.block2_line,2,1)
        grid.addWidget(self.block3_text,3,0)
        grid.addWidget(self.block3_line,3,1)
        grid.addWidget(self.block6_text,4,0)
        grid.addWidget(self.block6_line,4,1)
        # grid.addWidget(self.block4_text,5,0)
        # grid.addWidget(self.block4_btn,5,1)
        # grid.addWidget(self.block5_text,5,0)
        # grid.addWidget(self.block5_btn,5,1)
        grid.addWidget(self.start_text,5,0)
        grid.addWidget(self.start_btn,5,1)

        self.setLayout(grid)
        self.setGeometry(200, 200, 640, 480)
        self.setWindowTitle('MATSimPreprocessingTools v2')
        self.show()
    def select_file_block4(self):
        fname = QFileDialog.getOpenFileName(self, 'Откройте файл', 'C:\\')
        self.block4_file=fname[0]
    def select_file_block5(self):
        fname = QFileDialog.getOpenFileName(self, 'Откройте файл', 'C:\\')
        self.block5_file=fname[0]
        self.filepath=dirname(realpath(fname[0]))
        return self.block5_file
    def network_gen(self):
        '''
        fj=json.load(open(self.roads, encoding='utf-8'))
        collection=[]
        print('____Remake geojson')
        for fts in range(len(fj['features'])):
            if fj['features'][fts]['geometry']['type']=='LineString':
                linecoords=[]
                for crds in range(len(fj['features'][fts]['geometry']['coordinates'])):
                    xy = (fj['features'][fts]['geometry']['coordinates'][crds][0], fj['features'][fts]['geometry']['coordinates'][crds][1])
                    linecoords.append(xy)
                line=geojson.LineString(linecoords)
                feature=geojson.Feature(geometry=line, properties={'highway': 'tertiary'})
                collection.append(feature)
        fet_col=geojson.FeatureCollection(collection)
        f_remake=self.pt2matsim_remake_file
        
        '''
        print(r'____Requesting roads from overpass')
        roads_cords=self.get_roads_overpass()
        collection=[]
        for i in range(len(roads_cords)):
            # print(roads_cords[i])
            if roads_cords[i][1] != 'pedestrian':
                line=geojson.LineString(roads_cords[i][0])
                feature=geojson.Feature(geometry=line, properties={'highway': f'{roads_cords[i][1]}'})
                collection.append(feature)
        fet_col=geojson.FeatureCollection(collection)
        f_pre_remake=self.pt2matsim_pre_remake_file
        geojson.dump(fet_col, open(f_pre_remake, mode='w', encoding='utf-8'))
        fj=json.load(open(f_pre_remake, encoding='utf-8'))
        collection=[]
        print('____Remake geojson')
        for fts in range(len(fj['features'])):
            if fj['features'][fts]['geometry']['type']=='LineString':
                linecoords=[]
                # print(len(fj['features'][fts]['geometry']['coordinates']))
                if len(fj['features'][fts]['geometry']['coordinates'])>1:
                    for crds in range(len(fj['features'][fts]['geometry']['coordinates'])):
                        xy = (fj['features'][fts]['geometry']['coordinates'][crds][0], fj['features'][fts]['geometry']['coordinates'][crds][1])
                        linecoords.append(xy)
                elif len(fj['features'][fts]['geometry']['coordinates'][0])>2:
                    for crds in range(len(fj['features'][fts]['geometry']['coordinates'])):
                        xy = (fj['features'][fts]['geometry']['coordinates'][0][crds][0], fj['features'][fts]['geometry']['coordinates'][0][crds][1])
                        linecoords.append(xy)
                line=geojson.LineString(linecoords)
                feature=geojson.Feature(geometry=line, properties={'highway': f"{fj['features'][fts]['properties']['highway']}"})
                collection.append(feature)
        f_remake=self.pt2matsim_remake_file
        fet_col=geojson.FeatureCollection(collection)
        
        geojson.dump(fet_col, open(f_remake, mode='w', encoding='utf-8'))
        print('____Converting from geojson to osm')
        cmd=f'geojsontoosm {f_remake} > {self.pt2matsim_conv_file} -f'
        proc = run(cmd, capture_output=False, shell=True, encoding='utf-8')
        defaultosmconfig=self.pt2matsim_defaultosmconfig
        pt2matsim_jar=self.pt2matsim_jar
        osm2mn_cf=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.CreateDefaultOsmConfig {defaultosmconfig}'
        # print(osm2mn_cf)
        print('____PT2MATSim DefaultOSMConfig')
        proc=run(osm2mn_cf, capture_output=False, shell=True, encoding='utf-8')
        tree=ET.parse(defaultosmconfig)
        root=tree.getroot()
        for child in root:
            for child1 in child:
                if child1.tag == 'param':
                    if child1.attrib['name']=='osmFile':
                        child1.attrib['value']=self.pt2matsim_conv_file
                    elif child1.attrib['name']=='outputCoordinateSystem':
                        child1.attrib['value']='EPSG:'+self.epsg
                    elif child1.attrib['name']=='outputDetailedLinkGeometryFile':
                        child1.attrib['value']=f'{self.path}\\detailedlinkgeom.csv'
                    elif child1.attrib['name']=='outputNetworkFile':
                        child1.attrib['value']=f'{self.path}\\osm_network.xml'
                if child1.tag == 'parameterset':
                    if child1.attrib['type']=='routableSubnetwork':
                        child1[0].attrib['value']='car'
                        child1[1].attrib['value']='car'
                    elif child1.attrib['type']=='wayDefaultParams':
                        child1[0].attrib['value']='car'
                        child1[4].attrib['value']='1'
        tree.write(self.pt2matsim_modosmconfig, encoding='utf-8', xml_declaration=True)
        path_file=self.pt2matsim_modosmconfig
        with open(path_file, "w", encoding='UTF-8') as xf:
            doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">'
            tostring = ET.tostring(root).decode('utf-8')
            file = f"{doc_type}{tostring}"
            xf.write(file)
        osm2mn=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.Osm2MultimodalNetwork {path_file}'
        # print(osm2mn)
        print('____PT2MATSim OSM2MultimodalNetwork')
        proc=run(osm2mn, capture_output=True, shell=True, encoding='utf-8')
        # print(proc)
        print('____PT2MATSim OSM2MultimodalNetwork success!')
        print('____GTFS Dummy gen')
        path_for_gtfs_dummy=self.gtfs_path
        """
        text, ok = QInputDialog.getText(self, 'X, Y (EPSG:4326)',
            'Введите первую пару координат X, Y (EPSG:4326)')
        if ok:
            x1_y1=text.replace(', ', '_')
        text, ok = QInputDialog.getText(self, 'X, Y (EPSG:4326)',
            'Введите вторую пару координат X, Y (EPSG:4326):')
        if ok:
            x2_y2=text.replace(', ', '_')
        """
        x1_y1='0.001_0.001'
        x2_y2='0.002_0.002'
        gtfs_dummy=path_for_gtfs_dummy+' '+x1_y1+' '+x2_y2
        # print(f'C:/Python27/python.exe C:/Git/MatsimPT/GTFS_dummy.py \n{gtfs_dummy}')
        proc=Popen('C:/Python27/python.exe C:/Git/MatsimPT/GTFS_dummy.py', stdin=PIPE, universal_newlines=True)
        proc.communicate(f'{gtfs_dummy}')
        # print(gtfs_dummy)
        # print(proc)
        print('____GTFS Dummy gen success!')
        # print('____GTFS Dummy path:')
        # print(path_for_gtfs_dummy+r'/GTFS_dummy.zip')
        import zipfile
        with zipfile.ZipFile(path_for_gtfs_dummy+r'\GTFS_dummy.zip', 'r') as zip_ref:
            zip_ref.extractall(path_for_gtfs_dummy+r'\GTFS_dummy')
        gtfs2transitschedule=f'java -cp {self.pt2matsim_jar} org.matsim.pt2matsim.run.Gtfs2TransitSchedule {path_for_gtfs_dummy+"/GTFS_dummy"} all WGS84 {self.path+"/"}transitSchedule.xml {self.final_vehicles}'
        # print(gtfs2transitschedule)
        proc=run(gtfs2transitschedule, capture_output=True, shell=True, encoding='utf-8')
        # print(proc)
        print('____PT2MATSim PTMapperConfig')
        ptmcf=f'java -cp {self.pt2matsim_jar} org.matsim.pt2matsim.run.CreateDefaultPTMapperConfig {self.pt2matsim_ptmconfig}'
        # print(ptmcf)
        proc=run(ptmcf, capture_output=False, shell=True, encoding='utf-8')
        f_ptm=self.pt2matsim_ptmconfig
        # print(f_ptm)
        tree1=ET.parse(f_ptm)
        # print('flag')
        root1=tree1.getroot()
        for child in root1:
            for child1 in child:
                # print(child1.tag, child1.attrib)
                if child1.tag == 'param':
                    # print(child1)
                    if child1.attrib['name']=='inputNetworkFile':
                        child1.attrib['value']=f'{self.path}\\osm_network.xml'
                    elif child1.attrib['name']=='inputScheduleFile':
                        child1.attrib['value']=f'{self.path}\\transitSchedule.xml'
                    elif child1.attrib['name']=='outputCoordinateSystem':
                        child1.attrib['value']=f'EPSG:'+self.epsg
                    elif child1.attrib['name']=='outputStreetNetworkFile':
                        child1.attrib['value']=f'{self.path}\\streetnet.csv'
                    elif child1.attrib['name']=='outputNetworkFile':
                        child1.attrib['value']=f'{self.final_network}'
                    elif child1.attrib['name']=='outputScheduleFile':
                        child1.attrib['value']=f'{self.final_transitschedule}'
        tree1.write(self.pt2matsim_ptmconfig_mod, encoding='utf-8', xml_declaration=True)
        with open(self.pt2matsim_ptmconfig_mod, "w", encoding='UTF-8') as xf:
            doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">'
            tostring = ET.tostring(root1).decode('utf-8')
            file = f"{doc_type}{tostring}"
            xf.write(file)
        print('____PT2MATSim PublicTransitMapper')
        ptm=f'java -cp {self.pt2matsim_jar} org.matsim.pt2matsim.run.PublicTransitMapper {self.pt2matsim_ptmconfig_mod}'
        # print(ptm)
        proc=run(ptm, capture_output=True, shell=True, encoding='utf-8')
        # print(proc)
        
        print('____PT2MATSim PublicTransitMapper success')
        
        return '____Preprocessing done!'
    def send_request(self):
        print('____Send request')
        # if self.block4_file==None:
        #     self.popul=None
        # else:
        #     self.popul=self.block4_file
        flag=1
        # if self.block5_file==None:
        #     self.roads=
        # else:
        #     self.roads=self.block5_file
        # self.city=self.block1_line.text()
        
        self.iters=self.block2_line.text()
        self.opers=self.block3_line.text()
        # print(self.city_id)
        self.epsg=self.block6_line.text()
        # if self.filepath:
            # self.path=self.filepath
        self.path=r'C:/output/cityid_'+str(self.city_id)
        # print(self.path)
        print(self.city, self.iters, self.opers)
        makedirs(self.path, exist_ok=True)
        # print(self.city, self.iters, self.opers)
        
        
        self.pt2matsim_jar=r'C:/matsim/MatsimPT_gui_ver2/pt2matsim-20.8-shaded.jar'
        self.pt2matsim_remake_file=self.path+f'\\{self.city_id}_remake.geojson'
        self.pt2matsim_pre_remake_file=self.path+f'\\{self.city_id}_pre_remake.geojson'
        self.pt2matsim_conv_file=self.path+f'\\{self.city_id}_conv.osm'
        self.pt2matsim_defaultosmconfig=self.path+'\DefaultOSMConfig.xml'
        self.pt2matsim_modosmconfig=self.pt2matsim_defaultosmconfig[:-4]+'_mod.xml' #модифицированный defaultosmconfig
        self.gtfs_path=self.path
        self.pt2matsim_ptmconfig=self.path+"\PTMapperConfig.xml"
        self.pt2matsim_ptmconfig_mod=self.path+"\PTMapperConfig_mod.xml"
        
        self.final_transitschedule=self.path+'\\PTM_schedule.xml'
        self.final_network=self.path+'\\PTM_network.xml'
        self.final_vehicles=self.path+'\\PTM_vehicles.xml'
        self.default_minibus_config='default_minibus_config.xml' #!!!
        self.final_config=self.path+'\\PTM_config.xml'
        self.final_config_mod=self.path+'\\PTM_config_mod.xml'
        if flag!=0:
            print('____Network gen start')
            print(self.network_gen())
            print(self.get_workplaces_overpass())
        else:
            print('____lohanylsya')
    def get_roads_overpass(self):
        # self.city=self.block1_line.text()
        from OSMPythonTools.nominatim import Nominatim
        from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
        nominatim = Nominatim()
        areaId = nominatim.query(self.city).areaId()
        print(f'____Area ID:{areaId}')
        overpass=Overpass()
        # import overpy
        # pattern=f'[out:json];area({areaId})->.searchArea;way["highway"](area.searchArea);out;'
        # api=overpy.Overpass()
        pattern_2=overpassQueryBuilder(area=areaId, elementType=['way', 'relation'], 
                                       selector='"highway"', out='body', 
                                       includeGeometry=True)
        result=overpass.query(pattern_2)
        coordinates=[]
        # print(result.elements()[0])
        for i in range(len(result.elements())):
            coordinates.append([result.elements()[i].geometry()['coordinates'], result.elements()[i].tags()['highway']])
            
        # print(coordinates)
        return coordinates
    def get_workplaces_overpass(self):
        print("____Requesting houses (mostransport db)")
        city_ids=self.get_city_ids()
        city_id=city_ids[self.city]
        conn=psycopg2.connect(dbname='mostransport', user='readonly', 
                              password='Alex2', host='84.201.146.240')
        cursor=conn.cursor()
        cursor.execute(f'select * from houses where city_id = {city_id}')
        houses=cursor.fetchall()
        # print(houses)
        # print(type(houses))
        houses_list=[]
        for i in range(len(houses)):
            # print(houses[i][15]['coordinates'])
            if houses[i][15]['coordinates'] != []:
                houses_list.append([houses[i][15]['coordinates'],houses[i][14]])
            # print(houses[i][15]['coordinates'])
        # for house in houses:
            # print(house[6])
            
        # print(houses_list)
        
        tags=['college', 'university', 'school', 'transportation', 'train_station',
              'public', 'hospital', 'government', 'warehouse', 'supermarket', 'retail',
              'office', 'industrial', 'commercial', 'bank', 'clinic', 'dentist', 'doctors', 
              'cafe', 'bar', 'pharmacy', 'veterinary', 'cinema', 'community_centre', 'theatre', 
              'courthouse', 'police', 'post_office', 'townhall', 'marketplace', 'place_of_worship']
        print("____Requesting workplaces (OSM)")
        from OSMPythonTools.nominatim import Nominatim
        from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
        nominatim = Nominatim()
        areaId = nominatim.query(self.city).areaId()
        # print(areaId)
        overpass=Overpass()
        building=overpassQueryBuilder(area=areaId, 
                                     elementType=['way', 'relation'],
                                     selector="building", out='body', 
                                     includeGeometry=True)
        result=overpass.query(building)
        # print(result.elements())
        workplaces=[]
        for i in range(len(result.elements())):
           if result.elements()[i].tags()['building'] in tags:
               workplaces.append(result.elements()[i].geometry()['coordinates'][0][0])
        # print(len(coordinates))
        amenity=overpassQueryBuilder(area=areaId, 
                                     elementType=['way', 'relation'],
                                     selector="amenity", out='body', 
                                     includeGeometry=True)
        result=overpass.query(amenity)
        for i in range(len(result.elements())):
           if result.elements()[i].tags()['amenity'] in tags:
               workplaces.append(result.elements()[i].geometry()['coordinates'][0][0])
        # print(workplaces)
        print('____Population ready for write')
        # return coordinates
        makedirs(self.path, exist_ok=True)
        # print(f'{self.path} added')
        inProj=Proj(init='epsg:4326')
        outProj=Proj(init=f'epsg:{self.epsg}')
        file=self.path+"/population.xml"
        self.population=file
        # print(self.population)
        # with open(file, 'wb+') as f_write:
        f_write=open(file, 'wb+')
        writer = matsim.writers.PopulationWriter(f_write)
        writer.start_population()
        print('____Population writing started')
        
        for i in range(len(houses_list)):
            # print(houses_list[i][1])
            for ppl in range(int(houses_list[i][1])):
                # print(i, ppl)
                endtime_h=random.randrange(6*3600, 17*3600)
                endtime_w=random.randrange(endtime_h+2*3600, 21*3600)
                workplace=random.choice(workplaces)
                # hx, hy = 
                # wx, wy = 
                # print('transforming')
                # print(f'transform({inProj} {outProj} {houses_list[i][0][0]} {houses_list[i][0][1]}')
                if type(workplace[0]) is list:
                    wx, wy = transform(inProj, outProj, workplace[0][0], workplace[0][1])
                else:
                    wx, wy = transform(inProj, outProj, workplace[0], workplace[1])
                hx, hy = transform(inProj, outProj, houses_list[i][0][0], houses_list[i][0][1])
                # wx, wy = transform(inProj, outProj, workplace[0], workplace[1])
                # print(hx, hy)
                # print(wx, wy)
                # print('transform success')
                length=math.sqrt((hx-wx)**2+(hy-wy)**2)
                # print(length)
                while length<2000:
                    # print('less than 5000')
                    workplace=random.choice(workplaces)
                    # print('old')
                    # print(hx, hy)
                    # print(workplace[0], workplace[1])
                    if type(workplace[0]) is list:
                        wx, wy = transform(inProj, outProj, workplace[0][0], workplace[0][1])
                    else:
                        wx, wy = transform(inProj, outProj, workplace[0], workplace[1])
                    # print('new')
                    # print(hx, hy)
                    # print(wx, wy)
                    length=math.sqrt((hx-wx)**2+(hy-wy)**2)
                    # print(str(math.sqrt((hx-wx)**2+(hy-wy)**2))+' changed')
                else:
                    # print(f'writing person_{i}_{ppl}')
                    writer.start_person(f'person_{i}_{ppl}')
                    writer.start_plan(selected=True)
                    writer.add_activity(type='home', x=hx, y=hy, end_time=endtime_h)
                    writer.add_leg(mode="pt")
                    writer.add_activity(type='work', x=wx, y=wy, end_time=endtime_w)
                    writer.add_leg(mode="pt")
                    writer.add_activity(type='home', x=hx, y=hy)
                    writer.end_plan()
                    writer.end_person()
        writer.end_population()
        print('____Population writing finished')
        tree2=ET.parse(self.default_minibus_config)
        root2=tree2.getroot()
        for child in root2:
            for child1 in child:
                # print(child1.tag, child1.attrib)
                if child1.attrib['name']=='outputDirectory':
                    child1.attrib['value']=f'{self.path}\output'
                elif child1.attrib['name']=='inputNetworkFile':
                    child1.attrib['value']=f'{self.final_network}'
                # elif child1.attrib['name']=='useTransit':
                #     child1.attrib['value']='false'
                elif child1.attrib['name']=='transitScheduleFile':
                    child1.attrib['value']=f'{self.final_transitschedule}'
                elif child1.attrib['name']=='vehiclesFile':
                    child1.attrib['value']=f'{self.final_vehicles}'
                elif child1.attrib['name']=='numberOfOperators':
                    child1.attrib['value']=f'{self.opers}'
                elif child1.attrib['name']=='lastIteration':
                    child1.attrib['value']=f'{self.iters}'
                elif child1.attrib['name']=='inputPlansFile':
                    child1.attrib['value']=f'{self.population}'
                elif child1.attrib['name']=='ModuleDisableAfterIteration_2':
                    child1.attrib['value']=f'{self.iters+20}'
        tree2.write(self.final_config, encoding='utf-8', xml_declaration=True)
        with open(self.final_config_mod, "w", encoding='UTF-8') as xf:
            doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v1.dtd">'
            tostring = ET.tostring(root2).decode('utf-8')
            file = f"{doc_type}{tostring}"
            xf.write(file)
        print('____Request to command line:')
        print(f'java -Xmx60000m C:/Users/Administrator/git/matsim_1/contribs/minibus/src/main/java/org/matsim/contrib/minibus/RunMinibus.java {self.final_config_mod}')
    def get_city_ids(self): # returns pair ID:CITY from database
        conn=psycopg2.connect(dbname='mostransport', user='readonly', 
                              password='Alex2', host='84.201.146.240')
        cursor=conn.cursor()
        cursor.execute('select * from cities')
        cities=cursor.fetchall()
        cities_dict=dict()
        for city in cities:
            cities_dict.update({city[1]: city[0]})
        # print(cities_dict)
        return cities_dict
    def onActivated(self, text):
        self.city=text
        print(self.city)
        self.city_id=self.get_city_ids()[text]
        print(self.city_id)
        print('ready')
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    print('end')