#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by ZyzonixDevelopments 
# -
# date      | 25/04/2021
# python-v  | 3.5.3
# -
# file      | mgfield.py
# project   | MGFieldPy
# project-v | 0.1
# 
import os
import sys
import threading
from configparser import ConfigParser
from datetime import date, datetime
from static import dataHandler, xlsxHandler

# writing, if enabled, console output to .txt-file
class LogWriter(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            # writing to files
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

# core class
class Core(object):

    # console time service | return the time --> formatted for console
    def getCTime(self):
        curTime = "[" + str(datetime.now().strftime("%H:%M:%S")) + "]"
        return curTime

    # file time stamp service | returns the time --> formatted for excel table
    def getFTime(self):
        curTime = str(datetime.now().strftime("%H:%M:%S"))
        return curTime

    # file date service | returns the date
    def getFDate(self):
        curDate = "" + str(date.today().strftime("%Y-%m-%d"))
        return curDate   

    # log writing initialization
    def writeLog(self):
        logFile = open(os.getcwd() + "/logs/" + str(date.today()) + "_" + str(datetime.now().strftime("%H-%M-%S")) + "_log.txt", "w")
        sys.stdout
        sys.stdout = LogWriter(sys.stdout, logFile)
                    

    # setting up enviroment
    def setupEnvironment(self, sheetName=str(date.today())):
        print(self.getCTime(), "performing environment setup")
        # creating day-based output directory
        if not os.path.exists(self.baseFilePath + str(date.today()) +"/"):
            os.mkdir(self.baseFilePath + str(date.today()) +"/")
        # starting xlsx-file setup
        xlsxFile = xlsxHandler.prepareXLSXFile(self, sheetName)
        # saving file data globally
        self.xlsxFileData = [xlsxFile, sheetName]
        # CONTINUE HERE

    # importing all required values from static/config.ini
    def importConfig(self):
        print(self.getCTime(), "importing configuration")
        # initializing config reading module
        confPars = ConfigParser()
        configFile = os.getcwd() + "/static/config.ini"
        # reading file
        confPars.read(configFile)
        # collecting all values
        self.MES_TIME = float(confPars["CONFIGURATION"]["MES_TIME"])
        self.baseFilePath = confPars["CONFIGURATION"]["basefilepath"]
        self.log = confPars["CONFIGURATION"].getboolean("log")
        self.input = confPars["CONFIGURATION"]["input"]
        self.average = int(confPars["CONFIGURATION"]["average"])

    # static lists
    global mgfield_values 
    mgfield_values = []
    global temp_values
    temp_values = []
    
    # collecting all required data
    def collectData(self, mgfield_value, temp_value):
        row_content = [self.getFDate(), self.getFTime(), mgfield_value, temp_value, dataHandler.getSystemStatistics()]
        # writing data to file
        xlsxHandler.writeToXLSXFile(self, row_content)

    # calculating average values from the two given lists
    def calculateAverage(self, temp_list, mgfield_list):
        temp = 0.0
        for item in temp_list:
            temp = float(temp) + float(item)
        result_temp = temp/float(len(temp_list))

        mgfield = 0.0
        for item in mgfield_list:
            mgfield = mgfield + item
        result_mgfield = mgfield/len(mgfield_list)
        # starting collecting process
        Core.collectData(self, result_mgfield, result_temp)

    # data retrieving
    def MGFieldCore(self):
        threading.Timer(self.MES_TIME, Core.MGFieldCore, [self]).start()
        mgfield_values.append(self.inputMethod(self))
        temp_values.append(dataHandler.getTemperature())
        # checking if the max limit has been reached
        if len(mgfield_values) == self.average:
            Core.calculateAverage(self, temp_values, mgfield_values)
            temp_values.clear()
            mgfield_values.clear()

    # initiation function
    def __init__(self):
        print(self.getCTime(), "starting MGFieldPy")
        self.importConfig()
        # checking if log is enabled
        if self.log:
            print(self.getCTime(), "initializing logwriter")
            self.writeLog()
        # row indicator for XLSX-Sheet
        self.xlsxRow = 1
        # starting environment setup  
        self.setupEnvironment()
        # call inputmethod = self.inputMethod(self)
        dataHandler.handleInputMethod(self)  
        print("\n" + self.getCTime(), "starting measurement - " + str(date.today()) + "\n")
        self.MGFieldCore()
        
        

if __name__ == "__main__":
    Core()
