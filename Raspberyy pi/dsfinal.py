import os
import time
import pymongo
from pymongo import MongoClient

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')          #initialises pins

temp_sensor = '/sys/bus/w1/devices/28-031725077dff/w1_slave'            #reads the file created by the sensor

uri = "mongodb://cooking:wsurop18@ds223268.mlab.com:23268/wsurop_cooking"       #connects to the MongoDB
client = MongoClient(uri)

db = client.wsurop_cooking
glo_temp = -273                                             #initialises a temporary value that holds the last temepratures

db.temperatures.remove({"units" : "Celsius"})               #clears all data in the database upon bootup of the code

db.temperatures.insert_one(
           {'temperature': glo_temp, 'units': "Celsius"}        #adds a dummy data to database
        )

def temp_raw():         #reads the lines from sensor file

    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():        #extracts the temperature data only from the file

    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()


    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        temp_c2 = int(temp_c)

        return temp_c2

while True:
    curr_temp = read_temp()
    
    print("waiting for temp change")
    if glo_temp != curr_temp:               #checks if there is a temperature change
        print("temp changed!")
        print(curr_temp)
        db.temperatures.insert_one(                                 #insert temperature data to database
           {'temperature': read_temp(), 'units': "Celsius"}
        )
        glo_temp = curr_temp
        time.sleep(1)

