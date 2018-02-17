#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Summarize by Beacon and Hour
#
import os
import sqlite3
from dateutil import rrule
from datetime import datetime, timedelta
import dcDB
import hourly_notification as hnot
import slackWebhook as slackwh


#
# Perform the Hourly Summarization of the Beacons
#
def summarize(con):
  # Exclude the current hour because we might not have all readings yet
  # Clear minutes, seconds, and microseconds because we are working by hour
  # end_ts is used for SQL statements
  end_ts = datetime.now().replace(minute=0, second=0, microsecond=0)
  # loop_end_ts is used for python looping
  loop_end_ts = end_ts - timedelta(hours=1)
  # init to something so stats at end do not error
  start_ts = "-"


  # Move the new records from Raw to Working for processing
  working_readings = con.execute('UPDATE as_posted SET status = "W" WHERE status = "R" AND ts < ?;', (end_ts,)).rowcount
  con.commit();

  tot_beacon_count = 0
  tot_hour_count = 0
  tot_reading_count = 0
  #
  # Process each Beacon that sent a reading
  #
  for beacon_row in con.execute('SELECT beacon, COUNT(beacon) AS readings, MIN(ts) AS "min_ts [timestamp]", MAX(ts) AS "max_ts [timestamp]" FROM as_posted WHERE status = "W" GROUP BY beacon'):
    #print row
    beacon = beacon_row["beacon"]
    min_ts = beacon_row["min_ts"]
    max_ts = beacon_row["max_ts"]
    print "Summary of Beacon {0}".format(beacon)
    #print "Start at {0}; Finish at {1}".format(min_ts, max_ts)
    tot_beacon_count += 1

    # Clear minutes, seconds, and microseconds from min timestamp
    # because we are working by hour
    start_ts = min_ts.replace(minute=0, second=0, microsecond=0)

    #
    # Process each Hour that we received a reading
    #
    for process_hour in rrule.rrule(rrule.HOURLY, dtstart=start_ts, until=loop_end_ts):
      print "Summarizing Hour {0:%Y-%m-%d %H:%M} for {1}".format(process_hour, beacon)
      next_process_hour = process_hour + timedelta(hours=1)
      tot_hour_count += 1

      #
      # Process each reading
      #
      readings = 0
      min_time = 0
      max_time = 0
      tot_celsius = 0     # Used for Average
      tot_fahrenheit = 0  # Used for Average
      tot_humidity = 0    # Used for Average
      min_celsius = 0
      min_fahrenheit = 0
      min_temp_ts = 0
      min_humidity = 0
      max_celsius = 0
      max_fahrenheit = 0
      max_temp_ts = 0
      max_humidity = 0
      for reading_row in con.execute('SELECT ts AS "ts [timestamp]", beacon, celsius, fahrenheit, humidity FROM as_posted WHERE beacon = ? AND ts >= ? AND ts < ?', (beacon, process_hour, next_process_hour)):
        #print reading
        tot_reading_count += 1
        ts = reading_row['ts']
        celsius = reading_row['celsius']
        fahrenheit = reading_row['fahrenheit']
        humidity = reading_row['humidity']

        # Check if Min Time needs to be updated
        if (readings == 0 or ts < min_time):
          min_time = ts

        # Check if Min Temperature needs to be updated
        if (readings == 0 or celsius < min_celsius):
          min_celsius = celsius
          min_fahrenheit = fahrenheit
          min_temp_ts = ts
  
        # Check if Min Humidity needs to be updated
        if (readings == 0 or humidity < min_humidity):
          min_humidity = humidity
  
        # Check if Max Time needs to be updated
        if (readings == 0 or ts > max_time):
          max_time = ts
  
        # Check if Max Temperature needs to be updated
        if (readings == 0 or celsius > max_celsius):
          max_celsius = celsius
          max_fahrenheit = fahrenheit
          max_temp_ts = ts

        # Check if Max Humidity needs to be updated
        if (readings == 0 or humidity > max_humidity):
          max_humidity = humidity

        # Sum totals for average calculation
        tot_celsius += celsius
        tot_fahrenheit += fahrenheit
        tot_humidity += humidity
        readings += 1

      # Is there a summary to save
      if (readings != 0):
        # Calculate Averages
        avg_celsius = tot_celsius/readings
        avg_fahrenheit = tot_fahrenheit/readings
        avg_humidity = tot_humidity/readings

        # Save the Summary
        con.execute("""INSERT OR REPLACE INTO hourly_summary_by_beacon 
                    (reporting_hour, beacon, readings, 
                     min_celsius, max_celsius, avg_celsius, 
                     min_fahrenheit, max_fahrenheit, avg_fahrenheit,
                     min_humidity, max_humidity, avg_humidity,
                     min_temp_time, max_temp_time)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",
                    (process_hour, beacon, readings,
                     min_celsius, max_celsius, avg_celsius,
                     min_fahrenheit, max_fahrenheit, avg_fahrenheit,
                     min_humidity, max_humidity, avg_humidity,
                     min_temp_ts, max_temp_ts,))
        con.commit();

        # Print summary
        print "Readings: {0}, First: {1}, Last: {2}".format(readings, min_time, max_time)
        print " Temp Time MIN: {0:%Y-%m-%d %H:%M},  MAX: {1:%Y-%m-%d %H:%M}".format(min_temp_ts, max_temp_ts)
        print "   Celsius MIN:{0: 3.2f}, AVG:{1: 3.2f}, MAX:{2: 3.2f}".format(min_celsius, avg_celsius, max_celsius)
        print "Fahrenheit MIN:{0: 3.2f}, AVG:{1: 3.2f}, MAX:{2: 3.2f}".format(min_fahrenheit, avg_fahrenheit, max_fahrenheit)
        print "  Humidity MIN:{0: 3.2f}, AVG:{1: 3.2f}, MAX:{2: 3.2f}".format(min_humidity, avg_humidity, max_humidity)
      else:
        print "No Data to Summarize"

  # Move the processed records from Working to Done
  done_readings = con.execute('UPDATE as_posted SET status = "D" WHERE status = "W" AND ts < ?;', (end_ts,)).rowcount
  con.commit();

  # Print Summarization Stats
  summary_stat = ""
  summary_stat += "Hourly Summary Process Completed\n"
  summary_stat += "Time Range from {0} to {1}\n".format(start_ts, end_ts)
  summary_stat += "{0:4d} Working Readings\n".format(working_readings)
  summary_stat += "{0:4d} Beacons Summarized\n".format(tot_beacon_count)
  summary_stat += "{0:4d} Hours Summarized\n".format(tot_hour_count)
  summary_stat += "{0:4d} Readings Summarized\n".format(tot_reading_count)
  summary_stat += "{0:4d} Done Readings\n".format(done_readings)
  print ""
  print summary_stat
  print ""
  #slackwh.debug2slack(summary_stat)

#
# Find out if any beacons are no longer reporting
#
def findMissing(con):
  # Clear minutes, seconds, and microseconds because we are working by hour
  end_hour_ts = datetime.now().replace(minute=0, second=0, microsecond=0)
  start_hour_ts = end_hour_ts - timedelta(hours=1)
  end_day_ts = start_hour_ts
  start_day_ts = end_day_ts - timedelta(days=1)

  # Get the beacons that reported in the last hour
  #print "Last Hour"
  last_hour_beacons = set()
  for reading_row in con.execute('SELECT DISTINCT(beacon) AS beacon FROM as_posted WHERE ts >= ? AND ts < ?', (start_hour_ts, end_hour_ts)):
    beacon = reading_row['beacon']
    #print beacon
    last_hour_beacons.add(beacon)

  # Get the beacons that reported in the last day
  #print "Last Day"
  last_day_beacons = set()
  for reading_row in con.execute('SELECT DISTINCT(beacon) AS beacon FROM as_posted WHERE ts >= ? AND ts < ?', (start_day_ts, end_day_ts)):
    beacon = reading_row['beacon']
    #print beacon
    last_day_beacons.add(beacon)

  # Missing Beacons
  for beacon in last_day_beacons - last_hour_beacons:
    slackwh.post2slack("Missing Beacon {0}".format(beacon), icon="exclamation", name="Missing Watchdog")

  # New Beacons
  for beacon in last_hour_beacons - last_day_beacons:
    slackwh.post2slack("New Beacon {0}".format(beacon), icon="exclamation", name="New Watchdog")

def main():
  path=os.path.dirname(os.path.realpath(__file__))
  #print(path)
  os.chdir(path)

  # Setup the Database Connection
  dbConnection = dcDB.setupDB()

  # Summarize the Data
  summarize(dbConnection)

  # Find any Beacons not reporting in
  findMissing(dbConnection)

  # Prepare Notifications
  hnot.notification(dbConnection)

  # Close the Database Connection
  dcDB.closeDB(dbConnection)

#
# Check if we are running as main
#
if (__name__ == "__main__"):
  main()
