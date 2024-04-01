#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 29-03-2024 16:56:55
# 
# file          | scripts/virtualSensor.py
# project       | MGFieldPy
# file version  | 1.0
#
from scripts.logHandler import logging
from scripts.hostinformationHandler import getFullHostname

import time
import os
import random     
import psutil   
import socket

class virtualSensor():     

    # Funktion für den Input aus einer virtuellen Umgebung (ohne Sensor --> aus Datei)
    def sensor():
        x1 = random.random()
        y1 = random.random()
        z1 = random.random()
        logging.writeDebugHigh("[MGField] got the following values: x=" + str(x1) + ", y=" + str(y1) + ", z=" + str(z1))
        time.sleep(0.2)

        return x1, y1, z1

    def temperatureSensor():
        # return zero 
        logging.writeDebugHigh("[Temperature] Accessing virtual temperature sensor")
        return 0.00
    
    # returns dict with values: cpu-speed, cpu-usage (%), total-ram, free-ram, used-ram, cached-ram, free-ram-with-cache (%), free-ram-wo-cache (%)
    def sysStatsSensor():
        total_memory, used_memory, free_memory, shared_memory, cached_memory, available_memory = map(int, os.popen('free -t -m').readlines()[1].split()[1:])
        free_withcache_percent = round((free_memory+cached_memory)/(total_memory/100), 2)
        free_withoutcache_percent = round(free_memory/(total_memory/100), 2)
        cpu_percent = psutil.cpu_percent()
        cpu_frequency = psutil.cpu_freq()
        sysSet = {
            "cpu_speed" : cpu_frequency.current,
            "cpu_usage" : cpu_percent,
            "ram_total" : total_memory,
            "ram_free" : free_memory,
            "ram_used" : used_memory,
            "ram_cached" : cached_memory,
            "ram_free_wcache_perc" : free_withcache_percent,
            "ram_free_wocache_perc" : free_withoutcache_percent
        }
        logging.writeDebug("[SysStats] got SysStats: CPU-Usage: " + str(cpu_percent) + "%, RAM-Usage: " + str(free_withcache_percent) + "%")
        return sysSet
    
    # returns dict with values:
    def netStatsSensor():
        netSet = {
            "hostname" : getFullHostname(),
            "local_IP" : socket.gethostbyname(socket.gethostname())
        }
        # further development here       
        return netSet
        
