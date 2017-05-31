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

    parser.add_argument('-manifest_file')
    parser.add_argument('-manifest_source')
    parser.add_argument('-notes')
    parser.add_argument('-sync', action='store_true')

    args = parser.parse_args()

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
        manifest = Manifest(manifestSource)
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
