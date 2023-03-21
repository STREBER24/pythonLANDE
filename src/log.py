import tkinter.messagebox as popup
from config import Configuration
import time
import os
import io

TITLE = 'LANDE AutoInvest'

def getTimeString(config: Configuration):
    date = time.localtime()
    string = ''
    if config.newFileFrequency >= 1: string +=       str(date.tm_year).zfill(4)
    if config.newFileFrequency >= 2: string += '_' + str(date.tm_mon ).zfill(2)
    if config.newFileFrequency >= 3: string += '_' + str(date.tm_mday).zfill(2)
    return string

def ensureDir(file: str):
    dir = os.path.dirname(file)
    if not os.path.isdir(dir):
        os.mkdir(dir)
        i('created directory ' + dir)
          
def appendFile(config: Configuration, text: str):
    date = getTimeString(config)
    ensureDir(config.logFile % date)
    file = io.open(config.logFile % date, 'a', encoding='utf-8')
    file.write('\n%f %s' % (time.time(), text))
    file.close()
            
def v(config: Configuration, msg: str):
    text = '[VERBOSE] ' + msg
    if config.loggingLevelFile    >= 3: appendFile(config, text)
    if config.loggingLevelConsole >= 3: print(text)
    if config.loggingLevelPopup   >= 3: popup.showinfo(TITLE, msg)

def i(config: Configuration, msg: str):
    text = '[INFO]    ' + msg
    if config.loggingLevelFile    >= 2: appendFile(config, text)
    if config.loggingLevelConsole >= 2: print(text)
    if config.loggingLevelPopup   >= 2: popup.showinfo(TITLE, msg)

def w(config: Configuration, msg: str):
    text = '[WARNING] ' + msg
    if config.loggingLevelFile    >= 1: appendFile(config, text)
    if config.loggingLevelConsole >= 1: print(text)
    if config.loggingLevelPopup   >= 1: popup.showwarning(TITLE, msg)

def e(config: Configuration, msg: str):
    text = '[ERROR]   ' + msg
    if config.loggingLevelFile    >= 0: appendFile(config, text)
    if config.loggingLevelConsole >= 0: print(text)
    if config.loggingLevelPopup   >= 0: popup.showerror(TITLE, msg)

def pop(msg: str):
    popup.showinfo(TITLE, msg)

def confirm(msg: str):
    return popup.askquestion(TITLE, msg) == 'yes'
