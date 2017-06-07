import argparse
import logging
import sys
import traceback

from du.smartpush.ArtifactManifest import ArtifactManifest
from du.smartpush.adb.AdbSmartPushApp import AdbSmartPushApp
from du.smartpush.file.FileSmartPushApp import FileSmartPushApp
from du.smartpush.ssh.SshSmartPushApp import SshSmartPushApp


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


    protocolApps = [
        FileSmartPushApp,
        SshSmartPushApp,
        AdbSmartPushApp
    ]
    protocolMap = { cls.getProtocolName() : cls for cls in protocolApps }

    if protocol not in protocolMap:
        logger.error('Unsupported protocol %r, available: %s' % (protocol, ', '.join(protocolMap.keys())))
        return -1;

    app = protocolMap[protocol]()

    parser = argparse.ArgumentParser()

    parser.add_argument('-manifest_file',
                        help='path to the input manifest file')
    parser.add_argument('-manifest_source',
                        help='input manifest source')
    parser.add_argument('-timestamps',
                        help='temporary directory used to store application metadata')
    parser.add_argument('-set',
                        help='artifact set name, if not provided the default set will be used')
    parser.add_argument('-force', action='store_true',
                        help='if set to true, all artifacts will be pushed regardless of their timestamp')

    app.createArgParser(parser)

    args = parser.parse_args()

    if not app.parseArgs(args):
        return -1

    try:
        if args.manifest_file:
            manifest = ArtifactManifest.parseFile(args.manifest_file, app.getManifestEnv())
        elif args.manifest_source:
            manifest = ArtifactManifest.parseSource(args.manifest_source, app.getManifestEnv())
        else:
            logger.error('Manifest file nor source provided')
            return -1

        artifacts = manifest.getArtifactSet(args.set)

        if not artifacts:
            logger.error('No artifact set found (set name=%r)' % args.set)
            return -1

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.debug('#' * 40)
        logger.error('Error getting artifacts')
        return -1

    timestampFile = '.smart-push-timestamps'
    if args.timestamps:
        timestampFile = args.timestamps

    try:
        res = app.execute(args, artifacts, timestampFile, args.force)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.debug('#' * 40)
        logger.error('Error installing artifacts')
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

