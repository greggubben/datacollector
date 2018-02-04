#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

#con.execute("ALTER TABLE as_posted RENAME TO as_posted_old;")

#con.execute("CREATE TABLE as_posted (ts timestamp, beacon text, celsius real, fahrenheit real, humidity real, status text)")

con.execute("INSERT INTO as_posted (ts, beacon, celsius, fahrenheit, humidity, status) SELECT ts, beacon, celcius, fahrenheit, humidity, status from as_posted_old;")

con.commit();
con.close();
