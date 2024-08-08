#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 16-02-2024 11:35:08
# 
# file          | scripts/hostinformationHandler.py
# project       | mgfield
# file version  | 1.0
#
import platform
import subprocess
import traceback

from scripts.logHandler import logging

# scheme
#hostname = "unknown"
# fullHostname = "unknown.localdomain"

# get hostname with local dns-suffix
def getFullHostname():
    fullHostname = "unknown"
    try:

        # request dns suffix
        resultEncoded = subprocess.run("/usr/bin/hostname -A", capture_output=True, shell=True)
        result = resultEncoded.stdout.decode()[:-1]
        resultErr = resultEncoded.stderr.decode()[:-1]
        if resultErr:
            logging.writeError("Failed to get DNS suffix (command exited with error)")
        else:
            # in case of 'hostname hostname' --> only one time hostname
            if str(platform.node() + " ") in result:
                logging.write("Correcting retrieved hostname from " + result + " to " + platform.node())
                fullHostname = platform.node()
            else: fullHostname = result

            if fullHostname[len(fullHostname) - 1] == " ":
                fullHostname = fullHostname[:-1]
    except:
        logging.writeError("Failed to get full hostname")
        logging.writeExecError(traceback.format_exc())

    return fullHostname

# get raw hostname
def getHostname():
    hostname = "unknown"
    try: hostname = platform.node()
    except: logging.writeError("Failed to get hostname")
    return hostname