#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

for row in con.execute("SELECT * FROM group_beacon"):
  print row

con.close();
