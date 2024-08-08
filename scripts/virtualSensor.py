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
# project       | mgfield
# file version  | 2.0
#
from scripts.logHandler import logging
from scripts.hostinformationHandler import getFullHostname

import time
import random    

class virtualSensor():     

    # Funktion für den Input aus einer virtuellen Umgebung (ohne Sensor --> aus Datei)
    def sensor():
        x1 = random.random()
        y1 = random.random()
        z1 = random.random()
        out1 = random.random()
        logging.writeDebugHigh("[MGField] got the following values: x=" + str(x1) + ", y=" + str(y1) + ", z=" + str(z1) + ", out=" + str(out1))
        time.sleep(0.2)

        return x1, y1, z1, out1

    def temperatureSensor(self):
        # return zero 
        logging.writeDebugHigh("[Temperature] Accessing virtual temperature sensor")
        return 0.00

        
