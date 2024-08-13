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
# project       | mgfield
# version       | 1.1.0
#
import time
import threading
from datetime import datetime, timezone
import traceback
import json

# import custom scripts
from scripts.logHandler import logging
from scripts.mysqlHandler import mySQLHandler
from scripts.logHandler import globalVars

# default path to config
CONFIG = "/root/.config/mgfield/config.json"

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
    def storeSysStatsData(self, measurementTimeUTC, measurementTimeLocal, cpuData, memData, netData, sensData):
        formattedTimestampUTC = mySQLHandler.formatDate(measurementTimeUTC)
        
        # build dataString for sqlCommand builder
        # sysData table
        sysDataString = str(measurementTimeLocal)
        for key in cpuData.keys(): sysDataString += "__" + str(cpuData[key])
        for key in memData.keys(): sysDataString += "__" + str(memData[key])
        for key in sensData.keys(): sysDataString += "__" + str(sensData[key])

        # netData table
        netDataString = str(measurementTimeLocal)
        for key in netData.keys(): netDataString += "__" + str(netData[key])
        
        try:
            sysStatsSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.sysstats, formattedTimestampUTC, sysDataString)
            netStatsSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.netstats, formattedTimestampUTC, netDataString)

            # save SQL commands
            dataArrayOther["sysstats_" + str(formattedTimestampUTC)] = sysStatsSQLCommand
            dataArrayOther["netstats_" + str(formattedTimestampUTC)] = netStatsSQLCommand

            logging.writeDebugHigh("[SysStats] Saved SQL commands of SysStats and NetStats")
        except:
            logging.writeError("[SysStats] Failed to build SQL commands for SysStats and NetStats")
            logging.writeExecError(traceback.format_exc())

    # prepare data storing for temperature values
    def storeTemperatureData(self, measurementTimeUTC, measurementTimeLocal, temperatureValue):
        formattedTimestampUTC = mySQLHandler.formatDate(measurementTimeUTC)
        formattedTimestampLocal = mySQLHandler.formatDate(measurementTimeLocal)
        try:
            temperatureSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.temperature, formattedTimestampUTC, str(formattedTimestampLocal) + "__" + str(temperatureValue))
        
            dataArrayOther["temperature_" + str(formattedTimestampUTC)] = temperatureSQLCommand
            logging.writeDebugHigh("[Temperature] Saved SQL commands of Temperature")
        except:
            logging.writeError("[Temperature] Failed to SQL command for temperature")
            logging.writeExecError(traceback.format_exc())

    # prepare data storing and calculation for MGField values
    def storeMGFieldData(self, numberOfValuesToCollect, startTime, startTimeLocal):
        logging.write("[MGField] storing data for timestamp: " + str(startTime))

        measuredValuesList = []
        # validate that enough data has been collected
        for key in dataArray[startTime].keys(): measuredValuesList.append(key)
        
        if not len(measuredValuesList) == numberOfValuesToCollect:
            logging.writeError("[MGField] data set: " + str(startTime) + " is malformed - expected " + str(numberOfValuesToCollect) + " values, got " + str(len(dataArray[startTime].keys())))
            return

        # mySQL boolean 0(false)/1(true)
        firstValueNotWritten = 1
        # store all x-,y- and z-values from each measurement
        try:
            # for each measurement collect all required data and format it to make it storeable
            for timestamp in measuredValuesList:
                
                formattedTimestampLong = mySQLHandler.formatDateLong(timestamp)
                dataString = str(dataArray[startTime][timestamp]["startTimeThreadLocal"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["x_value"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["y_value"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["z_value"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["out_value"])+ "__"
                dataString += str(dataArray[startTime][timestamp]["measurement_result"]) + "__"
                dataString += str(dataArray[startTime][timestamp]["measurement_duration"]) + "__"
                dataString += str(firstValueNotWritten) 
                mgfieldrawSQLCommand = mySQLHandler.commandBuilder(sqlTableNames.mgfield, formattedTimestampLong, dataString)
                self.mySQLCursor.execute(mgfieldrawSQLCommand)
                firstValueNotWritten = 0

        except:
            logging.writeError("[MGField] Failed to store measurement data (x-,y-,-z-values) to SQL server")
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
        if self.useVirtualEnvironment:
            logging.writeDebug("Using virtual sensors")
            from scripts.virtualSensor import virtualSensor
            self.dataSource = getattr(virtualSensor, "sensor")
            self.temperatureSource = getattr(virtualSensor, "temperatureSensor")

        else:
            logging.writeDebug("Using physical sensors")
            from scripts.physicalSensor import physicalSensor
            from scripts.virtualSensor import virtualSensor
            self.dataSource = getattr(physicalSensor, "sensor")
            self.temperatureSource = getattr(physicalSensor, "temperatureSensor")
        
        from scripts.systemMonitoring import systemMonitoring
        self.memStatsSource = getattr(systemMonitoring, "mem")
        self.cpuStatsSource = getattr(systemMonitoring, "cpu")
        self.netStatsSource = getattr(systemMonitoring, "net")
        self.sensStatsSource = getattr(systemMonitoring, "internalTemperatureSensors")


    # will be started as thread, collects data and saves to global var
    def mgFieldDataCollectorThread(self, startTime):

        startTimeThreadRaw = time.time()

        # time when this thread is started
        startTimeThread = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S.%f")
        startTimeThreadLocal = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")

        # get data
        dataFromSensor = self.dataSource()

        # extract data and save it to correct locations
        dataArray[startTime][startTimeThread] = {} 
        dataArray[startTime][startTimeThread]["startTimeThreadLocal"] = str(startTimeThreadLocal)
        dataArray[startTime][startTimeThread]["x_value"] = dataFromSensor[0]
        dataArray[startTime][startTimeThread]["y_value"] = dataFromSensor[1]
        dataArray[startTime][startTimeThread]["z_value"] = dataFromSensor[2]
        dataArray[startTime][startTimeThread]["out_value"] = dataFromSensor[3]

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
        startTime = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S.%f")
        startTimeLocal = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
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
        logging.writeDebug("[MGField] collecting data for " + str(startTime) + " took " + str(finishedTimeRaw - startTimeRaw) + " s, expected: " + str(rerunInterval) + " (delta: " + str(time_delta) + ")\n")
        mgfield.storeMGFieldData(self, numberOfValuesToCollect, startTime, startTimeLocal)


    # collects system and network data
    def sysStatsDataCollector(self):
        targets = {"target1":self.target1, "target2":self.target2, "target3":self.target3}
        measurementTimeUTC = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        measurementTimeLocal = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cpuData = self.cpuStatsSource()
        memData = self.memStatsSource()
        netData = self.netStatsSource(targets)
        sensData = self.sensStatsSource()
        logging.write("[SysStats] collected system statistics successfully")

        mgfield.storeSysStatsData(self, measurementTimeUTC, measurementTimeLocal, cpuData, memData, netData, sensData)


    # collects data from temperature sensor
    def temperatureDataCollector(self):
        measurementTimeUTC = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        measurementTimeLocal = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        temperatureValue = self.temperatureSource(self)
        logging.write("[Temperature] got " + str(temperatureValue) + "°C as value")

        mgfield.storeTemperatureData(self, measurementTimeUTC, measurementTimeLocal, temperatureValue)

    
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

    # monitor running threads for debugging purposes
    def threadWatcher(self):
        while True: 
            threadInfoList = threading.enumerate()
            logging.writeDebug("[ThreadWatcher] Currently running threads/timers: " + str(len(threadInfoList)))
            logging.writeDebugHigh("Type | Thread-Name | is_stopped | ident | native_id")
            for thread in threadInfoList:
                logging.writeDebugHigh("[ThreadWatcher] " + thread.__class__.__name__ + ", " + str(vars(thread)["_name"]) + ", " + str(vars(thread)["_is_stopped"]) + ", " + str(vars(thread)["_ident"]) + ", " + str(vars(thread)["_native_id"]))
            time.sleep(self.threadWatcherInterval)

    # import config from file
    def importConfig(self):
        try:
            configFile = open(CONFIG)
            configContent = json.load(configFile)
            self.version = configContent["version"]
            self.measurementInterval = configContent["measurement"]["measurementInterval"]
            self.numberOfValuesToCollect = configContent["measurement"]["numberOfValuesToCollect"]
            self.useVirtualEnvironment = bool(configContent["measurement"]["useVirtualEnvironment"])
            self.temperatureCollectionEnabled = bool(configContent["measurement"]["temperatureCollectionEnabled"])
            self.temperatureCollectionInterval = configContent["measurement"]["temperatureCollectionInterval"]
            self.temperatureSensorPath = configContent["measurement"]["temperatureSensorPath"]
            self.sysstatsCollectionInterval = configContent["monitoring"]["sysstats"]["sysstatsCollectionInterval"]
            self.threadWatcherInterval = configContent["monitoring"]["sysstats"]["threadWatcherInterval"]
            self.target1 = configContent["monitoring"]["network"]["target1"]
            self.target2 = configContent["monitoring"]["network"]["target2"]
            self.target3 = configContent["monitoring"]["network"]["target3"]
            debugSetting = bool(configContent["logging"]["debuggingEnabled"])
            debugHighSetting = bool(configContent["logging"]["higherDebugLevelEnabled"])
            # set both log variables globally
            globalVars(debugSetting, debugHighSetting)
            self.mysqlServerIP = configContent["mysql"]["mysqlServerIP"]
            self.mysqlUsername = configContent["mysql"]["mysqlUsername"]
            self.mysqlPassword = configContent["mysql"]["mysqlPassword"]
            self.mysqlDatabaseName = configContent["mysql"]["mysqlDatabaseName"]

            configFile.close()
        except:
            logging.writeError("Failed to load config file from: " + CONFIG)
            logging.writeExecError(traceback.print_exc())
            return False
        return True

    def __init__(self):
        logging.write("--------[INITIALIZING]--------")
        logging.write("Starting MGFieldPy data collection")
        
        # load config, return if fails
        logging.write("Reading config...")
        configResult = mgfield.importConfig(self)
        if not configResult: return
        logging.writeDebug("Running version: " + str(self.version))
        logging.write("Setting datasource...")
        mgfield.setDataSources(self)

        # calculate interval of seconds until rerun
        rerunInterval = self.measurementInterval*self.numberOfValuesToCollect

        # open mySQL connection
        self.mySQLConnection = mySQLHandler.openConnection(self)
        
        # if connection fails, return
        if not self.mySQLConnection: 
            logging.writeError("failed connecting to mySQL server, check config - exiting.")
            return
        
        # get cursor
        self.mySQLCursor = self.mySQLConnection.cursor()
        logging.write("Connected successfully to mySQL server and database")

        # wait until timestamp xx:xx:xx.000 is reached --> to make data more easy comparable with other stations
        while True:
            if datetime.now().microsecond == 0:
                # start data collection
                threading.Thread(target=mgfield.runnerMGField, args=[self, rerunInterval, self.measurementInterval, self.numberOfValuesToCollect]).start()
                threading.Thread(target=mgfield.runnerSysStats, args=[self, self.sysstatsCollectionInterval]).start()
                if self.temperatureCollectionEnabled: mgfield.runnerTemperature(self, self.temperatureCollectionInterval)
                mgfield.threadWatcher(self)
                break

# initialize script
if __name__ == "__main__":
    mgfield()   
