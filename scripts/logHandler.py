#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 16-02-2024 11:34:01
# 
# file          | scripts/logHandler.py
# project       | MGFieldPy
# file version  | 1.0
#
from datetime import datetime

# import custom scripts
import config

# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"))
        return curTime
    
    def getTimeLong():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"))
        return curTime


class logging():
    
    # import custom scripts
    # log file handling will be managed with systemd
    LOGGING_ENABLED = False

    def toFile(msg):
        if logging.LOGGING_ENABLED:
            try:
                logFile = open(logging.LOGFILEDIR + logging.LOGFILENAME, "a")
                logFile.write(msg + "\n")
                logFile.close()
            except:
                logging.LOGGING_ENABLED = False
                logging.writeError("Failed to open logfile directory, maybe a permission error?")

    def write(msg):
        message = str(ctime.getTime() + " INFO   | " + str(msg))
        print(message)
        logging.toFile(message)

    def writeError(msg):
        message = str(ctime.getTime() + " ERROR  | " + msg)
        print(message)
        logging.toFile(message)

    def writeDebug(msg):
        if config.debuggingEnabled:
            message = str(ctime.getTime() + " DEBUG  | " + msg)
            print(message)
            logging.toFile(message)

    def writeDebugHigh(msg):
        if config.higherDebugLevelEnabled and config.debuggingEnabled:
            message = str(ctime.getTime() + " DEBUG  | " + msg)
            print(message)
            logging.toFile(message)

    # log/print error stack trace
    def writeExecError(msg):
        message = str(msg)
        print(message)
        logging.toFile(message)


    
    def writeNix(self):
        logging.toFile(self, "")
        print()
