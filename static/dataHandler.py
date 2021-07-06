#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY and ZyzonixDevelopments 
# -
# date      | 25/04/2021
# python-v  | 3.5.3
# -
# file      | static/dataHandler.py
# project   | MGFieldPy
# project-v | 0.2
# 
from datetime import datetime
import random
import psutil
import board    
import os                                   
import busio                                       
import adafruit_ads1x15.ads1115 as ADS         
from adafruit_ads1x15.analog_in import AnalogIn 
import mgfield

# Klasse für die Inputmöglichkeiten
class inputMethods():
    # Funktion für den Input aus einer virtuellen Umgebung (ohne Sensor --> aus Datei)
    def importDataFromFile(self):
        value_list = []
        input_file = open(os.getcwd() + "/static/data.txt", "r")
        for line in input_file:
            value_list.append(str(line))
        # Pickt eine zufällige Zahl aus dem Dokument
        result = value_list[random.randint(1, len(value_list) - 1)]
        result = result.rstrip(result[-1])
        result = result.rstrip(result[-1])
        print(mgfield.Core.getCTime(self), "got", result, "as value")
        return float(result)

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
        print(mgfield.Core.getCTime(self), "got", result, "as value")
        return result
    
    
    def importDataFromSensor2(self):
        # Initialisiert die I2C-Schnittstelle
        i2c = busio.I2C(board.SCL, board.SDA)                          
        # creating the ADC object using the I2C bus located at 0x48 for fluxgate sensor 2
        # analog digital converter
        # Konfiguriert den Input vom I2C-Gerät mit der ID 0x49
        ads2 = ADS.ADS1115(i2c, address=0x49) 
        # creating input for x,y,z axis located at P0, P1, P2
        # Fragt die x,y,z-Werte ab
        x = AnalogIn(ads2, ADS.P0)
        y = AnalogIn(ads2, ADS.P1)
        z = AnalogIn(ads2, ADS.P2)
         
        # Formula for calculating the magnitude of the earth's magnetic field
        # Berechnung des Wertes
        result = (((x.value * x.value) + (y.value * y.value) + (z.value * z.value)) ** 0.5)         
        print(mgfield.Core.getCTime(self), "got", result, "as value")
        return result

# Abfrage des noch zusätzlich angeschlossenen Temperatursensors (OneWire)
def getTemperature():
    # Öffnen der Datei für den Datensatz
    try:
        # unique ID for DS18B20 sensor
        sensor = open('/sys/bus/w1/devices/28-01193a114ec3/w1_slave')
        temp_raw = sensor.read()
        sensor.close()

        # Berechnung des Temperaturwertes
        temp_string = temp_raw.split("\n")[1].split(" ")[9]
        temp = float(temp_string[2:]) / 1000
        value = str('%6.2f' % temp)
    # Für den Fall, dass die Berechnung nicht möglich ist
    except:
        value = 1.00 
    return value

# Sammelt die aktuelle RAM-Auslastung
def getSystemStatistics():
    ram_percent = float(psutil.virtual_memory().percent)
    return ram_percent

# Sucht die aktuelle Inputmethode aus (wird durch die Config-Datei bestimmt)
def handleInputMethod(self):
    if self.input == 1:
        self.inputMethod = getattr(inputMethods, "importDataFromSensor1")
        self.inputMethod2 = getattr(inputMethods, "importDataFromSensor2")
    else:
        self.inputMethod = getattr(inputMethods, "importDataFromFile")
        self.inputMethod2 = getattr(inputMethods, "importDataFromFile")
