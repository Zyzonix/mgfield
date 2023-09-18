#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY and ZyzonixDevelopments
# -
# date      | 24/01/2022
# python-v  | 3.5.3
# -
# file      | static/csvHandler.py
# project   | MGFieldPy
# project-v | 1.1
# 
import csv

# Vorbereiten der Excel-Datei
def prepareCSVFile(filePath, fileName):
    # öffnen der Datei
    csvFile = open(filePath, mode="w")
    # Variable für die Spaltenbezeichnung (Zeile 1)
    values = ["Date","Time","x1","y1","z1","MGField Value1","x2","y2","z2", "Temperature", "RAM-Available %"]
    # Initialisiert den Csv-Schreiber
    csvWriter = csv.writer(csvFile, dialect=csv.excel)
    # Schreibt die vorher behannten Bezeichnungen in die erste Zeile
    csvWriter.writerow(values)
    # Sauberes Schließen der Datei
    csvFile.close()
    # Dateiname als self.-Variable gesichert
    return fileName

# Schreiben von Daten in die Datei
def writeToCSVFile(self, data):
    # öffnen der Datei
    csvFile = open(self.fileData[2], mode="a")
    # Initialisiert den Csv-Schreiber
    csvWriter = csv.writer(csvFile, dialect=csv.excel)
    # Schreibt die Daten in die nächste Zeile
    csvWriter.writerow(data)
    # Sauberes Schließen der Datei
    csvFile.close()
