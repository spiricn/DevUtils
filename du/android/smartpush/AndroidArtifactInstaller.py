import os

from du.ArtifactInstaller import ArtifactInstaller


TYPE_INVALID, \
TYPE_LIB, \
TYPE_BIN, \
TYPE_APK, \
TYPE_CUSTOM = range(5)

class AndroidArtifactInstaller(ArtifactInstaller):
    def __init__(self, artifacts, androidRoot, productName, timestampFilePath):
        ArtifactInstaller.__init__(self, artifacts, timestampFilePath)

        self._androidRoot = androidRoot
        self._productName = productName

    def installArtifact(self, artifact):
        if artifact.type == TYPE_LIB:
            return self._push(self.getLibPath(artifact.source), '/system/lib/')
        elif artifact.type == TYPE_BIN:
            return self._push(self.getBinPath(artifact.source), '/system/bin/')
        elif artifact.type == TYPE_APK:
            return self._push(self.getAPKPath(artifact.source), os.path.join('/system/app', os.path.splitext(artifact.source)[0] + "/"))
        elif artifact.type == TYPE_CUSTOM:
            return self._push(os.path.join(self.outDir, artifact.source), artifact.dest)
        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

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
        cmd = 'adb push %s %s' % (source, dest)
        return os.system(cmd) == 0
