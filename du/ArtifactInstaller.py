from collections import namedtuple
from du.Utils import getFileTimestamp
import pickle


STATUS_SKIPPED, \
STATUS_INSTALLED, \
STATUS_ERROR = range(3)

Artifact = namedtuple('Artifact', 'type, source, dest, checkDifference')
Artifact.__new__.__defaults__ = (-1, None, None, False)

InstallStatistics = namedtuple('InstallStatistics', 'numUpToDate, numInstalled, numErrors')

class ArtifactInstaller:
    def __init__(self, artifacts, timestampFilePath):
        self._timestampFilePath = timestampFilePath
        self._artifacts = artifacts
        self._loadTimestamps()

    def installArtifact(self, artifact):
        raise NotImplementedError('Not implemented')

    def install(self, force):
        if force:
            self._timestamps = {}


        self._force = force
        numUpToDate = 0
        numInstalled = 0
        numErrors = 0

        for artifact in self._artifacts:
            status = self._installArtifact(artifact)

            if status == STATUS_SKIPPED:
                numUpToDate += 1

            elif status == STATUS_INSTALLED:
                numInstalled += 1

            elif status == STATUS_ERROR:
                numErrors += 1

            else:
                raise RuntimeError('Sanity check fail')

        self._saveTimestamps()

        return InstallStatistics(numUpToDate, numInstalled, numErrors)

    def getFullArtifactPath(self, artifact):
        raise NotImplementedError('Not implemented')

    def artifactNeedsUpdate(self, artifact):
        raise NotImplementedError('Not implemented')

    def _loadTimestamps(self):
        try:
            with open(self._timestampFilePath, 'rb') as fileObj:
                self._timestamps = pickle.load(fileObj)
        except:
            self._timestamps = {}

    def _saveTimestamps(self):
        with open(self._timestampFilePath, 'wb') as fileObj:
            pickle.dump(self._timestamps, fileObj)

    def _isFileUpToDate(self, path):
        newTimestamp = getFileTimestamp(path)

        if path in self._timestamps:
            savedTimestamp = self._timestamps[path]

            return savedTimestamp == newTimestamp

        else:
            return False

    def _installArtifact(self, artifact):
        fullPath = self.getFullArtifactPath(artifact)
        if self._isFileUpToDate(fullPath):
            return STATUS_SKIPPED

        if not self._force and (artifact.checkDifference and self.artifactNeedsUpdate(artifact)):
            return STATUS_SKIPPED

        if not self.installArtifact(artifact):
            return STATUS_ERROR

        self._timestamps[fullPath] = getFileTimestamp(fullPath)

        return STATUS_INSTALLED
