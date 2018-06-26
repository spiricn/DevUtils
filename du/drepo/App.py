import argparse
import logging
import sys
import traceback

from du.drepo.DRepo import DRepo
from du.drepo.Manifest import Manifest
from du.drepo.ReleaseNoteGenerator import ReleaseNoteGenerator


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    logger = logging.getLogger(__name__.split('.')[-1])

    parser = argparse.ArgumentParser()

    parser.add_argument('-manifest_file',
                        help='path to manifest file')
    parser.add_argument('-manifest_source',
                        help='manifest source string')
    parser.add_argument('-notes',
                        help='release notes path; if set release notes will be generated and stored here')
    parser.add_argument('-sync', action='store_true',
                        help='if provided, drepo will syncrhonize source code'
                        )
    parser.add_argument('-build')

    args, unknown = parser.parse_known_args()

    manifestArgs = {}
    for i in unknown:
        tokens = i.split('=')
        if len(tokens) == 2:
            key, value = tokens
            logger.debug('adding arg: %r = %r' % (key, value))
            manifestArgs[key] = value

    if args.manifest_file and args.manifest_source:
        logger.error('arguments -manifest_file and -manifest_source are mutually exclusive')
        return -1
    elif args.manifest_file:
        with open(args.manifest_file, 'rb') as fileObj:
            manifestSource = fileObj.read()

    elif args.manifest_source:
        manifestSource = args.manifest_source

    else:
        logger.error('manifest not provided')
        return -1;

    logger.debug('parsing manifest ..')

    try:
        manifest = Manifest(manifestSource, buildName=args.build, args=manifestArgs)
    except:
        traceback.print_exc(file=sys.stdout)
        logger.error('-----------------------------------')
        logger.error('error parsing manifest')
        return -1

    if args.sync:
        logger.debug('syncing ..')
        try:
            drepo = DRepo(manifest)
            drepo.run()

        except Exception:
            traceback.print_exc(file=sys.stdout)
            logger.error('-----------------------------------')
            logger.error('drepo failed')
            return -1

    if args.notes:
        logger.debug('generating notes ..')
        try:
            generator = ReleaseNoteGenerator(manifest)
            generator.run(args.notes)
        except:
            traceback.print_exc(file=sys.stdout)
            logger.error('-----------------------------------')
            logger.error('error generating release notes')
            return -1

    logger.debug('-------------------------------')
    logger.debug('done')

    return 0


if __name__ == '__main__':
    sys.exit(main())
