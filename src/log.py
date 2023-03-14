import os

def ensureDir(file: str):
      dir = os.path.dirname(file)
      if not os.path.isdir(dir):
            i('create directory ' + dir)
            os.mkdir(dir)
            
def v(msg: str):
    print(msg)

def i(msg: str):
    print(msg)

def w(msg: str):
    print(msg)

def e(msg: str):
    print(msg)