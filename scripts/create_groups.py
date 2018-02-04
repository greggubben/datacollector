#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

con.execute("DROP TABLE IF EXISTS groups;")

con.execute("CREATE TABLE groups (group_name text PRIMARY KEY);")

con.commit();
con.close();
