#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 29-03-2024 15:08:27
# 
# file          | scripts/mysqlHandler.py
# project       | MGFieldPy
# file version  | 1.0
#
import mysql.connector
import traceback

# custom scripts
import config
from scripts.logHandler import logging


mysqlTableTemplates = {
    "mgfield" : "`mgfield`(`time`, `avg_result`, `time_delta`) ",
    "mgfieldraw" : "`mgfieldraw`(`time`, `x_value`, `y_value`, `z_value`, `measurement_result`, `measurement_duration`) ",
    "netstats" : "`netstats`(`time`, `hostname`, `local_ip`) ",
    "sysstats" : "`sysstats`(`time`, `cpu_speed`, `cpu_usage`, `ram_total`, `ram_free`, `ram_used`, `ram_cached`, `ram_free_wcache_perc`, `ram_free_wocache_perc`) ",
    "temperature" : "`temperature`(`time`, `temperature_value`) "
}

# connection handler
class mySQLHandler():

    # create db connection
    def openConnection():
        
        try:
            # try creating a connection
            serverConnection = mysql.connector.connect(
                host = config.mysqlServerIP,
                user = config.mysqlUsername,
                password = config.mysqlPassword,
                database = config.mysqlDatabaseName
            )

        except:
            logging.writeExecError(traceback.format_exc())
            return False

        if serverConnection.is_connected(): return serverConnection
        else: return False

    # format timestamp to make it readable for grafana
    # required final format e.g. 2023-12-03 12:44:02
    def formatDate(date):
        dateSplit = date.split("_")
        formattedDate = dateSplit[0]
        formattedTime = dateSplit[1].replace("-", ":")
        if "." in formattedTime: formattedTime = formattedTime.split(".")[0]
        formattedTimestamp = formattedDate + " " + formattedTime
        return formattedTimestamp

    # leave microseconds at the end
    def formatDateLong(date):
        dateSplit = date.split("_")
        formattedDate = dateSplit[0]
        formattedTime = dateSplit[1].replace("-", ":")
        formattedTimestamp = formattedDate + " " + formattedTime
        return formattedTimestamp
    
    # build mySQL insert command
    def commandBuilder(table, time, dataString):
        insertInto = "INSERT INTO "
        values = "VALUES "
        valueBegin = "('"
        valueSeparator = "','"
        valueEnd = "')"
        valueContent = time + valueSeparator + dataString.replace("__", valueSeparator)
        sqlCommand = insertInto + mysqlTableTemplates[table] + values + valueBegin + valueContent + valueEnd
        
        logging.writeDebugHigh("Build SQL command for " + str(time) + " and table: " + table + " successfully")
        return sqlCommand
