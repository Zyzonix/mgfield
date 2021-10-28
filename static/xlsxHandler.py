#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY and ZyzonixDevelopments
# -
# date      | 25/04/2021
# python-v  | 3.5.3
# -
# file      | static/xlsxHandler.py
# project   | MGFieldPy
# project-v | 0.2
# 
from datetime import date, datetime
import openpyxl

# Vorbereiten der Excel-Datei
def prepareXLSXFile(self, sheetName):
    # Setzt den Dateipfad
    file = self.baseFilePath + str(date.today()) + "/" + str(date.today()) + "_" + datetime.now().strftime("%H-%M-%S") + ".xlsx"
    row = 1
    # Initialisiert die notwendige Bibliothek zum schreiben/lesen von Excel-Dateien
    workBook = openpyxl.Workbook()
    # Aktiviert die zu bearbeitende Tabelle
    workSheet = workBook.active
    # Setzt den Tabellennamen
    workSheet.title = sheetName
    # Variable für die Spaltenbezeichnung (Zeile 1)
    values = ["Date", "Time", "MGField Value1","MGField Value2", "Temperature", "Ram-Available"]
    # Schreibt die vorher behannten Bezeichnungen in die erste Zeile
    for column, item in enumerate(values, start=1):
        workSheet.cell(row, column, item)
    # Speichert die Datei
    workBook.save(filename=file)
    # Gibt den Dateinamen für zukünftige Schreibzyklen zurück
    return file

# Schreiben von Daten in die Datei
def writeToXLSXFile(self, data):
    # Öffnen der Datei und aktivieren der Tabelle
    workBook = openpyxl.load_workbook(self.xlsxFileData[0])
    workSheet = workBook[self.xlsxFileData[1]]
    currentRow = workBook.active.max_row + 1
    # Schreibt Daten in die Zeile
    for column, item in enumerate(data, start=1):
        workSheet.cell(currentRow, column, item)
    # Speichert die Datei
    workBook.save(filename=self.xlsxFileData[0])
