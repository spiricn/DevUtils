from collections import namedtuple
import os
import subprocess
import tarfile


CommandRes = namedtuple('CommandRes', 'stdout, stderr, rc, strStdout, strStderr')

def getFileTimestamp(path):
    return os.stat(path).st_mtime

def shellCommand(command):
    if isinstance(command, str):
        command = command.split(' ')

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    res = pipe.communicate()

    return CommandRes(res[0], res[1], pipe.returncode, str(res[0], 'UTF-8'), str(res[1], 'UTF-8'))

def makeDirTree(path):
    if os.path.exists(path) and os.path.isdir(path):
        return

    os.makedirs(path)

def archiveDirectory(archivePath, dirPath):
    t = tarfile.open(archivePath, mode='w')

    t.add(dirPath, arcname=os.path.basename(dirPath))
    t.close()

def getHumanReadableSize(size):
    KB = 1024
    MB = KB * KB
    GB = MB * MB

    if size < KB:
        return '%d B' % size
    elif size >= KB and size < MB:
        return '%.2f KB' % (size / KB)
    elif size >= MB and size < GB:
        return '%.2f MB' % (size / MB)
    else:
        return '%.2f GB' % (size / GB)
