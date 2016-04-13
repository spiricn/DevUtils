from du.ArtifactInstaller import ArtifactInstaller
from du.Utils import shellCommand
import filecmp
import logging
import os


TYPE_INVALID, \
TYPE_LIB, \
TYPE_BIN, \
TYPE_APK, \
TYPE_CUSTOM = range(5)

logger = logging.getLogger(__name__)

class AndroidArtifactInstaller(ArtifactInstaller):
    def __init__(self, artifacts, androidRoot, productName, timestampFilePath, adb='adb'):
        ArtifactInstaller.__init__(self, artifacts, timestampFilePath)

        self._androidRoot = androidRoot
        self._productName = productName
        self._symbols = True
        self._adb = adb

    def getFullArtifactPath(self, artifact):
        if artifact.type == TYPE_LIB:
            return self.getLibPath(artifact.source, self._symbols)

        elif artifact.type == TYPE_BIN:
            return self.getBinPath(artifact.source, self._symbols)

        elif artifact.type == TYPE_APK:
            return self.getAPKPath(artifact.source)

        elif artifact.type == TYPE_CUSTOM:
            return os.path.join(self.outDir, artifact.source)

        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def installArtifact(self, artifact):
        sourcePath = self.getFullArtifactPath(artifact)

        if artifact.type == TYPE_LIB:
            return self._push(sourcePath, '/system/lib/')
        elif artifact.type == TYPE_BIN:
            return self._push(sourcePath, '/system/bin/')
        elif artifact.type == TYPE_APK:
            return self._push(sourcePath, os.path.join('/system/app', os.path.splitext(artifact.source)[0] + "/"))
        elif artifact.type == TYPE_CUSTOM:
            return self._push(sourcePath, artifact.dest)
        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def artifactNeedsUpdate(self, artifact):
        sourcePath = self.getFullArtifactPath(artifact)

        tmpFile = os.popen('mktemp').read().rstrip()

        cmd = self._adb + ' pull ' + artifact.dest + ' ' + tmpFile

        cmdRes = shellCommand(cmd)

        if cmdRes.rc != 0:
            logger.error('Shell command %r failed: %d' % (cmd, cmdRes.rc))
            return False

        res = filecmp.cmp(sourcePath, tmpFile)

        os.remove(tmpFile)

        return res

    @property
    def appDir(self):
        return os.path.join(self.outDir, "system/app")

    @property
    def outDir(self):
        return os.path.join(self._androidRoot, 'out/target/product/' + self._productName)

    def getLibDir(self, symbols):
        return os.path.join(self.outDir, '%ssystem/lib' % ('symbols/' if symbols else ''))

    def getBinDir(self, symbols):
        return os.path.join(self.outDir, '%ssystem/bin' % ('symbols/' if symbols else ''))

    def getLibPath(self, name, symbols):
        return os.path.join(self.getLibDir(symbols), name)

    def getBinPath(self, name, symbols):
        return os.path.join(self.getBinDir(symbols), name)

    def getAPKPath(self, name):
        return os.path.join(self.appDir, os.path.splitext(name)[0], name)

    def _push(self, source, dest):
        cmd = self._adb + ' push %s %s' % (source, dest)
        logger.debug('Pushing: %r' % os.path.basename(source))

        cmdRes = shellCommand(cmd)

        return cmdRes.rc == 0
