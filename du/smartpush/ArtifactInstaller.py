from collections import namedtuple
import filecmp
import hashlib
import logging
import os
import pickle
import shutil
import tarfile

from du.Utils import getFileTimestamp, makeDirTree, getHumanReadableSize


STATUS_SKIPPED, \
STATUS_INSTALLED, \
STATUS_ERROR = range(3)

TYPE_INVALID, \
TYPE_LIB, \
TYPE_BIN, \
TYPE_APK, \
TYPE_CUSTOM = range(5)

class Artifact(object):
    def __init__(self, artifactType, source=None, destination=None, checkDifference=None, install=True, opts={}):
        self._type = artifactType
        self._source = source
        self._destination = destination
        self._checkDifference = checkDifference
        self._opts = opts
        self._install = install

    @property
    def type(self):
        return self._type

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @property
    def checkDifference(self):
        return self._checkDifference

    @property
    def install(self):
        return self._install

    @property
    def opts(self):
        return self._opts

InstallStatistics = namedtuple('InstallStatistics', 'numUpToDate, numInstalled, numErrors')

logger = logging.getLogger(__name__)

class ArtifactMeta:
    def __init__(self):
        self.timestamp = None
        self.cache = None

class ArtifactInstaller:
    def __init__(self, artifacts, workingDirectory='.du_artifact_installer'):
        self._workDir = workingDirectory
        self._metaFilePath = os.path.join(self._workDir, 'timestamps')
        self._cacheDir = os.path.join(self._workDir, 'cache')
        self._artifacts = artifacts

        makeDirTree(self._workDir)
        makeDirTree(self._cacheDir)

        self._loadMeta()

    def installArtifact(self, artifact):
        raise NotImplementedError('Not implemented')

    def install(self, force):
        if force:
            self._meta = {}


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

        self._saveMeta()

        return InstallStatistics(numUpToDate, numInstalled, numErrors)

    def createArchive(self, archivePath):
        out = tarfile.open(archivePath, mode='w')

        for artifact in self._artifacts:
            fullPath = self.getFullArtifactPath(artifact)

            archivePath = self.getArtifactArchivePath(artifact)

            logger.debug('Packing: %r -> %r' % (os.path.basename(fullPath), archivePath))

            out.add(fullPath, archivePath)

        out.close()

    def getArtifactArchivePath(self, artifact):
        raise NotImplementedError('Not implemented')

    def getFullArtifactPath(self, artifact):
        raise NotImplementedError('Not implemented')

    def artifactNeedsUpdate(self, artifact):
        raise NotImplementedError('Not implemented')

    def _loadMeta(self):
        try:
            with open(self._metaFilePath, 'rb') as fileObj:
                self._meta = pickle.load(fileObj)
        except:
            self._meta = {}

    def _saveMeta(self):
        with open(self._metaFilePath, 'wb') as fileObj:
            pickle.dump(self._meta, fileObj)

    def _isFileUpToDate(self, path):
        newTimestamp = getFileTimestamp(path)

        if path in self._meta:
            savedTimestamp = self._meta[path].timestamp

            if savedTimestamp != newTimestamp:
                # Check contents
                cachePath = self._getArtifactCachePath(path)

                if os.path.exists(cachePath):
                    return filecmp.cmp(cachePath, path)
                else:
                    return False
            else:
                return True
        else:
            return False

    def _encodePath(self, path):
        m = hashlib.md5()

        m.update(path.encode('utf-8'))

        return m.hexdigest()

    def _getArtifactCachePath(self, fullPath):
        return os.path.join(self._cacheDir, self._encodePath(fullPath))

    def _installArtifact(self, artifact):
        if not artifact.install:
            return STATUS_SKIPPED

        fullPath = self.getFullArtifactPath(artifact)
        if self._isFileUpToDate(fullPath):
            return STATUS_SKIPPED

        cachePath = self._getArtifactCachePath(fullPath)

        if not self._force and (artifact.checkDifference and self.artifactNeedsUpdate(artifact)):
            return STATUS_SKIPPED

        logger.debug('Installing %r ( %s )' % (os.path.basename(fullPath), getHumanReadableSize(os.path.getsize(fullPath))))
        if not self.installArtifact(artifact):
            return STATUS_ERROR

        if fullPath not in self._meta:
            meta = ArtifactMeta()
            self._meta[fullPath] = meta
        else:
            meta = self._meta[fullPath]

        meta.timestamp = getFileTimestamp(fullPath)

        # Copy to cache
        shutil.copy(fullPath, cachePath)

        return STATUS_INSTALLED
