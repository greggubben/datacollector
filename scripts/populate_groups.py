#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

con.execute("INSERT OR REPLACE INTO groups VALUES ('House');")
con.execute("INSERT OR REPLACE INTO groups VALUES ('First Floor');")
con.execute("INSERT OR REPLACE INTO groups VALUES ('Second Floor');")
con.execute("INSERT OR REPLACE INTO groups VALUES ('Basement');")
con.execute("INSERT OR REPLACE INTO groups VALUES ('Garage');")

con.commit();
con.close();
