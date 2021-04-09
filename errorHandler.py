from enum import Enum

logMsgDict = {
     999:"General error",
     1:"Fail to load image on the notebook"
 }

class LOGTYPE(Enum):
    ERROR_LOAD_IMG_NOTEBOOK = 1

def _logEnumGet(logType):
    return logMsgDict.get(logType,logMsgDict.get(0))

def printLog(logType,errorMsg=None):
    print("###############################################")
    print(logType)
    if not errorMsg == None:
        print("MESSAGE:")
        print(errorMsg)
        print("###############################################")
       