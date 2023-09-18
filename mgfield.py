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
# project-v | 1.11
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
        timeFormatted = time[:-5]
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
    global x1_values
    x1_values = []
    global y1_values
    y1_values = []
    global z1_values
    z1_values = []
    global temp_values
    temp_values = []
    
    # Sammelt und schreibt alle notwendigen Daten in die Datei
    def collectData(self, x1, y1, z1, mgfield_value, temp_value, x2, y2, z2):
        # Sammeln der Daten
        try:
            row_content = [self.getFDate(), self.getFTime(), x1, y1, z1, mgfield_value, x2, y2, z2, temp_value, dataHandler.getSystemStatistics()]
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
    def calculateAverage(self, temp_list, x1_list, y1_list, z1_list, mgfield_list):
        try:
            temp = 0.0
            for item in temp_list:
                temp = float(temp) + float(item)
            result_temp = temp/float(len(temp_list))

            x1 = 0.0
            for item in x1_list:
                x1 = x1 + item
            result_x1 = x1/len(x1_list)

            y1 = 0.0
            for item in y1_list:
                y1 = y1 + item
            result_y1 = y1/len(y1_list)

            z1 = 0.0
            for item in z1_list:
                z1 = z1 + item
            result_z1 = z1/len(z1_list)        

            mgfield = 0.0
            for item in mgfield_list:
                mgfield = mgfield + item
            result_mgfield = mgfield/len(mgfield_list)

            # Startet das Schreiben in die Datei
            Core.collectData(self, result_x1, result_y1, result_z1, result_mgfield, result_temp)

        except Exception as e:
            print("\n" + self.getCTime(), "something went wrong ERR: 1")
            print(e)
            print("\n")

    # Core-Funktion
    def MGFieldCore(self):
        # Planen des nächsten Durchlaufs
        threading.Timer(self.MES_TIME, Core.MGFieldCore, [self]).start()
        try:
            mgfield_values.append(self.inputMethod(self)[3])
            temp_values.append(dataHandler.getTemperature())
            x1_values.append(self.inputMethod(self)[0])
            y1_values.append(self.inputMethod(self)[1])
            z1_values.append(self.inputMethod(self)[2])
            # Überprüfen ob der Durchschnittswert berechnet werden muss
            if len(mgfield_values) == self.average:
                # Berechnen des Durchschnittswertes
                Core.calculateAverage(self, temp_values, x1_values, y1_values, z1_values, mgfield_values)
                temp_values.clear()
                mgfield_values.clear()
                x1_values.clear()
                y1_values.clear()
                z1_values.clear()

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
            if not (os.path.exists(os.getcwd() + "/logs")):
                os.mkdir(os.getcwd() + "/logs")
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
