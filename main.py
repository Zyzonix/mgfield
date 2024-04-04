#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 29-03-2024 14:45:57
# 
# file          | main.py
# project       | MGFieldPy
# file version  | 1.0.0
#
import time
import threading
from datetime import datetime
import traceback

# import custom scripts
import config
from scripts.logHandler import logging
from scripts.mysqlHandler import mySQLHandler


# static public storage
dataArray = {}
# temp storage for temperature and SysStats, to save it when saving MGField data; prevents complications with mySQL connection
dataArrayOther = {}
# storage for threads
tasks = {}

# storage for sql-Table names
class sqlTableNames():
    # sql table names
    mgfield = "mgfield"
    mgfieldraw = "mgfieldraw"
    sysstats = "sysstats"
    netstats = "netstats"
    temperature = "temperature"

# main class
class mgfield():

    # delete data when stored to mysql
    def cleanupDataArray(startTime):
        currentDataSets = str(len(dataArray.keys()))
        logging.writeDebug("[MGField] cleaning up dataArray, current dataSets: " + currentDataSets + ", removing: " + str(startTime))
        dataArray.pop(startTime)
        remainingDataSets = str(len(dataArray.keys()))
        logging.writeDebugHigh("[MGField] remaining dataSets in dataArray: " + remainingDataSets + " (" + str(list(dataArray.keys())) + ")")

    # calculate average value from timestamp and return it
    def calcAvg(startTime, measuredValuesList):
        # first calculate average value and save it to sql
        calculator = 0.0
        valueCount = 0
        for key in measuredValuesList:
            calculator += dataArray[startTime][key]["measurement_result"]
            valueCount += 1
        avg_result = calculator/valueCount
        return avg_result
    
    # check and store values of temperature and sysstats if unsaved data is stored in dataArrayOther
    def checkUnsavedDataAndSave(self):
        sqlCommandsToExecute = {}
        finishedSavings = []

        # get keys (is data so to save)
        for key in dataArrayOther.keys():
            if dataArrayOther[key]: sqlCommandsToExecute[key] = dataArrayOther[key]

        # execute commands
        if sqlCommandsToExecute:
            commandsBeforeSave = str(len(sqlCommandsToExecute.keys()))
            logging.writeDebug("[SQLHandler] Found remaining data to save, commands to execute: " + str(len(sqlCommandsToExecute)))
            for data in sqlCommandsToExecute.keys():
                
                try:
                    self.mySQLCursor.execute(sqlCommandsToExecute[data])
                    # when executed successfully remove data from global tmp storage and local dict
                    dataArrayOther.pop(data)
                    finishedSavings.append(data)
                except:
                    logging.writeError("[SQLHandler] Failed to save remaining data")
                    logging.writeError("[SQLHandler] Failed command: " + sqlCommandsToExecute[data])
                    logging.writeExecError(traceback.format_exc())

            # remove from local tmp storage to verify successful write
            for data in finishedSavings: sqlCommandsToExecute.pop(data)

            logging.writeDebug("[SQLHandler] Saved remaining data, before: " + commandsBeforeSave + ", after: " + str(len(sqlCommandsToExecute.keys())))
            logging.writeDebugHigh("[SQLHandler] remaining keys: " + str(sqlCommandsToExecute.keys()))
            

    # prepare data storing for system statistics --> save it to dataArray; make it storeable later
    def storeSysStatsData(self, measurementTime, sysData, netData):
        formattedTimestamp = mySQLHandler.formatDate(measurementTime)
        
        # build dataString for sqlCommand builder
        sysDataString = ""
        for key in sysData.keys():
            if not sysDataString: sysDataString = str(sysData[key])
            else: sysDataString += "__" + str(sysData[key])

        netDataString = ""
        for key in netData.keys():
            if not netDataString: netDataString = str(netData[key])
            else: netDataString += "__" + str(netData[key])
        
        try:
            sysStatsSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.sysstats, formattedTimestamp, sysDataString)
            netStatsSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.netstats, formattedTimestamp, netDataString)

            # save SQL commands
            dataArrayOther["sysstats_" + str(formattedTimestamp)] = sysStatsSQLCommand
            dataArrayOther["netstats_" + str(formattedTimestamp)] = netStatsSQLCommand

            logging.writeDebugHigh("[SysStats] Saved SQL commands of SysStats and NetStats")
        except:
            logging.writeError("[SysStats] Failed to build SQL commands for SysStats and NetStats")
            logging.writeExecError(traceback.format_exc())

    # prepare data storing for temperature values
    def storeTemperatureData(self, measurementTime, temperatureValue):
        formattedTimestamp = mySQLHandler.formatDate(measurementTime)
        try:
            temperatureSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.temperature, formattedTimestamp, str(temperatureValue))
        
            dataArrayOther["temperature_" + str(formattedTimestamp)] = temperatureSQLCommand
            logging.writeDebugHigh("[Temperature] Saved SQL commands of Temperature")
        except:
            logging.writeError("[Temperature] Failed to SQL command for temperature")
            logging.writeExecError(traceback.format_exc())

    # prepare data storing and calculation for MGField values
    def storeMGFieldData(self, numberOfValuesToCollect, startTime):
        logging.write("[MGField] storing data for timestamp: " + str(startTime))

        measuredValuesList = []
        # validate that enough data has been collected, therefore select only measured values, skip time_delta etc.
        for key in dataArray[startTime].keys():
            if key != "time_delta": measuredValuesList.append(key)
        
        if not len(measuredValuesList) == numberOfValuesToCollect:
            logging.writeError("[MGField] data set: " + str(startTime) + " is malformed - expected " + str(numberOfValuesToCollect) + " values, got " + str(len(dataArray[startTime].keys())))
            return
        
        # format timestamp
        formattedTimestamp = mySQLHandler.formatDate(startTime)
        
        avg_result = mgfield.calcAvg(startTime, measuredValuesList)

        # build dataString for mgfield table
        dataString = str(avg_result) + "__" + str(dataArray[startTime]["time_delta"])
        try:
            mgfieldSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.mgfield, formattedTimestamp, dataString)
            self.mySQLCursor.execute(mgfieldSQLCommand)
        except:
            logging.writeError("[MGField] (ERR: 1) Failed to store average measurement data to SQL server")
            logging.writeExecError(traceback.format_exc())

        try:
            # for each measurement collect all required data and format it to make it storeable
            for timestamp in measuredValuesList:

                formattedTimestampLong = mySQLHandler.formatDateLong(timestamp)
                dataString = ""
                dataString += str(dataArray[startTime][timestamp]["x_value"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["y_value"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["z_value"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["measurement_result"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["measurement_duration"])
                mgfieldrawSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.mgfieldraw, formattedTimestampLong, dataString)
                self.mySQLCursor.execute(mgfieldrawSQLCommand)

        except:
            logging.writeError("[MGField] (ERR: 2) Failed to store complete measurement data to SQL server")
            logging.writeExecError(traceback.format_exc())

        # before committing everything check for unsaved SysStats and Temperature data
        try:
            mgfield.checkUnsavedDataAndSave(self)
        except:
            logging.writeError("[SQLHandler] Failed to save temperature/SysStats data to SQL server")
            logging.writeExecError(traceback.format_exc())
        
        # commit data 
        try: self.mySQLConnection.commit()
        except:
            logging.writeError("[MGField] Failed to commit data to SQL server")
            logging.writeExecError(traceback.format_exc())
        

        # finally remove this data set from dataArray to remove garbage
        mgfield.cleanupDataArray(startTime)

    # selects and sets data sources
    def setDataSources(self):
        if config.useVirtualEnvironment:
            logging.writeDebug("Using virtual sensors")
            from scripts.virtualSensor import virtualSensor
            self.dataSource = getattr(virtualSensor, "sensor")
            self.temperatureSource = getattr(virtualSensor, "temperatureSensor")
            self.sysStatsSource = getattr(virtualSensor, "sysStatsSensor")
            self.netStatsSource = getattr(virtualSensor, "netStatsSensor")

        else:
            logging.writeDebug("Using physical sensors")
            from scripts.physicalSensor import physicalSensor
            self.dataSource = getattr(physicalSensor, "sensor")
            self.temperatureSource = getattr(physicalSensor, "temperatureSensor")
            self.sysStatsSource = getattr(virtualSensor, "sysStatsSensor")
            self.netStatsSource = getattr(virtualSensor, "netStatsSensor")


    # will be started as thread, collects data and saves to global var
    def mgFieldDataCollectorThread(self, startTime):

        startTimeThreadRaw = time.time()

        # time when this thread will is started
        startTimeThread = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
        # get data
        dataFromSensor = self.dataSource()

        # extract data and save it to correct locations
        dataArray[startTime][startTimeThread] = {} 
        dataArray[startTime][startTimeThread]["x_value"] = dataFromSensor[0]
        dataArray[startTime][startTimeThread]["y_value"] = dataFromSensor[1]
        dataArray[startTime][startTimeThread]["z_value"] = dataFromSensor[2]

        # formula for calculating the magnitude of the earth's magnetic field
        measurement_result = (((dataFromSensor[0] * dataFromSensor[0]) + (dataFromSensor[1] * dataFromSensor[1]) + (dataFromSensor[2] * dataFromSensor[2])) ** 0.5)         
        logging.writeDebug("[MGField] got " + str(measurement_result) + " as value")

        dataArray[startTime][startTimeThread]["measurement_result"] = measurement_result
        
        # save endTimeThread to calculate 
        endTimeThreadRaw = time.time()
        dataArray[startTime][startTimeThread]["measurement_duration"] = str(endTimeThreadRaw - startTimeThreadRaw)
        logging.writeDebugHigh("[MGField] gettting data for measurement '" + str(startTimeThread) + "' took " + str(endTimeThreadRaw - startTimeThreadRaw) + "ms")

    
    # collects data from MGField sensor
    def mgFieldDataCollector(self, rerunInterval, measurementInterval, numberOfValuesToCollect):

        startTimeRaw = time.time()
        # time when one measurement interval is started
        startTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
        dataArray[startTime] = {}
        logging.write("[MGField] started interval at " + startTime)

        for task in range(numberOfValuesToCollect):
            loopStartTime = time.time()
            tasks[startTime] = {}
            tasks[startTime][str(task) + "-" + str(startTime)] = threading.Thread(target=mgfield.mgFieldDataCollectorThread, args=(self,startTime))
            tasks[startTime][str(task) + "-" + str(startTime)].start()
            loopEndTime = time.time()
            time.sleep(measurementInterval - int(loopEndTime - loopStartTime))

        # wait until all tasks are finished
        for task in tasks[startTime]:
            tasks[startTime][task].join()

        # save time when finished, to calc delta of measurement
        finishedTimeRaw = time.time()

        time_delta = round(finishedTimeRaw - startTimeRaw - rerunInterval, 5)
        dataArray[startTime]["time_delta"] = time_delta
        logging.writeDebug("[MGField] collecting data for " + str(startTime) + " took " + str(finishedTimeRaw - startTimeRaw) + " s, expected: " + str(rerunInterval) + " (delta: " + str(time_delta) + ")\n")
        mgfield.storeMGFieldData(self, numberOfValuesToCollect, startTime)


    # collects system and network data
    def sysStatsDataCollector(self):
        measurementTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sysData = self.sysStatsSource()
        netData = self.netStatsSource()
        logging.write("[SysStats] collected system statistics successfully")

        mgfield.storeSysStatsData(self, measurementTime, sysData, netData)


    # collects data from temperature sensor
    def temperatureDataCollector(self):
        measurementTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        temperatureValue = self.temperatureSource()
        logging.write("[Temperature] got " + str(temperatureValue) + "°C as value")

        mgfield.storeTemperatureData(self, measurementTime, temperatureValue)

    
    # function that will automatically be started as thread 
    # to collect MGField data
    def runnerMGField(self, rerunInterval, measurementInterval, numberOfValuesToCollect):

        # initialize rerun of this thread
        threading.Timer(rerunInterval, mgfield.runnerMGField, [self, rerunInterval, measurementInterval, numberOfValuesToCollect]).start()

        logging.writeDebug("[MGField] registered rerun of MGField in " + str(rerunInterval) + " seconds")
        threading.Thread(target=mgfield.mgFieldDataCollector, args=(self, rerunInterval, measurementInterval, numberOfValuesToCollect)).start()
        

    # function that will automatically be started as thread 
    # to collect sysStats data
    def runnerSysStats(self, sysstatsCollectionInterval):

        # initialize rerun of thread
        threading.Timer(sysstatsCollectionInterval, mgfield.runnerSysStats, [self, sysstatsCollectionInterval]).start()
        
        logging.writeDebug("[SysStats] registered rerun of SysStats in " + str(sysstatsCollectionInterval) + " seconds")
        threading.Thread(target=mgfield.sysStatsDataCollector, args=(self,)).start()


    # function that will automatically be started as thread 
    # to collect temperature data
    def runnerTemperature(self, temperatureCollectionInterval):
        
        # initialize rerun of thread
        threading.Timer(temperatureCollectionInterval, mgfield.runnerTemperature, [self, temperatureCollectionInterval]).start()
        
        logging.writeDebug("[Temperature] registered rerun of temperatureCollection in " + str(temperatureCollectionInterval) + " seconds")
        threading.Thread(target=mgfield.temperatureDataCollector, args=(self,)).start()

    
    def __init__(self):
        logging.write("Starting MGFieldPy data collection")
        logging.writeDebug("Running version: " + str(config.VERSION))
        logging.write("Setting datasource...")
        mgfield.setDataSources(self)

        # calculate interval of seconds until rerun
        rerunInterval = config.measurementInterval*config.numberOfValuesToCollect

        # open mySQL connection
        self.mySQLConnection = mySQLHandler.openConnection()
        
        # if connection fails, return
        if not self.mySQLConnection: 
            logging.writeError("failed connecting to mySQL server, check config - exiting.")
            return
        
        # get cursor
        self.mySQLCursor = self.mySQLConnection.cursor()
        logging.write("Connected successfully to mySQL server and database")

        # start data collection
        mgfield.runnerMGField(self, rerunInterval, config.measurementInterval, config.numberOfValuesToCollect)
        mgfield.runnerSysStats(self, config.sysstatsCollectionInterval)
        if config.temperatureCollectionEnabled: mgfield.runnerTemperature(self, config.temperatureCollectionInterval)

# initilize script
if __name__ == "__main__":
    mgfield()   