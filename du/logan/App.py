import argparse
import logging
import sys

from du.logan.Logan import Logan


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    logger = logging.getLogger(__name__.split('.')[-1])

    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')

    parser.add_argument('-points', nargs='+',
                        help='a list of point regexes')

    args = parser.parse_args()

    la = Logan(args.points)

    with open(args.input, 'r') as fileObj:
        with open(args.output, 'w') as outputFile:
            la.parse(fileObj, outputFile)

    return 0

if __name__ == '__main__':
    sys.exit(main())
