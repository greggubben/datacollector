#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Amanda');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Nick');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Gregg');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Back');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Office');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Kitchen');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Turtle');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('House', 'Family');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('First Floor', 'Office');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('First Floor', 'Kitchen');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('First Floor', 'Turtle');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('First Floor', 'Family');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('Second Floor', 'Amanda');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('Second Floor', 'Nick');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('Second Floor', 'Gregg');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('Second Floor', 'Back');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('Garage', 'Garage');")
con.execute("INSERT OR REPLACE INTO group_beacon VALUES ('Basement', 'Basement');")

con.commit();
con.close();
