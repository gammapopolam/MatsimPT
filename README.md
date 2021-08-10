# MatsimPT
MatsimPreprocessingTools


# gui.py
gui.py создает пользовательский интерфейс для автоматической обработки входных данных для Minibus или Matsim Classic. 
Python 3.7.3, Spyder 4.1.1

# GTFS_sakhalin.py
GTFS_sakhalin.py - обработка данных для генерации transitfeed второго этапа моделирования. Требует доработки
Python 2.7

# GTFS.py
GTFS.py - старая версия GTFS_sakhalin.py, более универсальная. Требует доработки.
Python 2.7

# GTFS_dummy.py 
GTFS_dummy.py - скрипт-пустышка для того, чтобы сгенерировать необходимый для Minibus transitschedule.xml. Связь с gui.py через subprocess.run

позиции:
 [0] - путь сохранения GTFS_Dummy
 [1] - x_y пара остановки №1
 [2] - x_y пара остановки №2
по умолчанию время прибытия с остановки 1 на остановку 2 - 3 минуты, т.е. время 22:00:00 - 22:03:00

Python 2.7

[out:json];{{geocodeArea:Krasnoyarsk}}->.searchArea;way["highway"](area.searchArea);out body;


[out:json][timeout:25];

{{geocodeArea:Красноярск}}->.searchArea;
(
  way["highway"](area.searchArea);
);
out body;
>;
out skel qt;




'"amenity"="university"',
                                               '"amenity"="college"',
                                               '"amenity"="school"',
                                               '"amenity"="bank"',
                                               '"amenity"="clinic"',
                                               '"amenity"="dentist"',
                                               '"amenity"="doctors"',
                                               '"amenity"="hospital"',
                                               '"amenity"="pharmacy"',
                                               '"amenity"="veterinary"',
                                               '"amenity"="cinema"',
                                               '"amenity"="community_centre"',
                                               '"amenity"="theatre"',
                                               '"amenity"="courthouse"',
                                               '"amenity"="police"',
                                               '"amenity"="post_office"',
                                               '"amenity"="townhall"',
                                               '"amenity"="marketplace"',
                                               '"amenity"="place_of_worship"',
                                               '"building"="commercial"',
                                               '"building"="industrial"',
                                               '"building"="office"',
                                               '"building"="retail"',
                                               '"building"="supermarket"',
                                               '"building"="warehouse"',
                                               '"building"="government"',
                                               '"building"="hospital"',
                                               '"building"="public"',
                                               '"building"="train_station"',
                                               '"building"="transportation"',
                                               '"building"="school"',
                                               '"building"="university"',
                                               '"building"="college"'
