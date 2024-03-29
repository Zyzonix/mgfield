#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY and ZyzonixDevelopments 
# -
# date      | 24/01/2022
# python-v  | 3.5.3
# -
# file      | venv.py
# project   | MGFieldPy
# project-v | 1.1
# 
import random        
import os                            
import mgfield

class inputFromFile():

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
        x1 = 0.1
        y1 = 0.2
        z1 = 0.3
        return x1,y1,z1,float(result)