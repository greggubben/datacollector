#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

con.execute("DROP TABLE IF EXISTS as_posted;")

con.execute("CREATE TABLE as_posted (ts timestamp, beacon text, celsius real, fahrenheit real, humidity real, status text)")

con.commit();
con.close();
