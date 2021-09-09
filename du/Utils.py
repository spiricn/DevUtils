from collections import namedtuple
import os
import subprocess
import tarfile
import hashlib


def makeDirTree(path):
    """
    Create directory tree if it doesn't exist

    @param path Directory path
    """

    if os.path.exists(path) and os.path.isdir(path):
        return

    os.makedirs(path)


def getHumanReadableSize(size, decimals=2):
    """
    Get human readable size

    @param size Size
    @param decimals Number of decimals to display
    @return human readable size string
    """

    units = (" bytes", "K", "M", "G", "T", "P")

    k = 1024
    size = float(size)
    unitIndex = 0

    while size >= k and unitIndex < len(units) - 1:
        size /= k
        unitIndex += 1

    # Conver the size into a string
    sizeStr = ("{:." + str(decimals) + "f}").format(size)

    # Check if all the decimals are zeros (e.g. 1.000)
    splitter = sizeStr.find(".")
    suffix = sizeStr[splitter + 1 :]

    if suffix == "0" * len(suffix):
        # Trim off the zeroes
        sizeStr = sizeStr[:splitter]

    return "{}{}".format(sizeStr, units[unitIndex])


def generateFileMd5sum(fielPath):
    """
    Generate MD5 hex digest from given file

    @param fielPath File path
    @return md5 checksum
    """

    md5 = hashlib.md5()
    with open(fielPath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)

    return md5.hexdigest()
