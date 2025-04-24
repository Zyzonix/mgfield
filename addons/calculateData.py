#!/usr/bin/env python3
#
# written by Zyzonix
# published by xerberosDevelopments
#
# Copyright (c) 2024 xerberosDevelopments
#
# date created  | 10-08-2024 12:25:28
# 
# file          | addons/calculateData.py
# project       | mgfield
# version       | 1.0.0
#

# source databases to calculate avg from
# sourcedatabase must have the format from mgfield_template.sql
# key = database/station, value = list of [<multiplicator>, <value-to-add>], boths are floats
# will be left emtpy in our usecase or removed in a further patch
SOURCES = {
    "station" : [1, 0]
}

# switch to enable import from earlier mgfiel versions
IMPORTOLDDATA = False

# log every single step while calculating
MASSLOGGING = False

# table where all raw data is stored
SOURCETABLE = "mgfield"

if IMPORTOLDDATA: SOURCETABLE = "rawmeasurements"

# maximum rows to request per run (to prevent process getting killed)
REQUESTLIMIT = 1000

# mySQL settings
MYSQLSERVERIP = ""
MYSQLUSERNAME = ""
MYSQLPASSWORD = ""

TARGETDATABASE = "mgfield.calculated"

MYSQLINSERTCALCULATEDCOMMAND = "`(`time_utc`, `time_local`, `x_value`, `y_value`, `z_value`, `out_value`, `measurement_duration`, `start_avg`, `measurement_result`) "

from datetime import datetime
import time
import traceback
import mysql.connector

# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"))
        return curTime
    
    def getTimeLong():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"))
        return curTime

class logging():

    # log file handling will be managed by linux

    def write(msg):
        message = str(ctime.getTime() + " INFO   | " + str(msg))
        print(message)

    def writeError(msg):
        message = str(ctime.getTime() + " ERROR  | " + msg)
        print(message)

    # log/print error stack trace
    def writeExecError(msg):
        message = str(msg)
        print(message)

    def writeNix():
        print()

# connection handler
class mySQLHandler():

    # create db connection
    def openConnection(self):
        
        try:
            # try creating a connection
            serverConnection = mysql.connector.connect(
                host = MYSQLSERVERIP,
                user = MYSQLUSERNAME,
                password = MYSQLPASSWORD
            )
        except:
            logging.writeExecError(traceback.format_exc())
            return False

        if serverConnection.is_connected(): return serverConnection
        else: return False

    # build mySQL insert command
    def insertCommandBuilder(table, data):
        insertInto = "INSERT INTO `"
        values = "VALUES "
        valueBegin = "('"
        valueSeparator = "','"
        valueEnd = "')"
        #                  INSERT INTO ` + table + `(entities) + VALUES + ( + values + )                     
        sqlInsertCommand = insertInto + table + MYSQLINSERTCALCULATEDCOMMAND + values + valueBegin + str(data[0]) + valueSeparator + str(data[1]) + valueSeparator + str(data[2])+ valueSeparator + str(data[3])+ valueSeparator + str(data[4])+ valueSeparator + str(data[5])+ valueSeparator + str(data[6])+ valueSeparator + str(data[7]) + valueSeparator + str(data[8]) + valueEnd
        return sqlInsertCommand
    
    # insert data to database, requires output of 'insertCommandBuilder'
    def insertIn(self, sqlInsertCommand):
        self.mySQLCursor.execute(sqlInsertCommand)

    # change databse
    def changeDB(self, database):
        sqlCommand = "USE `" + database + "`;"  
        try: 
            self.mySQLCursor.execute(sqlCommand)
        except:
            logging.writeError("Failed to change database...")
            logging.writeExecError(traceback.print_exc())
            return False
        return True

    # get all data since timestamp and now
    def getAllDataSince(self, table, UTCtimestamp):
        valueList = []
        sqlCommand = "SELECT * FROM `" + table + "` WHERE time_utc>'" + str(UTCtimestamp) + "' ORDER BY time_utc ASC LIMIT " + str(REQUESTLIMIT) + ";"
        try: 
            self.mySQLCursor.execute(sqlCommand)
            valueList = self.mySQLCursor.fetchall()
        except:
            logging.writeError("Failed to read values...")
            logging.writeExecError(traceback.print_exc())
            return "error"

        return valueList
    
    # get all data since timestamp and now
    def getAllData(self, table):
        valueList = []
        sqlCommand = "SELECT * FROM `" + table + "`ORDER BY time_utc ASC LIMIT " + str(REQUESTLIMIT) + ";"
        try: 
            self.mySQLCursor.execute(sqlCommand)
            valueList = self.mySQLCursor.fetchall()
        except:
            logging.writeError("Failed to read values...")
            logging.writeExecError(traceback.print_exc())
            return "error"

        return valueList

    # get last calculated value (from last run)
    def getLastEntry(self, table):
        content = ""
        sqlCommand = "SELECT * FROM `" + table + "` ORDER BY time_utc DESC LIMIT 1;"  
        try: 
            self.mySQLCursor.execute(sqlCommand)
            content = self.mySQLCursor.fetchall()
        except:
            logging.writeError("Failed to read last entry...")
            logging.writeExecError(traceback.print_exc())
            return "error"
        return content

    # get last calculated value (from last run)
    def getRowWithTimestamp(self, table, UTCTimestamp):
        content = ""
        sqlCommand = "SELECT * FROM `" + table + "` WHERE time_utc='" + str(UTCTimestamp) + "';"  
        try: 
            self.mySQLCursor.execute(sqlCommand)
            content = self.mySQLCursor.fetchall()
        except:
            logging.writeError("Failed to read row with timestamp (" + str(UTCTimestamp) + ")...")
            logging.writeExecError(traceback.print_exc())
            return "error"
        return content


class calculateData():

    # only getting used when importing data from old mgfield versions
    def calcOld(self, station, data, measurement_duration):       
        time_utc = data[0]
        time_local = data[1]
        x = data[2]
        y = data[3]
        z = data[4]
        out_value = data[5]
        corrected_x = x - out_value
        corrected_y = y - out_value
        corrected_z = z - out_value
        pre_measurement_result = (((corrected_x * corrected_x) + (corrected_y * corrected_y) + (corrected_z * corrected_z)) ** 0.5)
        measurement_result = pre_measurement_result * SOURCES[station][0] + SOURCES[station][1]
        return (time_utc, time_local, x, y, z, out_value, measurement_duration, str(0), measurement_result)

    # calc from data input
    def calc(self, station, data):        
        time_utc = data[0]
        time_local = data[1]
        x = data[2]
        y = data[3]
        z = data[4]
        out_value = data[5]
        measurement_duration = data[6]
        start_avg = data[7]
        corrected_x = x - out_value
        corrected_y = y - out_value
        corrected_z = z - out_value
        pre_measurement_result = (((corrected_x * corrected_x) + (corrected_y * corrected_y) + (corrected_z * corrected_z)) ** 0.5)
        measurement_result = pre_measurement_result * SOURCES[station][0] + SOURCES[station][1]
        return (time_utc, time_local, x, y, z, out_value, measurement_duration, start_avg, measurement_result)

    # get last row with start_avg = 1 
    def getLastRowWithStartAVG(self, data):
        updatedData = []
        foundStartAVG = False
        for line in data:
            if line[8] == 1:
                foundStartAVG = True
            if foundStartAVG:
                updatedData.append(line)

        initialLines = len(data)
        selectedLines = len(updatedData)

        logging.write("Removed " + str(initialLines - selectedLines) + " lines")
        return updatedData

    def runner(self):
        for database in SOURCES.keys():
            calculatedDatabase = database + "-calculated"

            logging.write("Selected " + database + " for calculation")
            changedDB = mySQLHandler.changeDB(self, TARGETDATABASE)
            if not changedDB:
                return

            # first get last timestamp when calculated 
            lastRow = mySQLHandler.getLastEntry(self, database + "-calculated")
            #print(lastRow)
            valueList = []
            # case of error while request
            if lastRow == "error":
                return
                
            # case of empty table start at the beginning of the source table
            elif lastRow == []:
                logging.write("Starting at the very beginning of the source database")
                # change to DB with uncalculated data
                changedDB = mySQLHandler.changeDB(self, database)
                if not changedDB:
                    return  
                logging.write("Trying to collect raw data...")
                valueList = mySQLHandler.getAllData(self, SOURCETABLE)
                if valueList == "error":
                    return
                
            # if data was already calculated
            else:
                logging.write("Getting last calculated row...")
                lastRowCalculated = mySQLHandler.getLastEntry(self, calculatedDatabase)
                lastUTCDateCalculated = lastRowCalculated[0][0]
                # change to DB with uncalculated data
                changedDB = mySQLHandler.changeDB(self, database)
                if not changedDB:
                    return  
                
                lastRowUncalculated = mySQLHandler.getLastEntry(self, SOURCETABLE)
                lastUTCDateUncalculated = lastRowUncalculated[0][0]
                if lastUTCDateCalculated == lastUTCDateUncalculated:
                    logging.write("No new data found - returning.")
                    return
                
                logging.write("Trying to collect raw data...")
                valueList = mySQLHandler.getAllDataSince(self, SOURCETABLE, lastUTCDateCalculated)
                if valueList == "error":
                    return

            # if data available to calculate
            if valueList:
                logging.write("Got data, calculating " + str(len(valueList)) + " lines...")
                calculatedList = []
                counter = 0
                for line in valueList:
                    counter += 1
                    if MASSLOGGING: logging.write("Calculating timestamp: " + str(line[0]) + " (" + str(counter) + "/" + str(len(valueList)) + ")")
                    if IMPORTOLDDATA:
                        measurement_duration = str(mySQLHandler.getRowWithTimestamp(self, "allmeasurements", line[0])[0][3])
                        calculatedList.append(calculateData.calcOld(self, database, line, measurement_duration))

                    else:
                        calculatedLine = calculateData.calc(self, database, line)
                        calculatedList.append(calculatedLine)

                if calculatedList:
                    logging.write("Calculated successfully (" + str(counter) + "/" + str(len(valueList)) + ") lines, storing to database...")
                    changedDB = mySQLHandler.changeDB(self, TARGETDATABASE)
                    if not changedDB:
                        return
                    insertCounter = 0
                    storeCounter = 0
                    for line in calculatedList:
                        sqlInsertCommand = mySQLHandler.insertCommandBuilder(calculatedDatabase, line)
                        mySQLHandler.insertIn(self, sqlInsertCommand)
                        insertCounter += 1
                        storeCounter += 1
                        # commit in between to prevent data loss
                        if storeCounter == 100:
                            self.mySQLConnection.commit()
                            storeCounter = 0
                            if MASSLOGGING: logging.write("Stored " + str(insertCounter) + " lines (last timestamp: " + str(line[0]) + ")")
                            time.sleep(0.25)

                    if not insertCounter == len(calculatedList):
                        logging.write("Insertcounter mismatches calculated rows: " + str(insertCounter) + "/" + str(len(calculatedList)))
                    # finally commit all changes
                    self.mySQLConnection.commit()
                    logging.write("Stored all calculated data")
                    logging.write("Calculated values for " + database + " in interval from " + str(calculatedList[0][0]) + " to " + str(calculatedList[len(calculatedList) - 1][0]) + " rows in total: " + str(len(calculatedList)))
            else:
                logging.write("valueList empty, nothing to calculate")

        # finally close all connections
        self.mySQLConnection.commit()
        self.mySQLCursor.close()
        self.mySQLConnection.close()


    def __init__(self):
        logging.write("-----[NEXT RUN]-----")

        # open mySQL connection
        self.mySQLConnection = mySQLHandler.openConnection(self)
        
        # if connection fails, return
        if not self.mySQLConnection: 
            logging.writeError("failed connecting to mySQL server, check config - exiting.")
            return
        
        # get cursor
        self.mySQLCursor = self.mySQLConnection.cursor()
        logging.write("Connected successfully to mySQL server and database")
        calculateData.runner(self)


# initialize script
if __name__ == "__main__":
    calculateData()   