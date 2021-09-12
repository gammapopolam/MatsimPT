# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 16:27:11 2021
MOSCOW PARATRANSIT project
@author: Ivan
"""
import matsim
import random
file=r'C:\Users\Ivan\moscow_paratransit\population.xml'
f_write=open(file, 'wb+')
writer = matsim.writers.PopulationWriter(f_write)
writer.start_population()

popul=r'C:/Users/Ivan/moscow_paratransit/popul_2.geojson'


