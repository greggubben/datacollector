#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Determine if a notification needs to sent this hour
#
import os
from dateutil import rrule
from datetime import datetime, timedelta
import dcDB
import slackWebhook as slackwh

def notification(con):
  cur = con.cursor()
  # Clear minutes, seconds, and microseconds because we are working by hour
  curr_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
  # Hour to be evaluated against - Use last hour
  eval_hour = curr_hour - timedelta(hours=1)
  # Hour to end metrics - Use hour prior to eval hour
  end_metrics_hour = eval_hour - timedelta(hours=1)
  # Hour to start metrics - go back a full day
  begin_metrics_hour = end_metrics_hour - timedelta(days=1)

  #
  # Process each Beacon that sent a reading
  #
  for group_row in con.execute('SELECT group_name FROM groups ORDER BY group_name'):
    #print group_row
    group = group_row['group_name']

    print "Group: {0}".format(group)
    group_summary_status = "Group: {0}\n".format(group)

    # Get the historic MIN and MAX temps
    cur.execute("""SELECT COUNT(hsbb.beacon),
                  MIN(hsbb.reporting_hour) AS "begin_rep_hour [timestamp]",
                  MAX(hsbb.reporting_hour) AS "end_rep_hour [timestamp]",
                  MIN(hsbb.min_celsius) AS min_celsius,
                  MAX(hsbb.max_celsius) AS max_celsius,
                  MIN(hsbb.min_fahrenheit) AS min_fahrenheit,
                  MAX(hsbb.max_fahrenheit) AS max_fahrenheit
                  FROM hourly_summary_by_beacon AS hsbb,
                       group_beacon
                 WHERE hsbb.beacon = group_beacon.beacon
                   AND group_beacon.group_name = ?
                   AND hsbb.reporting_hour >= ?
                   AND hsbb.reporting_hour <= ?""",
        (group, begin_metrics_hour, end_metrics_hour))
    history_row = cur.fetchone()
    #print history_row
    history_beg_time = history_row['begin_rep_hour']
    history_end_time = history_row['end_rep_hour']
    history_min_celsius = history_row['min_celsius']
    history_max_celsius = history_row['max_celsius']
    history_min_fahrenheit = history_row['min_fahrenheit']
    history_max_fahrenheit = history_row['max_fahrenheit']

    print "  Historic RNG: {0} to {1}".format(history_beg_time, history_end_time)
    group_summary_status += "  Historic RNG: {0} to {1}\n".format(history_beg_time, history_end_time)
    print "  Historic MIN: {0: 3.2f}F    {1: 3.2f}C".format(history_min_fahrenheit, history_min_celsius)
    group_summary_status += "  Historic MIN: {0: 3.2f}F    {1: 3.2f}C\n".format(history_min_fahrenheit, history_min_celsius)
    print "  Historic MAX: {0: 3.2f}F    {1: 3.2f}C".format(history_max_fahrenheit, history_max_celsius)
    group_summary_status += "  Historic MAX: {0: 3.2f}F    {1: 3.2f}C\n".format(history_max_fahrenheit, history_max_celsius)

    # Check each Beacon for a new MIN or MAX temp to notify about
    new_min_celsius = history_min_celsius
    new_min_fahrenheit = history_min_fahrenheit
    new_min_beacon = ""
    min_found = False
    new_max_celsius = history_max_celsius
    new_max_fahrenheit = history_max_fahrenheit
    new_max_beacon = ""
    max_found = False
    diff_min_celsius = history_max_celsius
    diff_min_fahrenheit = history_max_fahrenheit
    diff_min_beacon = ""
    diff_max_celsius = history_min_celsius
    diff_max_fahrenheit = history_min_fahrenheit
    diff_max_beacon = ""
    for beacon_row in con.execute("""SELECT hsbb.beacon,
                       min_celsius AS min_celsius,
                       max_celsius AS max_celsius,
                       avg_celsius AS avg_celsius,
                       min_fahrenheit AS min_fahrenheit,
                       max_fahrenheit AS max_fahrenheit,
                       avg_fahrenheit AS avg_fahrenheit
                  FROM hourly_summary_by_beacon AS hsbb,
                       group_beacon
                 WHERE hsbb.beacon = group_beacon.beacon
                   AND group_beacon.group_name = ?
                   AND hsbb.reporting_hour = ?
                 ORDER BY hsbb.beacon""",
                (group, eval_hour)):
      #print min_row
      beacon = beacon_row['beacon']
      min_celsius = beacon_row['min_celsius']
      max_celsius = beacon_row['max_celsius']
      avg_celsius = beacon_row['avg_celsius']
      min_fahrenheit = beacon_row['min_fahrenheit']
      max_fahrenheit = beacon_row['max_fahrenheit']
      avg_fahrenheit = beacon_row['avg_fahrenheit']

      print "  Beacon: {0}".format(beacon)
      group_summary_status += "  Beacon {0}\n".format(beacon)
      print "    Temp MIN: {0: 3.2f}F    {1: 3.2f}C".format(min_fahrenheit, min_celsius)
      group_summary_status += "    Temp MIN: {0: 3.2f}F    {1: 3.2f}C\n".format(min_fahrenheit, min_celsius)
      print "    Temp MAX: {0: 3.2f}F    {1: 3.2f}C".format(max_fahrenheit, max_celsius)
      group_summary_status += "    Temp MAX: {0: 3.2f}F    {1: 3.2f}C\n".format(max_fahrenheit, max_celsius)
      print "    Temp AVG: {0: 3.2f}F    {1: 3.2f}C".format(avg_fahrenheit, avg_celsius)
      group_summary_status += "    Temp AVG: {0: 3.2f}F    {1: 3.2f}C\n".format(avg_fahrenheit, avg_celsius)

      #post2slack("{0}.{1} MIN:{2: 3.2f} History:{3: 3.2f}.".format(group, beacon, min_celsius, history_min_beacon))

      # See if this Beacon has a Min below the Historic Min
      if (min_celsius < history_min_celsius):
        print "      New Historic MIN\n"
        group_summary_status += "      New Historic MIN\n"

      # Is this the lowest of the Min?
      if (min_celsius < new_min_celsius):
        new_min_celsius = min_celsius
        new_min_fahrenheit = min_fahrenheit
        new_min_beacon = beacon
        min_found = True

      # Find the Beacon with the lowest temp in this hour
      if (min_celsius < diff_min_celsius):
        diff_min_celsius = min_celsius
        diff_min_fahrenheit = min_fahrenheit
        diff_min_beacon = beacon

      # See if this Beacon has a Max above the Historic Max
      if (max_celsius > history_max_celsius):
        print "      New Historic MAX\n"
        group_summary_status += "      New Historic MAX\n"

      # Is this the highest of the Max?
      if (max_celsius > new_max_celsius):
        new_max_celsius = max_celsius
        new_max_fahrenheit = max_fahrenheit
        new_max_beacon = beacon
        max_found = True

      # Find the Beacon with the highest temp in this hour
      if (max_celsius > diff_max_celsius):
        diff_max_celsius = max_celsius
        diff_max_fahrenheit = max_fahrenheit
        diff_max_beacon = beacon

    # Notify MIN
    if (min_found):
      min_str =  "New MIN {0} temp of {1: 3.2f}F/{2: 3.2f}C in {3}.\nPrevious MIN was {4: 3.2f}F/{5: 3.2f}C.".format(group, new_min_fahrenheit, new_min_celsius, new_min_beacon, history_min_fahrenheit, history_min_celsius)
      print min_str
      group_summary_status += "  {0}\n".format(min_str)
      slackwh.post2slack(min_str)
  
    # Notify MAX
    if (max_found):
      max_str = "New MAX {0} temp of {1: 3.2f}F/{2: 3.2f}C in {3}.\nPrevious MAX was {4: 3.2f}F/{5: 3.2f}C.".format(group, new_max_fahrenheit, new_max_celsius, new_max_beacon, history_max_fahrenheit, history_max_celsius)
      print max_str
      group_summary_status += "  {0}\n".format(max_str)
      slackwh.post2slack(max_str)

    # Temp Range too high
    if (diff_max_fahrenheit - diff_min_fahrenheit > 2):
      status_str = "Temp different of {0} between {1} and {2} is too high\n".format(diff_max_fahrenheit - diff_min_fahrenheit, diff_min_beacon, diff_max_beacon)
      status_str += "{0} MIN: {1: 3.2f}F\n".format(diff_min_beacon, diff_min_fahrenheit,)
      status_str += "{0} MAX: {1: 3.2f}F\n".format(diff_max_beacon, diff_max_fahrenheit,)
      print status_str
      group_summary_status += status_str
      # This is too chatty now.  Ranges are all over the place causing accuracy to be questioned.
      #slackwh.post2slack(status_str)

    #slackwh.debug2slack(group_summary_status)

  cur.close();

  #slackwh.debug2slack("all done")

def main():
  path=os.path.dirname(os.path.realpath(__file__))
  print(path)
  os.chdir(path)

  # Setup the Database Connection
  dbConnection = dcDB.setupDB()

  # Summarize the Data
  notification(dbConnection)

  # Close the Database Connection
  dcDB.closeDB(dbConnection)

#
# Check if we are running as main
#
if (__name__ == "__main__"):
  main()

