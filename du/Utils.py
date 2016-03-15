import os
import subprocess
from collections import namedtuple

CommandRes = namedtuple('CommandRes', 'stdout, stderr, rc')

def getFileTimestamp(path):
    return os.stat(path).st_mtime

def shellCommand(command):
    if isinstance(command, str):
        command = command.split(' ')

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    res = pipe.communicate()

    return CommandRes(res[0], res[1], pipe.returncode)

