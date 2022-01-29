#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY-ds and ZyzonixDevelopments 
# -
# date      | 25/04/2021
# python-v  | 3.5.3
# -
# file      | static/dataHandler.py
# project   | MGFieldPy
# project-v | 1.1
# 
from datetime import datetime, date
import psutil
import os                                   
import mgfield
from static import xlsxHandler
from static import csvHandler

# preparing environment + required files
def performSetup(self):
    print(mgfield.Core.getCTime(self), "performing environment setup")
    # Erstellt ggf. den "output"-Ordner
    if not os.path.exists(self.baseFilePath):
        os.mkdir(self.baseFilePath)
    
    # Erstellt einen Ordner mit dem aktuellen Datum
    if not os.path.exists(self.baseFilePath + "/" + str(date.today()) +"/"):
        os.mkdir(self.baseFilePath+ "/" + str(date.today()) +"/")
        
    self.baseFilePath = self.baseFilePath + "/" + str(date.today()) +"/"
    
    # Name der Datei und Tabelle
    fileName = str(date.today()) + "_" + str(datetime.now().strftime("%H-%M-%S"))
    self.sheetName = str(date.today())
    filePath = self.baseFilePath + "/" + fileName

    # Output --> CSV
    if self.output == 0:
        # Hinzufügen der Dateiendung
        fileName += ".csv"
        filePath += ".csv"
        # Initialisiert die CSV-Datei
        self.fileName = csvHandler.prepareCSVFile(filePath, fileName)        
        # Speichert den Pfad zur CSV-Datei global (sheetName unused)
        self.fileData = [self.fileName, self.sheetName, filePath]

    # Output --> XLSX
    elif self.output == 1:
        # Zeilen-Indikator für die Excel-Tabelle
        self.xlsxRow = 1
        # Hinzufügen der Dateiendung
        fileName += ".xlsx"
        filePath += ".xlsx"
        # Initialisiert die Excel-Datei
        self.fileName = xlsxHandler.prepareXLSXFile(filePath, self.sheetName, fileName)
        # Speichert den Pfad zur Excel-Datei global
        self.fileData = [self.fileName, self.sheetName, filePath]

    else:
        print(mgfield.Core.getCTime(self), "something when wrong, please check the config [input method not found]")    
        exit()


# Abfrage des noch zusätzlich angeschlossenen Temperatursensors (OneWire)
def getTemperature():
    # Öffnen der Datei für den Datensatz
    try:
        # unique ID for DS18B20 sensor
        sensor = open('/sys/bus/w1/devices/28-01204b515089/w1_slave')
        temp_raw = sensor.read()
        sensor.close()

        # Berechnung des Temperaturwertes
        temp_string = temp_raw.split("\n")[1].split(" ")[9]
        temp = float(temp_string[2:]) / 1000
        value = str('%6.2f' % temp)
    # Für den Fall, dass die Berechnung nicht möglich ist
    except:
        value = 1.00 
    return value

# Sammelt die aktuelle RAM-Auslastung
def getSystemStatistics():
    ram_available = float(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
    return ram_available

# Sucht die aktuelle Inputmethode aus (wird durch die Config-Datei bestimmt)
def handleInputMethod(self):
    if self.input == 1:
        from static.input.sensor import inputFromSensor
        self.inputMethod = getattr(inputFromSensor, "importDataFromSensor1")
        self.inputMethod2 = getattr(inputFromSensor, "importDataFromSensor2")
    else:
        from static.input.venv import inputFromFile
        self.inputMethod = getattr(inputFromFile, "importDataFromFile")
        self.inputMethod2 = getattr(inputFromFile, "importDataFromFile")
