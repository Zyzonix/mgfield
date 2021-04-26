#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by ZyzonixDevelopments 
# -
# date      | 25/04/2021
# python-v  | 3.5.3
# -
# file      | static/xlsxHandler.py
# project   | MGFieldPy
# project-v | 0.1
# 
from datetime import date, datetime
import openpyxl

# preparing the xlsx-file
def prepareXLSXFile(self, sheetName):
    file = self.baseFilePath + str(date.today()) + "/" + str(date.today()) + "_" + datetime.now().strftime("%H-%M-%S") + ".xlsx"
    row = 1
    workBook = openpyxl.Workbook()
    workSheet = workBook.active
    # sheet name
    workSheet.title = sheetName
    # columnnames
    values = ["Date", "Time", "MGField Value", "Temperature", "Ram-Utilisation"]
    # inserting columnnames
    for column, item in enumerate(values, start=1):
        workSheet.cell(row, column, item)
    # writing all changes to file
    workBook.save(filename=file)
    # returning filename/path
    return file

# writing data to file
def writeToXLSXFile(self, data):
    # retrieving workbook, sheet and row
    workBook = openpyxl.load_workbook(self.xlsxFileData[0])
    workSheet = workBook[self.xlsxFileData[1]]
    currentRow = workBook.active.max_row + 1
    # inserting data per column
    for column, item in enumerate(data, start=1):
        workSheet.cell(currentRow, column, item)
    # saving changes
    workBook.save(filename=self.xlsxFileData[0])



