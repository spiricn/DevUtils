import argparse
import logging
import sys

from du.android.smartpush.AndroidArtifactInstaller import AndroidArtifactInstaller

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
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('android_root')
    parser.add_argument('product_name')
    parser.add_argument('manifests', nargs='+')
    parser.add_argument('-force', action='store_true')

    args = parser.parse_args()

    artifacts = []
    for manifestFile in args.manifests:
        manifest = Manifest(manifestFile)

        try:
            artifacts += manifest.getArtifacts()
        except Exception as e:
            logger.error('Error getting artifacts: %r' % str(e))
            return -1

    logger.debug('Loaded %d artifacts from %d files' % (len(artifacts), len(args.manifests)))

    ai = AndroidArtifactInstaller(artifacts, args.android_root, args.product_name, '.android-smart-push-timestamps')

    try:
        ai.install(False)
    except Exception as e:
        logger.error('Error installing artifacts: %s' % str(e))
        return -1

    return 0

if __name__ == '__main__':
    sys.exit(main())

