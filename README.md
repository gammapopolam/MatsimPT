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

позиции:\n
 [0] - путь сохранения GTFS_Dummy\n
 [1] - x_y пара остановки №1\n
 [2] - x_y пара остановки №2\n
по умолчанию время прибытия с остановки 1 на остановку 2 - 3 минуты, т.е. время 22:00:00 - 22:03:00

Python 2.7 