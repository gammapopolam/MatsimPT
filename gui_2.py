# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 12:31:18 2021

@author: Ivan
"""
from subprocess import run, check_output, Popen, PIPE
from os import listdir, rename
from os.path import isfile, join, isdir, abspath, basename, dirname, realpath
import sys
import json
import geojson
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QPushButton, QMessageBox, QFileDialog, QInputDialog, QGridLayout, QLabel
class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        self.block1_text=QLabel('Название города на латинице')
        self.block1_line=QLineEdit()
        
        self.block2_text=QLabel('Количество итераций')
        self.block2_line=QLineEdit()
        
        self.block3_line=QLineEdit()
        self.block3_text=QLabel('Количество операторов паратранзита')
        self.block4_text=QLabel('Файл населения .xml')
        self.block4_line=QLineEdit()
        self.block4_btn=QPushButton('Нажми для выбора файла')
        self.block4_btn.clicked.connect(self.select_file_block4)
        self.block5_text=QLabel('Файл УДС из Overpass-Turbo')
        self.block5_btn=QPushButton('Нажми для выбора файла')
        self.block5_btn.clicked.connect(self.select_file_block5)
        self.block6_text=QLabel('EPSG код')
        self.block6_line=QLineEdit()
        start_btn=QPushButton('Нажми для старта работы')
        start_text=QLabel('Начать моделирование.\nЛоги будет на сайте')
        start_btn.clicked.connect(self.send_request)
        grid.addWidget(self.block1_text,1,0)
        grid.addWidget(self.block1_line,1,1)
        grid.addWidget(self.block2_text,2,0)
        grid.addWidget(self.block2_line,2,1)
        grid.addWidget(self.block3_text,3,0)
        grid.addWidget(self.block3_line,3,1)
        grid.addWidget(self.block6_text,4,0)
        grid.addWidget(self.block6_line,4,1)
        grid.addWidget(self.block4_text,5,0)
        grid.addWidget(self.block4_btn,5,1)
        grid.addWidget(self.block5_text,6,0)
        grid.addWidget(self.block5_btn,6,1)
        grid.addWidget(start_text,7,0)
        grid.addWidget(start_btn,7,1)

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
        self.filepath=dirname(realpath(fname))
        return self.block5_file
    def network_gen(self):
        fj=json.load(open(self.city, encoding='utf-8'))
        collection=[]
        print('____Remake geojson')
        for fts in range(len(fj['features'])):
            if fj['features'][fts]['geometry']['type']=='LineString':
                linecoords=[]
                for crds in range(len(fj['features'][fts]['geometry']['coordinates'])):
                    xy = (fj['features'][fts]['geometry']['coordinates'][crds][0], fj['features'][fts]['geometry']['coordinates'][crds][1])
                    linecoords.append(xy)
                line=geojson.LineString(linecoords)
                feature=geojson.Feature(geometry=line, properties={'highway': fj['features'][fts]['properties']['highway']})
                collection.append(feature)
        fet_col=geojson.FeatureCollection(collection)
        f_remake=self.pt2matsim_remake_file
        geojson.dump(fet_col, open(f_remake, mode='w', encoding='utf-8'))
        print('____Converting from geojson to osm')
        cmd=f'geojsontoosm {f_remake} > {self.pt2matsim_conv_file} -f'
        proc = run(cmd, capture_output=False, shell=True, encoding='utf-8')
        defaultosmconfig=self.pt2matsim_defaultosmconfig
        pt2matsim_jar=self.pt2matsim_jar
        osm2mn_cf=f'java -cp {pt2matsim_jar} org.matsim.pt2matsim.run.CreateDefaultOsmConfig {defaultosmconfig}'
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
                        child1.attrib['value']=self.epsg
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
        print('____PT2MATSim OSM2MultimodalNetwork')
        proc=run(osm2mn, capture_output=True, shell=True, encoding='utf-8')
        # print(proc)
        print('____GTFS Dummy gen')
        path_for_gtfs_dummy=self.gtfs_path
        text, ok = QInputDialog.getText(self, 'X_Y (EPSG:4326)',
            'Введите первую пару координат X_Y (EPSG:4326)')
        if ok:
            x1_y1=text
        text, ok = QInputDialog.getText(self, 'X_Y (EPSG:4326)',
            'Введите вторую пару координат X_Y (EPSG:4326):')
        if ok:
            x2_y2=text
        gtfs_dummy=path_for_gtfs_dummy+' '+x1_y1+' '+x2_y2
        print(gtfs_dummy)
        proc=Popen(f'C:/Python27/python.exe C:/Git/MatsimPT/GTFS_dummy.py \n{gtfs_dummy}', stdin=PIPE, stdout=PIPE, universal_newlines=True)
        print(gtfs_dummy)
        print('____GTFS Dummy gen success!')
        print('____GTFS Dummy path:')
        print(path_for_gtfs_dummy+r'\\GTFS_dummy.zip')
        import zipfile
        with zipfile.ZipFile(path_for_gtfs_dummy+r'\\GTFS_dummy.zip', 'r') as zip_ref:
            zip_ref.extractall(path_for_gtfs_dummy+r'\\GTFS_dummy')
        gtfs2transitschedule=f'java -cp {self.pt2matsim_jar} org.matsim.pt2matsim.run.Gtfs2TransitSchedule {path_for_gtfs_dummy+"/GTFS_dummy"} all {self.epsg} {self.path+"/"}transitSchedule.xml {self.final_vehicles}'
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
                        child1.attrib['value']=self.epsg
                    elif child1.attrib['name']=='outputStreetNetworkFile':
                        child1.attrib['value']=f'{self.path}\\streetnet.csv'
                    elif child1.attrib['name']=='outputNetworkFile':
                        child1.attrib['value']=f'{self.final_network}'
                    elif child1.attrib['name']=='outputScheduleFile':
                        child1.attrib['value']=f'{self.final_schedule}'
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
        print('____fin')

        tree2=ET.parse(self.default_minibus_config)
        root2=tree2.getroot()
        for child in root2:
            for child1 in child:
                # print(child1.tag, child1.attrib)
                if child1.attrib['name']=='outputDirectory':
                    child1.attrib['value']=f'{self.path}\output'
                elif child1.attrib['name']=='inputNetworkFile':
                    child1.attrib['value']=f'{self.final_network}'
                elif child1.attrib['name']=='useTransit':
                    child1.attrib['value']='false'
                elif child1.attrib['name']=='transitScheduleFile':
                    child1.attrib['value']=f'{self.final_transitschedule}'
                elif child1.attrib['name']=='vehiclesFile':
                    child1.attrib['value']=f'{self.final_vehicles}'
        tree2.write(self.final_config, encoding='utf-8', xml_declaration=True)
        with open(self.final_config_mod, "w", encoding='UTF-8') as xf:
            doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v1.dtd">'
            tostring = ET.tostring(root2).decode('utf-8')
            file = f"{doc_type}{tostring}"
            xf.write(file)
        return 'final'
    def send_request(self):
        
        self.city=self.block1_line.text()
        self.iters=self.block2_line.text()
        self.opers=self.block3_line.text()
        self.popul=self.block4_file
        self.roads=self.block5_file
        self.epsg=self.block6_line.text()
        self.path=self.filepath
        print(self.city, self.iters, self.opers, self.popul, self.roads)
        
        self.pt2matsim_file=0
        self.minibus_file=0
        self.pt2matsim_remake_file=self.city[:-8]+'_remake.geojson'
        self.pt2matsim_conv_file=self.city[:-8]+'_conv.osm'
        self.pt2matsim_defaultosmconfig=self.path+'\DefaultOSMConfig.xml'
        self.pt2matsim_modosmconfig=self.pt2matsim_defaultosmconfig[:-4]+'_mod.xml' #модифицированный defaultosmconfig
        self.gtfs_path=self.path
        self.pt2matsim_ptmconfig=self.path+"\PTMapperConfig.xml"
        self.pt2matsim_ptmconfig_mod=self.path+"\PTMapperConfig_mod.xml"
        
        self.final_transitschedule=self.path+'\\PTM_schedule.xml'
        self.final_network=self.path+'\\PTM_network.xml'
        self.final_vehicles=self.path+'\\PTM_vehicles.xml'
        self.default_minibus_config=self.path+'defminibusconfig.xml' #!!!
        self.final_config=self.path+'\\PTM_config.xml'
        self.final_config_mod=self.path+'\\PTM_config_mod.xml'
        print(self.network_gen())
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    print('end')