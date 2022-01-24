#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY and ZyzonixDevelopments 
# -
# date      | 25/04/2021
# python-v  | 3.5.3
# -
# file      | mgfield.py
# project   | MGFieldPy
# project-v | 1.1
# 
#
# Required packages (pip3)
# pip3 install board
# pip3 install openpyxl
#
import os
import sys
import threading
from configparser import ConfigParser
from datetime import date, datetime
from static import xlsxHandler
from static import dataHandler
from static import csvHandler

# Schreibt eine Log-Datei
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

# Hauptklasse
class Core(object):

    # Zeitservice für die Consolenausgabe
    def getCTime(self):
        time = datetime.now().strftime("%H:%M:%S.%f")
        timeFormatted = time[:-4]
        curTime = "[" + str(timeFormatted) + "]"
        return curTime

    # Zeitservice für die Excel-Datei
    def getFTime(self):
        curTime = str(datetime.now().strftime("%H:%M:%S"))
        return curTime

    # Datumsservice für die Excel-Datei
    def getFDate(self):
        curDate = "" + str(date.today().strftime("%Y-%m-%d"))
        return curDate   

    # Initialisiert das Logschreiben
    def writeLog(self):
        logFile = open(os.getcwd() + "/logs/" + str(date.today()) + "_" + str(datetime.now().strftime("%H-%M-%S")) + "_log.txt", "w")
        sys.stdout
        sys.stdout = LogWriter(sys.stdout, logFile)
                    

    # Liest die Konfiguration aus static/config.ini
    def importConfig(self):
        print(self.getCTime(), "importing configuration")
        confPars = ConfigParser()
        configFile = os.getcwd() + "/static/config.ini"
        confPars.read(configFile)
        # Speichert alle notwendigen Werte global
        self.MES_TIME = float(confPars["CONFIGURATION"]["MES_TIME"])
        self.baseFilePath = os.getcwd() + "/output"
        self.log = confPars["CONFIGURATION"].getboolean("log")
        self.input = int(confPars["CONFIGURATION"]["input"])
        self.average = int(confPars["CONFIGURATION"]["average"])
        self.output = int(confPars["CONFIGURATION"]["output"])
        self.sensors = int(confPars["CONFIGURATION"]["sensors"])
        self.version = float(confPars["CONFIGURATION"]["version"])

    # Statische/globale Listen
    global mgfield_values 
    mgfield_values = []
    global mgfield_values2 
    mgfield_values2 = []
    global temp_values
    temp_values = []
    
    # Sammelt und schreibt alle notwendigen Daten in die Datei
    def collectData(self, mgfield_value, temp_value, mgfield_value2):
        # Sammeln der Daten
        try:
            row_content = [self.getFDate(), self.getFTime(), mgfield_value, mgfield_value2, temp_value, dataHandler.getSystemStatistics()]
        except Exception as e:
            print("\n" + self.getCTime(), "something went wrong ERR: 4")
            print(e)
            print("\n")
            exit()

        try:
            # Auswahl der Outputdatei
            # 0 = CSV
            if self.output == 0:
                # Schreibt Daten in die CSV-Datei
                csvHandler.writeToCSVFile(self, row_content)
                print("\n" + self.getCTime(), "wrote data to csv-file \n")
            elif self.output == 1:
                # Schreibt Daten in die Excel-Datei
                xlsxHandler.writeToXLSXFile(self, row_content)
                print("\n" + self.getCTime(), "wrote data to xlsx-file \n")
            else:
                print("\n" + self.getCTime(), "something went wrong ERR: 3 [no output file selected]\n")

        except Exception as e:
            print("\n" + self.getCTime(), "something went wrong ERR: 2")
            print(e)
            print("\n")

    # Berechnet den Durchschnittswert von Temperatur und den beiden Magnetfeldsensoren
    def calculateAverage(self, temp_list, mgfield_list, mgfield_list2):
        try:
            temp = 0.0
            for item in temp_list:
                temp = float(temp) + float(item)
            result_temp = temp/float(len(temp_list))

            mgfield = 0.0
            for item in mgfield_list:
                mgfield = mgfield + item
            result_mgfield = mgfield/len(mgfield_list)
            
            mgfield2 = 0.0
            for item in mgfield_list2:
                mgfield2 = mgfield2 + item
            result_mgfield2 = mgfield2/len(mgfield_list2)

            # Startet das Schreiben in die Datei
            Core.collectData(self, result_mgfield, result_temp, result_mgfield2)
        except Exception as e:
            print("\n" + self.getCTime(), "something went wrong ERR: 1")
            print(e)
            print("\n")

    # Core-Funktion
    def MGFieldCore(self):
        # Planen des nächsten durchlaufs
        threading.Timer(self.MES_TIME, Core.MGFieldCore, [self]).start()
        try:
            mgfield_values.append(self.inputMethod(self))
            # Überprüfung der Sensoranzahl
            if not self.sensors == 1:
                mgfield_values2.append(self.inputMethod2(self))
            else:
                mgfield_values2.append(1)
            temp_values.append(dataHandler.getTemperature())
            # Überprüfen ob der Durchschnittswert berechnet werden muss
            if len(mgfield_values) == self.average:
                # Berechnen des Durchschnittswertes
                Core.calculateAverage(self, temp_values, mgfield_values, mgfield_values2)
                temp_values.clear()
                mgfield_values.clear()
                mgfield_values2.clear()
        except Exception as e:
            print(self.getCTime(), "something went wrong ERR: 0")
            print(e)

    # Initialisiert das Skript
    def __init__(self):
        print(self.getCTime(), "starting MGFieldPy")
        self.importConfig()
        print(self.getCTime(), "running version:", self.version)
        # Überprüft ob das Logschreiben aktiviert ist, wenn ja --> initialisiert das Logschreiben
        if self.log:
            print(self.getCTime(), "initializing logwriter")
            self.writeLog()
        
        # Initialisiert das Erstellen der Arbeitsumgebung
        dataHandler.performSetup(self)
        # Sucht die Eingabemethode aus (abhängig von der Konfiguration)
        dataHandler.handleInputMethod(self)  
        print("\n" + self.getCTime(), "starting measurement - " + str(date.today()) + "\n")
        # Startet die Core-Funktion
        self.MGFieldCore()
        
if __name__ == "__main__":
    Core()
