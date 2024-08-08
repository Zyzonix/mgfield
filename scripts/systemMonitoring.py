#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 06-08-2024 14:57:58
# 
# file          | scripts/systemMonitoring.py
# project       | mgfield
# file version  | 1.0.0
#
from scripts.logHandler import logging
from scripts.hostinformationHandler import getFullHostname

from ping3 import ping
import psutil
import socket
import os
import traceback

# function to get ping time 
def getConnectionDelay(target):
    result = 0
    try:
        # timeout set to 1s
        responseInS = ping(target, timeout = 1)
        responseInMs = round(responseInS*1000, 2)
        result = responseInMs
        logging.writeDebug("[NetStats] Connecting to " + str(target) + " took " + str(responseInMs) + "ms")
    
    except:
        logging.writeError("Failed to collect connection data for " + target)
        logging.writeExecError(traceback.format_exc())

    return result

class systemMonitoring():

    # complete monitoring of memory 
    def mem():
        memSet = {}
        total_memory, used_memory, free_memory, shared_memory, cached_memory, available_memory = map(int, os.popen('free -t -m').readlines()[1].split()[1:])
        free_withcache_percent = round((free_memory+cached_memory)/(total_memory/100), 2)
        free_withoutcache_percent = round(free_memory/(total_memory/100), 2)
        
        memSet = {
            "ram_total" : total_memory,
            "ram_free" : free_memory,
            "ram_used" : used_memory,
            "ram_cached" : cached_memory,
            "ram_free_wcache_perc" : free_withcache_percent,
            "ram_free_wocache_perc" : free_withoutcache_percent
        }

        return memSet

    # complete monitoring of CPU
    def cpu():
        cpuSet = {}
        cpu_percent = psutil.cpu_percent()
        cpu_frequency = psutil.cpu_freq()
        cpu_stats = psutil.cpu_stats()
        
        cpuSet = {
            "cpu_speed" : cpu_frequency.current,
            "cpu_usage" : cpu_percent,
            "cpu_ctx_switches" : cpu_stats.ctx_switches,
            "cpu_interrupts" : cpu_stats.interrupts,
            "cpu_soft_interrupts" : cpu_stats.soft_interrupts
        }

        return cpuSet

    
    # complete network monitoring (targets = dict with targetname : ip/hostname)
    def net(targets):
        netSet = {}
        target1result = "0"
        target2result = "0"
        target3result = "0"
        if targets["target1"]: target1result = getConnectionDelay(targets["target1"])
        if targets["target2"]: target2result = getConnectionDelay(targets["target2"]) 
        if targets["target3"]: target3result = getConnectionDelay(targets["target3"]) 
        netStats = psutil.net_io_counters()
        netSet = {
            "hostname" : getFullHostname(),
            "local_IP" : socket.gethostbyname(socket.gethostname()),
            "packets_sent" : netStats.packets_sent,
            "packets_recv" : netStats.packets_recv,
            "errin" : netStats.errin,
            "errout" : netStats.errout,
            "dropin" : netStats.dropin,
            "dropout" : netStats.dropout,
            "target1" : target1result,
            "target2" : target2result,
            "target3" : target3result
        }

        return netSet
    
    # complete monitoring of all sensors available on the device
    def internalTemperatureSensors():
        intTempSet = {}
        try: 
            intTempSensors = psutil.sensors_temperatures()
            currentCPUTemp = intTempSensors["cpu_thermal"][0][1]
        except: 
            currentCPUTemp = 0
        intTempSet = {
            "cpu_thermal" : str(currentCPUTemp)
        }

        return intTempSet