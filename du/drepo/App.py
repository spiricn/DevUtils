import argparse
import logging
import sys
import traceback

from du.drepo.DRepo import DRepo


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    logger = logging.getLogger(__name__.split('.')[-1])

    parser = argparse.ArgumentParser()

    parser.add_argument('-manifest_file')
    parser.add_argument('-manifest_source')
    parser.add_argument('-notes')

    args = parser.parse_args()

    if args.manifest_file and args.manifest_source:
        logger.error('arguments -manifest_file and -manifest_source are mutually exclusive')
        return -1
    elif args.manifest_file:
        with open(args.manifest_file, 'rb') as fileObj:
            manifest = fileObj.read()

    elif args.manifest_source:
        manifest = args.manifest_source

    else:
        logger.error('manifest not provided')
        return -1;

    try:
        drepo = DRepo(manifest, args.notes)
        drepo.run()

        return 0
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logger.error('-----------------------------------')
        logger.error('drepo failed')
        return -1

if __name__ == '__main__':
    sys.exit(main())
