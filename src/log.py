import config
import time
import os
import io

def getDateString():
      date = time.localtime()
      return str(date.tm_year).zfill(4) + '_' + str(date.tm_mon).zfill(2) + '_' + str(date.tm_mday).zfill(2)

def ensureDir(file: str):
      dir = os.path.dirname(file)
      if not os.path.isdir(dir):
            os.mkdir(dir)
            i('created directory ' + dir)
          
def appendFile(text: str):
    date = getDateString()
    ensureDir(config.logFile % date)
    file = io.open(config.logFile % date, 'a', encoding='utf-8')
    file.write('\n%f %s' % (time.time(), text))
    file.close()
            
def v(msg: str):
    text = '[VERBOSE] ' + msg
    if config.loggingLevelFile    >= 3: appendFile(text)
    if config.loggingLevelConsole >= 3: print(text)

def i(msg: str):
    text = '[INFO]    ' + msg
    if config.loggingLevelFile    >= 2: appendFile(text)
    if config.loggingLevelConsole >= 2: print(text)

def w(msg: str):
    text = '[WARNING] ' + msg
    if config.loggingLevelFile    >= 1: appendFile(text)
    if config.loggingLevelConsole >= 1: print(text)

def e(msg: str):
    text = '[ERROR]   ' + msg
    if config.loggingLevelFile    >= 0: appendFile(text)
    if config.loggingLevelConsole >= 0: print(text)