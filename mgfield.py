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
# project-v | 0.2
# 
import os
import sys
import threading
from configparser import ConfigParser
from datetime import date, datetime
from static import dataHandler, xlsxHandler

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
        curTime = "[" + str(datetime.now().strftime("%H:%M:%S")) + "]"
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
                    

    # Bereitet die Arbeitsumgebung vor
    def setupEnvironment(self, sheetName=str(date.today())):
        print(self.getCTime(), "performing environment setup")
        # Erstellt einen Ordner mit dem aktuellen Datum
        if not os.path.exists(self.baseFilePath + str(date.today()) +"/"):
            os.mkdir(self.baseFilePath + str(date.today()) +"/")
        # Initialisiert die Excel-Datei
        xlsxFile = xlsxHandler.prepareXLSXFile(self, sheetName)
        # Speichert den Pfad zur Excel-Datei global
        self.xlsxFileData = [xlsxFile, sheetName]

    # Liest die Konfiguration aus static/config.ini
    def importConfig(self):
        print(self.getCTime(), "importing configuration")
        confPars = ConfigParser()
        configFile = os.getcwd() + "/static/config.ini"
        confPars.read(configFile)
        # Speichert alle notwendigen Werte global
        self.MES_TIME = float(confPars["CONFIGURATION"]["MES_TIME"])
        self.baseFilePath = confPars["CONFIGURATION"]["basefilepath"]
        self.log = confPars["CONFIGURATION"].getboolean("log")
        self.input = int(confPars["CONFIGURATION"]["input"])
        self.average = int(confPars["CONFIGURATION"]["average"])

    # Statische/globale Listen
    global mgfield_values 
    mgfield_values = []
    global mgfield_values2 
    mgfield_values2 = []
    global temp_values
    temp_values = []
    
    # Sammelt und schreibt alle notwendigen Daten in die Datei
    def collectData(self, mgfield_value, temp_value, mgfield_value2):
        try:
            row_content = [self.getFDate(), self.getFTime(), mgfield_value, mgfield_value2, temp_value, dataHandler.getSystemStatistics()]
            # Schreibt Daten in die Excel-Datei
            xlsxHandler.writeToXLSXFile(self, row_content)
        except Exception as e:
            print(self.getCTime(), "something went wrong ERR: 2")
            print(e)

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
            print(self.getCTime(), "something went wrong ERR: 1")
            print(e)

    # Core-Funktion
    def MGFieldCore(self):
        # Planen des nächsten durchlaufs
        threading.Timer(self.MES_TIME, Core.MGFieldCore, [self]).start()
        try:
            mgfield_values.append(self.inputMethod(self))
            mgfield_values2.append(self.inputMethod2(self))
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
        # Überprüft ob das Logschreiben aktiviert ist, wenn ja --> initialisiert das Logschreiben
        if self.log:
            print(self.getCTime(), "initializing logwriter")
            self.writeLog()
        # Zeilen-Indikator für die Excel-Tabelle
        self.xlsxRow = 1
        # Initialisiert das Erstellen der Arbeitsumgebung
        self.setupEnvironment()
        # Sucht die Eingabemethode aus (abhängig von der Konfiguration)
        dataHandler.handleInputMethod(self)  
        print("\n" + self.getCTime(), "starting measurement - " + str(date.today()) + "\n")
        # Startet die Core-Funktion
        self.MGFieldCore()
        
if __name__ == "__main__":
    Core()
