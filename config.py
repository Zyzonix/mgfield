#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 29-03-2024 16:05:43
# 
# file          | config.py
# project       | MGFieldPy
# file version  | 1.0
#
VERSION = 2.3

# set intervall of measurements (in seconds)
measurementInterval = 0.5

# number of values after calculating average value 
# (measurementInterval*numberOfValuesToCollect = seconds after restart of collecting process)
numberOfValuesToCollect = 60

# when enabled data will be sourced from virtual sensor
useVirtualEnvironment = True

# dis- or enable debugging
debuggingEnabled = True

# set higher debug level when True (requires debuggingEnabled to be True)
higherDebugLevelEnabled = False

# interval for collecting sysstats
sysstatsCollectionInterval = 30

# temperature sensor en-/disabling switch
temperatureCollectionEnabled = True

# interval for collecting data from temperature sensor, if enabled (in seconds)
temperatureCollectionInterval = 120

# path to temperature sensor
temperatureSensorPath = ""

# store raw measurement data (x-,y-,z-values)
storeAllRawData = False

# mysql server ip/hostname
mysqlServerIP = ""

# mysql user
mysqlUsername = ""

# mysql user's password
mysqlPassword = ""

# mysql database name
mysqlDatabaseName = ""

# ip's to ping 
# vpn-server
target1 = ""
# sql-server
target2 = ""
# any server on the internet
target3 = ""