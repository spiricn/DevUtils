from enum import Enum
from collections import namedtuple


class Operation:
    """
    Push artifact
    """

    PUSH = 1

    """
    Install APK artifact
    """
    INSTALL = 2


class Artifact(
    namedtuple("Artifact", "relativeSourcePath, absoluteSourcePath, operation, target")
):
    """
    Artifact information

    @param relativeSourcePath Relative path as defined by the manifest
    @param absoluteSourcePath Absolute source path on disk
    @param operation Artifact install operation
    @param target Installation target
    """
