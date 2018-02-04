#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import datetime

con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

con.execute("DROP TABLE IF EXISTS hourly_summary_by_beacon")

con.execute("""CREATE TABLE hourly_summary_by_beacon (
  reporting_hour timestamp, 
  beacon text, 
  readings integer, 
  min_celsius real, 
  max_celsius real, 
  avg_celsius real, 
  min_fahrenheit real, 
  max_fahrenheit real, 
  avg_fahrenheit real, 
  min_humidity real, 
  max_humidity real, 
  avg_humidity real,
  min_temp_time timestamp, 
  max_temp_time timestamp,
  CONSTRAINT pk_hourly_summary_by_beacon PRIMARY KEY (reporting_hour, beacon)
  );""")

con.commit()
con.close()
