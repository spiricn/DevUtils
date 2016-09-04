import argparse
import logging
import sys
import traceback

from du.android.smartpush.AndroidArtifactInstaller import AndroidArtifactInstaller
from du.android.smartpush.ArtifactManifest import ArtifactManifest


logger = logging.getLogger(__name__)

def main():
    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    parser = argparse.ArgumentParser()

    parser.add_argument('android_root')
    parser.add_argument('product_name')
    parser.add_argument('manifest')
    parser.add_argument('archive_path')

    args = parser.parse_args()

    manifest = ArtifactManifest(args.manifest)
    try:
        artifacts = manifest.parse()
    except Exception as e:
        logger.error('Error getting artifacts: %r' % str(e))
        return -1

    timestampFile = '.android-smart-push-timestamps'

    ai = AndroidArtifactInstaller(artifacts, args.android_root, args.product_name, timestampFile, None)

    try:
        ai.createArchive(args.archive_path)
    except Exception as e:
        logger.error('Error creating archive: %s' % str(e))
        logger.error(traceback.format_exc())
        return -1

    logger.debug('Archive created: %r' % args.archive_path)

    return 0

if __name__ == '__main__':
    sys.exit(main())

