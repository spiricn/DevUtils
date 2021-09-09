from du.manifest.Exceptions import *
from du.manifest.ManifestParser import ManifestParser
from du.afact.manifest.Types import *

from collections import namedtuple
import os

from enum import Enum


class ArtifactBuilder:
    """
    Artifact builder, methods are called from the manifest script (this the naming convention)
    """

    def __init__(self, relativeSourcePath):
        """
        @param relativeSourcePath Relative artifact source path
        """

        # Validate path
        self.__relativeSourcePath = relativeSourcePath
        if not isinstance(self.__relativeSourcePath, str):
            raise RuntimeError(
                "Expected string, got {}".format(type(self.__relativeSourcePath))
            )

        self.__target = None
        self.__operation = None

    def TARGET(self, target):
        """
        Set artifact target

        @param target Artifact target
        """

        if not isinstance(target, str):
            raise RuntimeError("Expected string, got {}".format(type(target)))

        self.__target = target
        self.__operation = Operation.PUSH

        return self

    def INSTALL(self):
        """
        Install an APK artifact
        """
        self.__operation = Operation.INSTALL

        return self

    def build(self, rootDirectory):
        """
        Build an artifact

        @param rootDirectory Root directory
        """

        if not self.__operation:
            raise RuntimeError("Operation not defined")

        # Must be relative
        if os.path.isabs(self.__relativeSourcePath):
            raise RuntimeError(
                "Source path not relative {}".format(self.__relativeSourcePath)
            )

        # Must be absolute
        absolutePath = os.path.abspath(
            os.path.normpath(os.path.join(rootDirectory, self.__relativeSourcePath))
        )

        # Does the artifact exist ?
        if not os.path.isfile(absolutePath):
            raise RuntimeError("Missing artifact {}".format(absolutePath))

        if isinstance(self.__target, str) and not os.path.isabs(self.__target):
            raise RuntimeError("Target path not absolute {}".format(self.__target))

        return Artifact(
            self.__relativeSourcePath, absolutePath, self.__operation, self.__target
        )


class Parser:
    @classmethod
    def parseString(cls, source, rootDirectory):
        """
        Parse string

        @param source Source string
        @param rootDirectory Afact root directory
        @return artifact list
        """

        # List of builders
        artifactBuilders = []

        # Helper function to create a builder
        def createBuilder(artifactBuilders, sourcePath):
            """
            Create a builder

            @param artifactBuilders List of builders
            @param sourcePath Source relative path
            """

            builder = ArtifactBuilder(sourcePath)
            artifactBuilders.append(builder)
            return builder

        manifestLocals = {
            "ADD_ARTIFACT": lambda sourcePath: createBuilder(
                artifactBuilders, sourcePath
            )
        }

        ManifestParser.executeString(source, manifestLocals)

        # Create artifacts
        return [builder.build(rootDirectory) for builder in artifactBuilders]
