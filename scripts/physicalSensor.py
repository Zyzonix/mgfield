#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 29-03-2024 16:56:44
# 
# file          | scripts/physicalSensor.py
# project       | MGFieldPy
# file version  | 1.0
#
from scripts.logHandler import logging
import config

class physicalSensor():
    from datetime import datetime
    import board                                  
    import busio                                       
    import adafruit_ads1x15.ads1115 as ADS         
    from adafruit_ads1x15.analog_in import AnalogIn 

    # Funktion für den Input vom Sensor
    def sensor():
        # Initialisiert die I2C-Schnittstelle
        i2c = physicalSensor.busio.I2C(physicalSensor.board.SCL, physicalSensor.board.SDA)                          
        # creating the ADC object using the I2C bus located at 0x48 for fluxgate sensor 1
        # analog digital converter
        # configures the input from the I2C device that has the ID 0x48
        ads1 = physicalSensor.ADS.ADS1115(i2c, address=0x48) 
        # creating input for x,y,z axis located at P0, P1, P2
        # requests the values x, y, z
        x = physicalSensor.AnalogIn(ads1, physicalSensor.ADS.P0)
        y = physicalSensor.AnalogIn(ads1, physicalSensor.ADS.P1)
        z = physicalSensor.AnalogIn(ads1, physicalSensor.ADS.P2)
        out = physicalSensor.AnalogIn(ads1, physicalSensor.ADS.P3)
        logging.writeDebugHigh("[MGField] got the following values: x=" + str(x.value) + ", y=" + str(y.value) + ", z=" + str(z.value) + ", out=" + str(out.value))

        return float(x.value), float(y.value), float(z.value), float(out.value)

    def temperatureSensor():
        # open data
        try:
            # unique ID for DS18B20 sensor
            sensor = open(config.temperatureSensorPath)
            temp_raw = sensor.read()
            sensor.close()

            # calculate temperature
            temp_string = temp_raw.split("\n")[1].split(" ")[9]
            temp = float(temp_string[2:]) / 1000
            value = str('%6.2f' % temp)
            logging.writeDebug("[Temperature] got " + str(value) + " from sensor")
        
        # if temperature sensor cannot be accessed
        except:
            value = 0.00 
            logging.writeDebug("Failed to access temperature sensor")
        return value
