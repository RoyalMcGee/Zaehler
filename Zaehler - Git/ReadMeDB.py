#!/usr/bin/python3
import os, sys, sqlite3
import time
from time import sleep
import datetime
from RPi import GPIO
dbfile="tempdata.db"

def db_anlegen():
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()
    # Tabelle erzeugen
    sql = "CREATE TABLE Strom("\
        "id INT AUTO_INCREMENT PRIMARY KEY,"\
        "trigger DATETIME, "\
        "count INT)"
    cursor.execute(sql)
    connection.commit()
    connection.close()
    print("Datenbank tempdata.db angelegt mit:\n")
    print (sql) 

GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN)
count=0
previous=1
start=time.time()
start = datetime.datetime.fromtimestamp(start).strftime('%Y%m%d_%H%M%S')
filename='log/data.'+start+'.log'
f=open(filename,'w+')
try:
    # Existenz der Datenbank überprüfen und ggf. diese anlegen
    if not os.path.exists(dbfile):
        print("Datenbank tempdata.db nicht vorhanden - Datenbank wird anglegt.")
        db_anlegen()
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()   

    print("Datenbank bereit, starte Messung")
    while True:
        sleep(0.2)
        v=GPIO.input(11)
        if(v == 0 and previous == 1):
            count+=1
            timenow=time.time()
            timestamp = datetime.datetime.fromtimestamp(timenow).strftime('%Y %m %d %H %M %S')
            timestampsql=datetime.datetime.fromtimestamp(timenow).strftime('%Y-%m-%d %H:%M:%S')
            print("count:", count, "Tiggered: ", timestamp)
            f.write(timestamp)
            f.write("\n")
            query='INSERT INTO Strom (trigger, count) VALUES("'+timestampsql+'",'+str(count)+')'
            cursor.execute(query)
            connection.commit()
            print (query)
        previous=v

except:
    connection.close()
    f.close()
    GPIO.cleanup()
