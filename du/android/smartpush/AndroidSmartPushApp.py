import argparse
from du.android.smartpush.AndroidArtifactInstaller import AndroidArtifactInstaller
import logging
import sys
import traceback
from utils.Git import Change

logger = logging.getLogger(__name__)

class Manifest:
    GET_ARTIFACTS_FNC_NAME = 'getArtifacts'

    def __init__(self, path):
        self._path = path

    def getArtifacts(self):
        env = {}

        with open(self._path, 'rb') as fileObj:
            exec(fileObj.read(), env)

            if self.GET_ARTIFACTS_FNC_NAME not in env:
                raise RuntimeError('Function %r not found in %r' % (self.GET_ARTIFACTS_FNC_NAME, self._path))

            return env[self.GET_ARTIFACTS_FNC_NAME]()

def main():
    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    parser = argparse.ArgumentParser()

    parser.add_argument('android_root')
    parser.add_argument('product_name')
    parser.add_argument('manifest')
    parser.add_argument('-adb')
    parser.add_argument('-timestamps')
    parser.add_argument('-force', action='store_true')

    args = parser.parse_args()

    manifest = Manifest(args.manifest)
    try:
        artifacts = manifest.getArtifacts()
    except Exception as e:
        logger.error('Error getting artifacts: %r' % str(e))
        return -1

    adb = 'adb'
    if args.adb:
        adb = args.adb

    timestampFile = '.android-smart-push-timestamps'
    if args.timestamps:
        timestampFile = args.timestamps

    ai = AndroidArtifactInstaller(artifacts, args.android_root, args.product_name, timestampFile, adb)

    force = False
    if args.force:
        force = args.force

    try:
        res = ai.install(force)
    except Exception as e:
        logger.error('Error installing artifacts: %s' % str(e))
        logger.error(traceback.format_exc())
        return -1

    logger.debug('#' * 40)

    if res.numInstalled:
        logger.debug('Installed: %d' % res.numInstalled)

    if res.numUpToDate:
        logger.debug('Skipped: %d' % res.numUpToDate)

    if res.numErrors:
        logger.error('Errors: %d' % res.numErrors)

    if res.numErrors:
        return -1

    return 0

if __name__ == '__main__':
    sys.exit(main())

