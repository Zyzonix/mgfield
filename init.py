#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by ZyzonixDevelopments 
# -
# date      | 26/04/2021
# python-v  | 3.5.3
# -
# file      | init.py
# project   | MGFieldPy
# project-v | 0.1
# 
from datetime import datetime
import sys
import threading
import time 
import itertools

# loading animation
def loadingAnimation():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        # checking if import is finished
        if loaded:
            # cancels for loop
            break
        sys.stdout.write('\r[' + str(datetime.now().strftime("%H:%M:%S")) + '] loading libraries ' + c)
        sys.stdout.flush()
        time.sleep(0.1)

# import finished indicator
loaded = False
print("\n[" + str(datetime.now().strftime("%H:%M:%S")) + "] running " + "\033[91m" + '\033[1m' +  "MGFieldPy" + '\033[0m' + "\n")
# starting loading animation
thread = threading.Thread(target=loadingAnimation)
thread.start()
# importing core
from mgfield import Core
loaded = True
# updating loaded-var in thread
thread.join()
print("\n")
# executing the core
Core()    
