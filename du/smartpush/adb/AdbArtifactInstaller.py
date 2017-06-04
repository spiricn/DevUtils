import filecmp
import logging
import os

from du.ArtifactInstaller import ArtifactInstaller
from du.Utils import shellCommand


TYPE_INVALID, \
TYPE_LIB, \
TYPE_BIN, \
TYPE_APK, \
TYPE_CUSTOM = range(5)

APK_TYPE_KEY = 'type'
APK_TYPE_SYSTEM = 'system'
APK_TYPE_SYSTEM_PRIV = 'system-priv'
APK_TYPE_USER = 'user'

LIB_DEST_DIR = '/system/lib'
BIN_DEST_DIR = '/system/bin'
APP_DEST_DIR = '/system/app'
PRIV_APP_DEST_DIR = '/system/priv-app'

logger = logging.getLogger(__name__.split('.')[-1])

class AdbArtifactInstaller(ArtifactInstaller):
    def __init__(self, artifacts, androidRoot, productName, timestampFilePath, adb='adb'):
        ArtifactInstaller.__init__(self, artifacts, timestampFilePath)

        self._androidRoot = androidRoot
        self._productName = productName
        self._symbols = True
        self._adb = adb.split(' ') if adb else None

    def getFullArtifactPath(self, artifact):
        if artifact.type == TYPE_LIB:
            return self.getLibPath(artifact.source, self._symbols)

        elif artifact.type == TYPE_BIN:
            return self.getBinPath(artifact.source, self._symbols)

        elif artifact.type == TYPE_APK:
            apkType = artifact.opts[APK_TYPE_KEY]

            path = self.appDir if apkType in [APK_TYPE_SYSTEM, APK_TYPE_USER] else self.privAppDir

            return os.path.join(path, os.path.splitext(artifact.source)[0], artifact.source)

        elif artifact.type == TYPE_CUSTOM:
            return artifact.source

        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def getArtifactArchivePath(self, artifact):
        if artifact.type == TYPE_LIB:
            return os.path.join(LIB_DEST_DIR, artifact.source)

        elif artifact.type == TYPE_BIN:
            return os.path.join(BIN_DEST_DIR, artifact.source)

        elif artifact.type == TYPE_APK:
            apkType = artifact.opts[APK_TYPE_KEY]

            path = APP_DEST_DIR if apkType in [APK_TYPE_SYSTEM, APK_TYPE_USER] else PRIV_APP_DEST_DIR

            return os.path.join(path, artifact.source)

        elif artifact.type == TYPE_CUSTOM:
            return artifact.destination

        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def installArtifact(self, artifact):
        sourcePath = self.getFullArtifactPath(artifact)

        if artifact.type == TYPE_LIB:
            return self._push(sourcePath, '/system/lib/')
        elif artifact.type == TYPE_BIN:
            return self._push(sourcePath, '/system/bin/')
        elif artifact.type == TYPE_APK:
            if APK_TYPE_KEY not in artifact.opts:
                raise RuntimeError('APK type not specified')

            apkType = artifact.opts[APK_TYPE_KEY]

            if apkType in [APK_TYPE_SYSTEM, APK_TYPE_SYSTEM_PRIV]:
                path = APP_DEST_DIR if apkType in [APK_TYPE_SYSTEM, APK_TYPE_USER] else PRIV_APP_DEST_DIR

                return self._push(sourcePath, os.path.join(path, os.path.splitext(artifact.source)[0] + "/"))
            elif apkType == APK_TYPE_USER:
                logger.debug('Installing: %r' % os.path.basename(sourcePath))

                cmd = shellCommand(self._adb + ['install', '-r', sourcePath])
                if cmd.rc != 0:
                    logger.error('Error installing apk (%d): %s %s', cmd.rc, cmd.stdout, cmd.stderr)
                    return False
                return True
            else:
                raise RuntimeError('Invalid apk type %r' % apkType)

        elif artifact.type == TYPE_CUSTOM:
            return self._push(sourcePath, artifact.destination)
        else:
            raise RuntimeError('Unhandled artifact type %d' % artifact.type)

    def artifactNeedsUpdate(self, artifact):
        sourcePath = self.getFullArtifactPath(artifact)

        tmpFile = os.popen('mktemp').read().rstrip()

        cmd = self._adb + ['pull', artifact.destination, tmpFile]

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
    def privAppDir(self):
        return os.path.join(self.outDir, "system/priv-app")

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

    def isDeviceOnline(self):
        magic = 42

        cmd = shellCommand(self._adb + ['shell', 'echo %d' % magic])

        if cmd.rc != 0 or cmd.stdout.strip() != str(magic):
            logger.error('Device offline (%d): %s %s' % (cmd.rc, cmd.stdout, cmd.stderr))
            return False

        return True

    def _push(self, source, dest):
        if not self.isDeviceOnline():
            return False

        logger.debug('Pushing: %r' % os.path.basename(source))

        destDir = os.path.dirname(dest)

        cmd = shellCommand(self._adb + ['shell', 'if [ -d %s ]; then echo 1; else echo 0; fi' % destDir])
        if cmd.rc != 0:
            logger.error('Error checking directory (%d): %s' % (cmd.rc, cmd.stderr))
            return False
        elif cmd.stdout.strip() == '0':
            logger.debug('Creating directory %s' % destDir)

            cmd = shellCommand(self._adb + ['shell', 'mkdir', '-p', destDir])
            if cmd.rc != 0:
                logger.error('Error creating directory (%d): %s' % (cmd.rc, cmd.stdout))
                return False

        cmd = shellCommand(self._adb + ['push', source, dest])
        if cmd.rc != 0:
            logger.error('Error pushing file (%d): %s %s' % (cmd.rc, cmd.stdout, cmd.stderr))
            return False

        return True
