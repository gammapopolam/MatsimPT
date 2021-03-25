# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 00:45:30 2021

@author: gammapopolam
"""
from subprocess import run
from os import listdir, rename

from os.path import isfile, join, isdir, abspath, basename, dirname, realpath
import sys
# import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QFileDialog, QInputDialog
# import folium
import json
import xml.etree.ElementTree as ET
# from xml.dom import minidom
import geojson
#from PyQt5.QtGui import QIcon


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
#        btn1=QPushButton('Выбрать конфиг и\n запустить модель', self)
#        btn1.move(0, 0)
        btn2=QPushButton('Проверить наличие\n новых итераций', self)
        btn2.move(0, 50)
        btn2.clicked.connect(self.check_iters_data_with_xml)
        btn3=QPushButton('Сгенерировать для \nодного файла карты\n с маршрутами', self)
        btn3.move(0, 90)
        # btn3.clicked.connect(self.gen_folium_maps)
        btn4=QPushButton('Чтение файла events\n (максимальная наполняемость)', self)
        btn4.move(0, 140)
        btn4.clicked.connect(self.event_reader)
        btn5=QPushButton('Перевести geojson\n в network.xml', self)
        btn5.move(0, 10)
        btn5.clicked.connect(self.network_gen)
        self.setGeometry(300, 220, 640, 480)
        self.setWindowTitle('MATSim')
        self.show()
        
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
        cmd=f'geojsontoosm {f_remake} > {OUTPUT_F} -f'
        proc = run(cmd, capture_output=False, shell=True, encoding='utf-8')
        defaultosmconfig=f'{f_path}DefaultOSMConfig.xml'
        pt2matsim_jar=QFileDialog.getOpenFileName(self, 'Откройте  pt2matsim jar', f_path)[0]
        # pt2matsim_path=pt2matsim_jar-basename(pt2matsim_jar)
        osm2mn_cf=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.CreateDefaultOsmConfig {defaultosmconfig}'
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
                        child1[0].attrib['value']='car, bus, pt'
                        child1[1].attrib['value']='car, bus, pt'
                    elif child1.attrib['type']=='wayDefaultParams':
                        child1[0].attrib['value']='car, bus, pt'
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
        proc=run(osm2mn, capture_output=True, shell=True, encoding='utf-8')
        print(proc)
                    
        
        
    def check_iters_data_with_xml(self):
        fname = QFileDialog.getOpenFileName(self, 'Откройте конфиг', 'C:\\')[0]
        name_of_file=basename(fname)
        f=open(fname, encoding='utf-8')
        for row in f:
            if 'ENTITY INPUTBASE' in row:
                netdir=fname[:-len(name_of_file)]+row[26:-3]
#                net=QFileDialog.getOpenFileName(self, 'Откройте сеть', netdir)[0]
            elif 'ENTITY OUTPUTBASE' in row:
                foldername=fname[:-len(name_of_file)]+row[26:-3]+'ITERS'
            elif 'ENTITY ITERS' in row:
                iters=row[19:-3]
            elif 'ENTITY EPSG' in row:
                EPSG=row[18:-3]
            elif 'ENTITY NETWORK' in row:
                net=fname[:-len(name_of_file)]+row[23:-3]
#        print(net, foldername, iters, EPSG)
        fls=listdir(path=foldername)
#        print(fls)
        i=0
        while i!=int(iters)+1:
            i+=1
            txt='it.'+str(i)
            outtxt='it'+str(i)
#            print(foldername+'/'+outtxt, foldername+'/'+txt)
            if outtxt not in fls and txt in fls:
                inschedfile=foldername+'/'+txt+'/'+'0.'+str(i)+'.transitSchedule.xml.gz'
#                print('java', '-cp', 
#                      'C:\\matsim\\pt2matsim\\pt2matsim-20.8-shaded.jar', 
#                      'org.matsim.pt2matsim.run.CheckMappedSchedulePlausibility',
#                      inschedfile, net, 'EPSG:'+str(EPSG), foldername+'/'+outtxt)
                subprocess.check_output(['java', '-cp', 
                    'C:\\matsim\\pt2matsim\\pt2matsim-20.8-shaded.jar', 
                    'org.matsim.pt2matsim.run.CheckMappedSchedulePlausibility',
                    inschedfile, net, 'EPSG:'+str(EPSG), foldername+'/'+outtxt])
                rename(foldername+'/'+outtxt+'/'+'schedule_TransitRoutes.geojson', foldername+'/'+outtxt+'_'+'schedule_TransitRoutes.geojson', )
                flag=0
            else:
                flag=1
        
        if int(flag)>0:
            print(flag)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Предупреждение")
            msg.setInformativeText('Модель не завершила генерацию итераций.')
            msg.setWindowTitle("Предупреждение")
            msg.exec_()
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
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        
        
        
        
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit()
    print('end')