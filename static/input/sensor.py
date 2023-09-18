#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY and ZyzonixDevelopments 
# -
# date      | 24/01/2022
# python-v  | 3.5.3
# -
# file      | sensor.py
# project   | MGFieldPy
# project-v | 1.1
# 
from datetime import datetime
import board                                  
import busio                                       
import adafruit_ads1x15.ads1115 as ADS         
from adafruit_ads1x15.analog_in import AnalogIn 
import mgfield

class inputFromSensor():

    # Funktion für den Input vom Sensor
    def importDataFromSensor1(self):
        # Initialisiert die I2C-Schnittstelle
        i2c = busio.I2C(board.SCL, board.SDA)                          
        # creating the ADC object using the I2C bus located at 0x48 for fluxgate sensor 1
        # analog digital converter
        # Konfiguriert den Input vom I2C-Gerät mit der ID 0x48
        ads1 = ADS.ADS1115(i2c, address=0x48) 
        # creating input for x,y,z axis located at P0, P1, P2
        # Fragt die x,y,z-Werte ab
        x = AnalogIn(ads1, ADS.P0)
        y = AnalogIn(ads1, ADS.P1)
        z = AnalogIn(ads1, ADS.P2)
         
        # Formula for calculating the magnitude of the earth's magnetic field
        # Berechnung des Wertes
        result = (((x.value * x.value) + (y.value * y.value) + (z.value * z.value)) ** 0.5)         
        print(mgfield.Core.getCTime(self), "got", result, "as value [1]")
        return x.value,y.value,z.value,result
