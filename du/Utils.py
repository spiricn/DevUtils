import os

def getFileTimestamp(path):
    return os.stat(path).st_mtime