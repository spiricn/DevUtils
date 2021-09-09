from du.afact.manifest.Types import Operation
import zipfile
from du.utils.ShellCommand import ShellCommand
from du.afact.manifest.Parser import Parser
import os
import logging
from collections import namedtuple
import pickle
import du.Utils as Utils

# Artifact meta, stored on disk to avoid unecessary installs
MetaEntry = namedtuple("MetaEntry", "timestamp, md5")

logger = logging.getLogger(__name__.split(".")[-1])


class Afact:
    # Name of the manifest when storing in an archive
    ARCHIVE_MANIFEST_FILENAME = "afact_manifest.py"

    # Name of the file where we're storing the artifact meta
    ARTIFACT_META_NAME = ".afact_meta"

    def __init__(self, manifestFilePath, rootDirectory):
        """
        @param manifestFilePath Manifest path
        @param rootDirectory Root directory all the paths in the manifest are relative to
        """

        self.__manifestFilePath = manifestFilePath
        self.__rootDirectory = rootDirectory

        # Open & parse manifest
        with open(self.__manifestFilePath, "r") as fileObj:
            self.__artifacts = Parser.parseString(fileObj.read(), self.__rootDirectory)

    def createArchive(self, archivePath):
        """
        Create a zip archive from the artifacts

        @param archivePath Archive target path
        """

        with zipfile.ZipFile(archivePath, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Write manifest at the root
            zipf.write(self.__manifestFilePath, arcname=self.ARCHIVE_MANIFEST_FILENAME)

            # Write all artifacts
            for artifact in self.__artifacts:
                logger.info(
                    "archiving {} ..".format(
                        os.path.basename(artifact.absoluteSourcePath)
                    )
                )
                zipf.write(
                    artifact.absoluteSourcePath, arcname=artifact.relativeSourcePath
                )

    def adbInstall(self, force=False, adbPath="adb", adbArgs=None):
        """
        Install artifacts on a target Android platform via ADB

        @param force Indication if all artifacts should be installed regardless if they're up to date or not
        @param adbPath ADB binary path
        @param adbArgs Additional ADB args
        """

        adbCommand = [adbPath]

        if adbArgs:
            adbCommand += adbArgs

        # Statistics
        numInstalled = 0
        numSkipped = 0

        # Meta map
        meta = {}

        # Attempt to load meta from file
        metaPath = os.path.join(self.__rootDirectory, self.ARTIFACT_META_NAME)
        try:
            with open(metaPath, "rb") as fileObj:
                meta = pickle.load(fileObj)
        except FileNotFoundError:
            pass

        for artifact in self.__artifacts:
            # Get file timestamp
            timestamp = int(os.stat(artifact.absoluteSourcePath).st_mtime)

            # Unique artifact key
            metaKey = artifact.relativeSourcePath

            # Check if we have info about this artifact
            metaEntry = meta.get(metaKey)

            # We need the MD5 calculated only if:
            # 1) we have no info about this artifact
            # 2) the timestamp changed (so we need to check if content changed as well)
            # 3) we're force installing
            if not metaEntry or metaEntry.timestamp != timestamp or force:
                logger.debug("calculate checksum ..")
                md5 = Utils.generateFileMd5sum(artifact.absoluteSourcePath)

            # We skip installing if timestamp or checksum is the same
            if not force and (
                metaEntry and (metaEntry.timestamp == timestamp or metaEntry.md5 == md5)
            ):
                # Update timestamp if it changed (but content is the same) so that we don't re-calculate MD5 on the consecutive executions
                if metaEntry.timestamp != timestamp:
                    meta[metaKey] = metaEntry._replace(timestamp=timestamp)

                numSkipped += 1
                continue

            logger.info(
                "install {} ( {} ) ..".format(
                    os.path.basename(artifact.absoluteSourcePath),
                    Utils.getHumanReadableSize(
                        os.path.getsize(artifact.absoluteSourcePath)
                    ),
                )
            )

            if artifact.operation == Operation.PUSH:
                # Remote target directory
                targetDir = os.path.dirname(artifact.target)

                # Directory exists ?
                cmd = ShellCommand.execute(
                    adbCommand
                    + [
                        "shell",
                        "if [ -d {} ]; then echo yes; else echo no; fi".format(
                            targetDir
                        ),
                    ]
                )

                if cmd.stdoutStr.rstrip() == "no":
                    # Create it
                    ShellCommand.execute(
                        adbCommand + ["shell", "mkdir", "-p", targetDir]
                    )

                # Push via ABD
                ShellCommand.execute(
                    adbCommand + ["push", artifact.absoluteSourcePath, artifact.target]
                )
            elif artifact.operation == Operation.INSTALL:
                ShellCommand.execute(
                    adbCommand + ["install", "-r", "-d", artifact.absoluteSourcePath]
                )
            else:
                raise RuntimeError("Unsupported operation")

            # Save new meta
            meta[metaKey] = MetaEntry(timestamp, md5)

            numInstalled += 1

        logger.info(
            "installed {}, skipped {}, total {}".format(
                numInstalled, numSkipped, len(self.__artifacts)
            )
        )

        # Dump meta
        with open(metaPath, "wb") as fileObj:
            pickle.dump(meta, fileObj)
