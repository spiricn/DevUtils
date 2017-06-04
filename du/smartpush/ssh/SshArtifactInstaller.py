import logging
import os

from du.ArtifactInstaller import ArtifactInstaller
from du.smartpush.ssh.Ssh import Ssh


TYPE_INVALID, \
TYPE_CUSTOM = range(2)

logger = logging.getLogger(__name__.split('.')[-1])

class SshArtifactInstaller(ArtifactInstaller):
    def __init__(self, artifacts, timestampFilePath, server, user):
        ArtifactInstaller.__init__(self, artifacts, timestampFilePath)

        self._ssh = Ssh(server, user)

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
        res = self._ssh.shell(['if [ -d %s ]; then echo 1; else echo 0; fi' % destDir])
        if res.rc != 0:
            raise RuntimeError(res.stderr)

        if int(res.stdout.rstrip()) == 0:
            logger.debug('creating directory: %r' % destDir)
            res = self._ssh.shell(['mkdir', '-p', destDir])
            if res.rc != 0:
                raise RuntimeError(res.stderr)

        self._ssh.push(source, dest)

        return True
