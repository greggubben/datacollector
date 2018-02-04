#!/usr/bin/python
# -*- coding: UTF-8 -*-
import cgi, cgitb
import sys 
import json 
import sqlite3
import datetime

# enable debugging
cgitb.enable()

result = {'success':'false','message':'Unknown Error'}
con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
     
datajson = json.load(sys.stdin)
now = datetime.datetime.now()
 
try:
  con.execute("INSERT INTO as_posted (ts, beacon, celsius, fahrenheit, humidity, status) VALUES (?, ?, ?, ?, ?, ?)", (now, datajson['beacon'], datajson['celsius'], datajson['fahrenheit'], datajson['humidity'], 'R'))
  con.commit();

  result = {'success':'true','message':'The Command Completed Successfully'}
except:
  result = {'success':'false','message':"{0}".format(sys.exc_info()[0])}
  #result = {'success':'false','message':"{0}: {1}".format(e.errno, e.strerror)}
finally:
  con.close();

print "Content-Type: application/json; charset=utf-8 \n\n"
print json.dumps(result)
#print json.dumps(datajson)

