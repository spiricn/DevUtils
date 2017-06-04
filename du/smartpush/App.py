import argparse
import logging
import sys
import traceback

from du.smartpush.ArtifactManifest import ArtifactManifest
from du.smartpush.file.FileSmartPushApp import FileSmartPushApp


logger = logging.getLogger(__name__)


def main():
    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    if len(sys.argv) < 2:
        logger.error('Protocol not provided')
        return -1

    protocol = sys.argv[1]
    sys.argv.pop(1)


    protocolMap = {
        'file' : FileSmartPushApp
    }

    if protocol not in protocolMap:
        logger.error('Unsupported protocol %r, available=%s' % (protocol, protocolMap.keys()))
        return -1;

    app = protocolMap[protocol]()

    parser = argparse.ArgumentParser()

    parser.add_argument('manifest')
    parser.add_argument('-timestamps')
    parser.add_argument('-force', action='store_true')

    app.createArgParser(parser)

    args = parser.parse_args()

    manifest = ArtifactManifest(args.manifest)
    try:
        artifacts = manifest.parse({})
    except Exception as e:
        logger.error('Error getting artifacts: %r' % str(e))
        return -1

    timestampFile = '.smart-push-timestamps'
    if args.timestamps:
        timestampFile = args.timestamps

    try:
        res = app.execute(args, artifacts, timestampFile, args.force)
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

