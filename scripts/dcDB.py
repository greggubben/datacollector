#
# SQLite3 Database access management
#
import sqlite3

# Set up the SQLite3 database
def setupDB():
  con = sqlite3.connect('../data/collected.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
  con.row_factory = sqlite3.Row
  return con

# Close down the database connection
def closeDB(con):
  con.close();

