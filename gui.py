# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 00:45:30 2021

@author: gammapopolam
"""
from subprocess import run, check_output, Popen, PIPE
from os import listdir, rename
from os.path import isfile, join, isdir, abspath, basename, dirname, realpath
import sys
# import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QFileDialog, QInputDialog, QGridLayout, QLabel
# import folium
import json
import xml.etree.ElementTree as ET
# from xml.dom import minidom
import geojson
# from win32api import GetSystemMetrics
#from PyQt5.QtGui import QIcon


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(5)
        
        btn1=QPushButton('Перевести geojson\nв osm_network.xml', self)
        btn1.clicked.connect(self.network_gen)
        btn1_text=QLabel('Использование geojson ТОЛЬКО из overpass-turbo\nво избежание проблем при обработки.')
        
        btn2=QPushButton('Обработка geojson в population.xml', self)
        btn2.clicked.connect(self.population_gen)
        btn2_text=QLabel(' ')
        
        btn3=QPushButton('Запуск minibus', self)
        btn3.clicked.connect(self.start_minibus)
        btn3_text=QLabel('Перед запуском убедись, что нажал на верхние кнопки!')
        
        btn4=QPushButton('Проверить наличие\nновых итераций', self)
        btn4.clicked.connect(self.check_iters_data_with_xml)
        btn4_text=QLabel('Нажимать только во время работы модели;\nкаждую итерацию переводит в geojson')
        
        btn5=QPushButton('Сгенерировать для одного файла \nкарты с маршрутами', self)
        btn5.clicked.connect(self.gen_folium_maps)
        btn5_text=QLabel('Веб-карты в формате folium. Требует доработки')
        
        btn6=QPushButton('Чтение файла events\n(максимальная наполняемость)', self)
        btn6.clicked.connect(self.event_reader)
        btn6_text=QLabel('Находит максимальную вместимость каждой техники \nпо модели. Рекомендуется для Этапа 2')
        
        grid.addWidget(btn1, 1, 0)
        grid.addWidget(btn2, 2, 0)
        grid.addWidget(btn3, 3, 0)
        grid.addWidget(btn4, 4, 0)
        grid.addWidget(btn5, 5, 0)
        grid.addWidget(btn6, 6, 0)
        
        grid.addWidget(btn1_text, 1, 1, 1, 2)
        grid.addWidget(btn2_text, 2, 1, 1, 2)
        grid.addWidget(btn3_text, 3, 1, 1, 2)
        grid.addWidget(btn4_text, 4, 1, 1, 2)
        grid.addWidget(btn5_text, 5, 1, 1, 2)
        grid.addWidget(btn6_text, 6, 1, 1, 2)

        self.setLayout(grid)
        self.setGeometry(200, 200, 640, 480)
        self.setWindowTitle('MATSim & Minibus')
        self.show()
    def population_gen(self):
        print('ыыыыы')
    def start_minibus(self):
        print('ыыыыы')
        fname = QFileDialog.getOpenFileName(self, 'Откройте config', 'C:\\')[0]
        minibus_f=r'C:/matsim/minibus-12.0/minibus-12.0-SNAPSHOT.jar'
        text, ok = QInputDialog.getText(self, 'java RAM limitation',
            'Enter RAM limit:')
        if ok:
            RAM_limit=f'-Xmx{text}m'
        minibus_cmd=f'java {RAM_limit} -jar {minibus_f} {fname}'
        print(minibus_cmd)
        proc=run(minibus_cmd, capture_output=True, shell=True, encoding='utf-8')
        print(proc)
    def network_gen(self):
        # import re
        fname = QFileDialog.getOpenFileName(self, 'Откройте geojson', 'C:\\')[0]
        f_path=dirname(realpath(fname))
        print(f_path)
        text, ok = QInputDialog.getText(self, 'EPSG Authority code',
            'Enter EPSG:')
        if ok:
            epsg=text
        EPSG_CODE='EPSG:'+str(epsg)
        OUTPUT_F=fname[:-8]+'_conv.osm'
        fj=json.load(open(fname, encoding='utf-8'))
        collection=[]
        print('____Remake geojson')
        for fts in range(len(fj['features'])):
            # print(fj['features'][fts]['geometry'])
            if fj['features'][fts]['geometry']['type']=='LineString':
                linecoords=[]
                for crds in range(len(fj['features'][fts]['geometry']['coordinates'])):
                    # print(fj['features'][fts]['geometry']['coordinates'][crds])
                    xy = (fj['features'][fts]['geometry']['coordinates'][crds][0], fj['features'][fts]['geometry']['coordinates'][crds][1])
                    linecoords.append(xy)
                line=geojson.LineString(linecoords)
                feature=geojson.Feature(geometry=line, properties={'highway': fj['features'][fts]['properties']['highway']})
                collection.append(feature)
        fet_col=geojson.FeatureCollection(collection)
        f_remake=fname[:-8]+'_remake.geojson'
        geojson.dump(fet_col, open(f_remake, mode='w', encoding='utf-8'))
        print('____Converting from geojson to osm')
        cmd=f'geojsontoosm {f_remake} > {OUTPUT_F} -f'
        proc = run(cmd, capture_output=False, shell=True, encoding='utf-8')
        defaultosmconfig=f'{f_path}\DefaultOSMConfig.xml'
        pt2matsim_jar=r'C:/matsim/pt2matsim/pt2matsim-20.8-shaded.jar'
        # pt2matsim_path=pt2matsim_jar-basename(pt2matsim_jar)
        osm2mn_cf=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.CreateDefaultOsmConfig {defaultosmconfig}'
        print('____PT2MATSim DefaultOSMConfig')
        proc=run(osm2mn_cf, capture_output=False, shell=True, encoding='utf-8')
        # print(proc)

        tree=ET.parse(defaultosmconfig)
        root=tree.getroot()
        for child in root:
            for child1 in child:
                # print(child1.tag, child1.attrib)
                if child1.tag == 'param':
                    if child1.attrib['name']=='osmFile':
                        child1.attrib['value']=fname[:-8]+'_conv.osm'
                    elif child1.attrib['name']=='outputCoordinateSystem':
                        child1.attrib['value']=EPSG_CODE
                    elif child1.attrib['name']=='outputDetailedLinkGeometryFile':
                        child1.attrib['value']=f'{f_path}\\detailedlinkgeom.csv'
                    elif child1.attrib['name']=='outputNetworkFile':
                        child1.attrib['value']=f'{f_path}\\osm_network.xml'
                if child1.tag == 'parameterset':
                    if child1.attrib['type']=='routableSubnetwork':
                        child1[0].attrib['value']='car'
                        child1[1].attrib['value']='car'
                    elif child1.attrib['type']=='wayDefaultParams':
                        child1[0].attrib['value']='car'
                        child1[4].attrib['value']='1'
        # tree.insert(1, ET.Comment('DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd'))
        tree.write(defaultosmconfig[:-4]+'_mod.xml', encoding='utf-8', xml_declaration=True)
        path_file=defaultosmconfig[:-4]+'_mod.xml'
        with open(path_file, "w", encoding='UTF-8') as xf:
            doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">'
            tostring = ET.tostring(root).decode('utf-8')
            file = f"{doc_type}{tostring}"
            xf.write(file)
        osm2mn=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.Osm2MultimodalNetwork {defaultosmconfig[:-4]+"_mod.xml"}'
        print('____PT2MATSim OSM2MultimodalNetwork')
        proc=run(osm2mn, capture_output=True, shell=True, encoding='utf-8')
        # print(proc)
        print('____GTFS Dummy gen')
        path_for_gtfs_dummy=QFileDialog.getExistingDirectory(self, 'Выберите папку для сохранения GTFS', 'C:\\')
        text, ok = QInputDialog.getText(self, 'X_Y (EPSG:4326)',
            'Введите первую пару координат X_Y (EPSG:4326)')
        if ok:
            x1_y1=text
        text, ok = QInputDialog.getText(self, 'X_Y (EPSG:4326)',
            'Введите вторую пару координат X_Y (EPSG:4326):')
        if ok:
            x2_y2=text
        # text, ok = QInputDialog.getText(self, 'X_Y (EPSG:4326)',
        #     'Введите третью пару координат X_Y (EPSG:4326):')
        # if ok:
        #     x3_y3=text
        gtfs_dummy=path_for_gtfs_dummy+' '+x1_y1+' '+x2_y2
        print(gtfs_dummy)
#         print('''
# позиции:
# [0] - путь сохранения GTFS_Dummy
# [1] - x_y пара остановки №1
# [2] - x_y пара остановки №2
# по умолчанию время прибытия с остановки 1 на остановку 2 - 3 минуты, т.е. время 22:00:00 - 22:03:00
# ''')

        proc=Popen('C:/Python27/python.exe GTFS_dummy.py', stdin=PIPE, stdout=PIPE, universal_newlines=True)
        # print(proc.stdout.read())
        proc.communicate(gtfs_dummy, timeout=1)
        print('____GTFS Dummy gen success!')
        print('____GTFS Dummy path:')
        print(path_for_gtfs_dummy+r'\\GTFS_dummy.zip')

        
        
        import zipfile
        with zipfile.ZipFile(path_for_gtfs_dummy+r'\\GTFS_dummy.zip', 'r') as zip_ref:
            zip_ref.extractall(path_for_gtfs_dummy+r'\\GTFS_dummy')
        gtfs2transitschedule=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.Gtfs2TransitSchedule {path_for_gtfs_dummy+"/GTFS_dummy"} all {EPSG_CODE} {f_path+"/"}transitSchedule.xml {f_path+"/"}PTM_vehicles.xml'
        # print(gtfs2transitschedule)
        proc=run(gtfs2transitschedule, capture_output=True, shell=True, encoding='utf-8')
        # print(proc)
        print('____PT2MATSim PTMapperConfig')
        ptmcf=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.CreateDefaultPTMapperConfig {f_path+"/PTMapperConfig.xml"}'
        # print(ptmcf)
        proc=run(ptmcf, capture_output=False, shell=True, encoding='utf-8')
        f_ptm=f_path+"\PTMapperConfig.xml"
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
                        child1.attrib['value']=f'{f_path}\\osm_network.xml'
                    elif child1.attrib['name']=='inputScheduleFile':
                        child1.attrib['value']=f'{f_path}\\transitSchedule.xml'
                    elif child1.attrib['name']=='outputCoordinateSystem':
                        child1.attrib['value']=EPSG_CODE
                    elif child1.attrib['name']=='outputStreetNetworkFile':
                        child1.attrib['value']=f'{f_path}\\streetnet.csv'
                    elif child1.attrib['name']=='outputNetworkFile':
                        child1.attrib['value']=f'{f_path}\\PTM_network.xml'
                    elif child1.attrib['name']=='outputScheduleFile':
                        child1.attrib['value']=f'{f_path}\\PTM_schedule.xml'
        tree1.write(f_path+'\PTMapperConfig_mod.xml', encoding='utf-8', xml_declaration=True)
        with open(f_path+'\PTMapperConfig_mod.xml', "w", encoding='UTF-8') as xf:
            doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">'
            tostring = ET.tostring(root1).decode('utf-8')
            file = f"{doc_type}{tostring}"
            xf.write(file)
        print('____PT2MATSim PublicTransitMapper')
        ptm=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.PublicTransitMapper {f_path+"/PTMapperConfig_mod.xml"}'
        # print(ptm)
        proc=run(ptm, capture_output=True, shell=True, encoding='utf-8')
        # print(proc)
        print('____fin')
        self.transitschedule=f'{f_path}\\PTM_network.xml'
        self.network=f'{f_path}\\PTM_network.xml'
        self.vehicles=f'{f_path}\\PTM_vehicles.xml'
        self.path=f_path
        self.pt2matsim_jar=pt2matsim_jar
        tree2=ET.parse('default_minibus_config.xml')
        root2=tree2.getroot()
        for child in root2:
            for child1 in child:
                # print(child1.tag, child1.attrib)
                if child1.attrib['name']=='outputDirectory':
                    child1.attrib['value']=f'{self.path}\output'
                elif child1.attrib['name']=='inputNetworkFile':
                    child1.attrib['value']=f'{self.network}'
                elif child1.attrib['name']=='useTransit':
                    child1.attrib['value']='true'
                elif child1.attrib['name']=='transitScheduleFile':
                    child1.attrib['value']=f'{self.transitschedule}'
                elif child1.attrib['name']=='vehiclesFile':
                    child1.attrib['value']=f'{self.vehicles}'
        tree2.write(f_path+'\PTM_config.xml', encoding='utf-8', xml_declaration=True)
        with open(f_path+'\PTM_config_mod.xml', "w", encoding='UTF-8') as xf:
            doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v1.dtd">'
            tostring = ET.tostring(root2).decode('utf-8')
            file = f"{doc_type}{tostring}"
            xf.write(file)
        print(f'''
MATSim Input data info:
dir: {self.path}
transitSchedule: {self.transitschedule}
network: {self.network}
vehicles: {self.vehicles}''')
        
    def check_iters_data_with_xml(self):
        pt2matsim_jar=r'C:/matsim/pt2matsim/pt2matsim-20.8-shaded.jar'
        fname = QFileDialog.getOpenFileName(self, 'Откройте конфиг', 'C:\\')[0]
        name_of_file=basename(fname)
        # print(fname)
        text, ok = QInputDialog.getText(self, 'EPSG Authority code',
            'Enter EPSG:')
        if ok:
            EPSG=text
        tree=ET.parse(fname)
        root=tree.getroot()
        for child in root:
            for child1 in child:
                # print(child1.tag, child1.attrib)
                    if child1.attrib['name']=='outputDirectory':
                        foldername=child1.attrib['value']
                    elif child1.attrib['name']=='lastIteration':
                        iters=child1.attrib['value']
                    elif child1.attrib['name']=='inputNetworkFile':
                        net=child1.attrib['value']
        # print(foldername, net, iters)
        i=0
        while i<=int(iters):
            path_to_iter=foldername+f'\\ITERS\\it.{i}'
            path_to_plaus_iter=foldername+f'\\ITERS\\it{i}_geojson'
            
            
            iter_schedule=path_to_iter+f'\\1.{i}.transitSchedule.xml.gz'
            # print(iter_schedule, path_to_plaus_iter)
            i+=1
            plaus_cmd=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.CheckMappedSchedulePlausibility {iter_schedule} {net} EPSG:{EPSG} {path_to_plaus_iter}'
            print(plaus_cmd)
            proc=run(plaus_cmd, capture_output=True, shell=True, encoding='utf-8')
            
            
    def gen_folium_maps(self):
        fname = QFileDialog.getOpenFileName(self, 'Откройте GeoJSON', 'C:\\')[0]
        features=json.load(open(fname, encoding='utf-8'))['features']
        transitLineIds_1=[]
        transitLineIds=[]
        for i in range(len(features)):
            transportMode=features[i]['properties']['transportMode']
            transitLineId=features[i]['properties']['transitRouteId'] # !!!!!!
            transitLineIds_1.append(transitLineId)
        transitLineIds=list(dict.fromkeys(transitLineIds_1))
        for lineid in range(len(transitLineIds)):
            transitLineId=transitLineIds[lineid]
            print(transitLineId)
            map_f=folium.Map(location=[46.959179, 142.738041])
            fg=folium.FeatureGroup(transitLineId)
            for i in range(len(features)):
                transitLineId_json=features[i]['properties']['transitRouteId'] # !!!!!!!
                if transitLineId==transitLineId_json:
                    # print(transitLineId_json)
                    geometry=features[i]['geometry']['coordinates']
                    new_geometry=[]
                    for g in range(len(geometry)):
                        new_geometry.append([geometry[g][1], geometry[g][0]])
                        info="departures: {str(features[i]['properties']['departures'])}\ndepartures: {str(features[i]['properties']['transitRouteSimLength']}"
                        folium.PolyLine(locations=new_geometry, popup=info,color='black',weight=2).add_to(fg)
                # print(line)
                # map_f.add_child(line)
                # print(1)
                fg.add_to(map_f)
        
            folium.TileLayer('cartodbpositron').add_to(map_f)
            folium.LayerControl().add_to(map_f)
            map_f.save('C:\\matsim\\minibus\\output_8_dokhrena_2\\folium_maps\\it.100\\'+transitLineId+".html")

    def event_reader(self):
        fname = QFileDialog.getOpenFileName(self, 'Откройте XML с events', 'C:\\')[0]
        # import csv
        tree=ET.parse(fname)
        root=tree.getroot()
        vehicles={}
        max_cap={}
        for child in root:
            if child.attrib['type']=='PersonEntersVehicle':
                # print(child.attrib['vehicle'])
                vehicles[child.attrib['vehicle']]=0
                max_cap[child.attrib['vehicle']]=0
        
        for child in root:
            if child.attrib['type']=='PersonEntersVehicle':
                # print(child.attrib['vehicle'])
                vehicles[child.attrib['vehicle']]=vehicles[child.attrib['vehicle']]+1
                if vehicles[child.attrib['vehicle']]>max_cap[child.attrib['vehicle']]:
                    max_cap[child.attrib['vehicle']]=vehicles[child.attrib['vehicle']]
            elif child.attrib['type']=='PersonLeavesVehicle':
                vehicles[child.attrib['vehicle']]=vehicles[child.attrib['vehicle']]-1
        print(max_cap)
        # f=csv.writer(open(fname[:-4]+'_PaxPerVeh.csv', 'w'))
        # for key, val in vehicles.items():
            # f.writerow([key, val])
        # f.close()
    # def closeEvent(self, event):

    #     reply = QMessageBox.question(self, 'Message',
    #         "Are you sure to quit?", QMessageBox.Yes |
    #         QMessageBox.No, QMessageBox.No)

    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()
        
        
        
        
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit()
    print('end')