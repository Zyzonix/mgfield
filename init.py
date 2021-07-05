#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by OCISLY and ZyzonixDevelopments 
# -
# date      | 26/04/2021
# python-v  | 3.5.3
# -
# file      | init.py
# project   | MGFieldPy
# project-v | 0.2
# 
from datetime import datetime
import sys
import threading
import time 
import itertools

# Ladeanimation
def loadingAnimation():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        # Überprüfen ob MGFieldPy geladen ist
        if loaded:
            break
        sys.stdout.write('\r[' + str(datetime.now().strftime("%H:%M:%S")) + '] loading libraries ' + c)
        sys.stdout.flush()
        time.sleep(0.1)


loaded = False
print("\n[" + str(datetime.now().strftime("%H:%M:%S")) + "] running " + "\033[91m" + '\033[1m' +  "MGFieldPy" + '\033[0m' + "\n")

thread = threading.Thread(target=loadingAnimation)
thread.start()
print("started thread")
# Core importieren
from mgfield import Core
loaded = True
print("import complete")
thread.join()
print("\n")
# Starting MGFIeldPy
Core()    
