import logging
import os
import shutil

from du.ArtifactInstaller import ArtifactInstaller


TYPE_INVALID, \
TYPE_CUSTOM = range(2)

logger = logging.getLogger(__name__.split('.')[-1])

class FileArtifactInstaller(ArtifactInstaller):
    def __init__(self, artifacts, timestampFilePath):
        ArtifactInstaller.__init__(self, artifacts, timestampFilePath)

    def getFullArtifactPath(self, artifact):
        if artifact.type == TYPE_CUSTOM:
            return artifact.source
        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def getArtifactArchivePath(self, artifact):
        if artifact.type == TYPE_CUSTOM:
            return artifact.destination
        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def installArtifact(self, artifact):
        sourcePath = self.getFullArtifactPath(artifact)

        if artifact.type == TYPE_CUSTOM:
            return self._push(sourcePath, artifact.destination)
        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def _push(self, source, dest):
        logger.debug('Pushing: %r -> %r' % (os.path.basename(source), dest))

        destDir = os.path.dirname(dest)
        if not os.path.isdir(destDir):
            logger.debug('creating directory: %r' % destDir)
            os.makedirs(destDir)

        shutil.copy(source, dest)

        return True
