from collections import namedtuple
import pickle

from du.Utils import getFileTimestamp

STATUS_SKIPPED, \
STATUS_INSTALLED, \
STATUS_ERROR = range(3)

Artifact = namedtuple('Artifact', 'type, source, dest')
Artifact.__new__.__defaults__ = (-1, None, None)

class ArtifactInstaller:
    def __init__(self, artifacts, timestampFilePath):
        self._timestampFilePath = timestampFilePath
        self._artifacts = artifacts

    def installArtifact(self, artifact):
        raise NotImplementedError('Not implemented')

    def install(self, force):
        if force:
            self._timestamps = {}

        numUpToDate = 0
        numPushed = 0
        numErrors = 0

        for artifact in self._artifacts:
            status = self._installArtifact(artifact)

            if status == STATUS_SKIPPED:
                numUpToDate += 1

            elif status == STATUS_INSTALLED:
                numPushed += 1

            elif status == STATUS_ERROR:
                numErrors += 1

            else:
                raise RuntimeError('Sanity check fail')

        self._saveTimestamps()

    def _loadTimestamps(self):
        try:
            with open(self.timestampFilePath, 'rb') as fileObj:
                self._timestamps = pickle.load(fileObj)
        except:
            self._timestamps = {}

    def _saveTimestamps(self):
        with open(self.timestampFilePath, 'wb') as fileObj:
            pickle.dump(self._timestamps, fileObj)


    def _isFileUpToDate(self, path):
        newTimestamp = getFileTimestamp(path)

        if path in self._timestamps:
            savedTimestamp = self._timestamps[path]

            return savedTimestamp == newTimestamp

        else:
            return False

    def _installArtifact(self, artifact):
        if self._isFileUpToDate(artifact.source):
            return STATUS_SKIPPED

        if not self.installArtifact(artifact):
            return STATUS_ERROR

        self._timestamps[artifact.source] = getFileTimestamp(artifact.source)

        return STATUS_INSTALLED
