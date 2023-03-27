import tkinter.messagebox as popup
from config import Configuration
from plyer import notification
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

def ensureDir(config: Configuration, file: str):
    dir = os.path.dirname(file)
    if not os.path.isdir(dir):
        os.mkdir(dir)
        i(config, 'created directory ' + dir)
          
def appendFile(config: Configuration, text: str):
    date = getTimeString(config)
    ensureDir(config, config.logFile % date)
    file = io.open(config.logFile % date, 'a', encoding='utf-8')
    file.write('\n%f %s' % (time.time(), text))
    file.close()
            
def v(config: Configuration, msg: str):
    text = '[VERBOSE] %s' % msg
    if config.loggingLevelFile    >= 3: appendFile(config, text)
    if config.loggingLevelConsole >= 3: print(text)
    if config.loggingLevelPopup   >= 3: popup.showinfo(TITLE, msg)

def i(config: Configuration, msg: str):
    text = '[INFO]    %s' % msg
    if config.loggingLevelFile    >= 2: appendFile(config, text)
    if config.loggingLevelConsole >= 2: print(text)
    if config.loggingLevelPopup   >= 2: popup.showinfo(TITLE, msg)

def w(config: Configuration, msg: str):
    text = '[WARNING] %s' % msg
    if config.loggingLevelFile    >= 1: appendFile(config, text)
    if config.loggingLevelConsole >= 1: print(text)
    if config.loggingLevelPopup   >= 1: popup.showwarning(TITLE, msg)

def e(config: Configuration, msg: str):
    text = '[ERROR]   %s' % msg
    if config.loggingLevelFile    >= 0: appendFile(config, text)
    if config.loggingLevelConsole >= 0: print(text)
    if config.loggingLevelPopup   >= 0: popup.showerror(TITLE, msg)

def pop(config: Configuration, msg: str):
    if config.notification == 'plyer': 
        notification.notify(TITLE, msg, app_icon = None, timeout = 15)
    elif config.notification == 'tkinter':
        popup.showinfo(TITLE, msg)
    text = '[POPUP]   %s' % msg
    if config.loggingLevelFile    >= 2: appendFile(config, text)
    if config.loggingLevelConsole >= 2: print(text)

def confirm(config: Configuration, msg: str):
    result = popup.askquestion(TITLE, msg)
    text = '[POPUP]   %s <result=%s>' % (msg, result)
    if config.loggingLevelFile    >= 2: appendFile(config, text)
    if config.loggingLevelConsole >= 2: print(text)
    return result == 'yes'

if __name__ == '__main__':
    pop(Configuration(), 'Das ist ein Test.')