#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

con.execute("DROP TABLE IF EXISTS group_beacon;")

con.execute("CREATE TABLE group_beacon (group_name text, beacon text, PRIMARY KEY(group_name, beacon));")

con.commit();
con.close();
