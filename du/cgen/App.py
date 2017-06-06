import argparse
import logging
from os.path import os
import sys

from du.cgen.Generator import TYPE_BOOL, TYPE_INT32, TYPE_STRING, Param
from du.cgen.JavaGenerator import JavaGenerator


LANG_JAVA = 'java'

def main():
    supportedLangs = [LANG_JAVA]

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    logger = logging.getLogger(__name__.split('.')[-1])

    parser = argparse.ArgumentParser()

    parser.add_argument('lang',
                        help='generator language. available languages=%s' % ','.join(supportedLangs))
    parser.add_argument('outputFile',
                        help='output file path; generated source will be stored here. to use stdout set to -')
    parser.add_argument('-java_class',
                        help='if language is set to %r, this will be the name of the java class generated' % LANG_JAVA)
    parser.add_argument('-java_package',
                        help='if lang is set to %r, this will be the package of the java class generated' % LANG_JAVA)
    parser.add_argument('-args', nargs='+',
                        help='a list of <name, value> pairs')

    args = parser.parse_args()

    if args.lang not in supportedLangs:
        logger.error('Invalid language: %r' % args.lang)
        return -1;

    params = []

    if args.args:
        if len(args.args) % 2 != 0:
            logger.error('Invalid number of args: %d' % len(args.args))
            return -1

        # Parse arguments

        for i in range(int(len(args.args) / 2)):
            name = args.args[i * 2 + 0]
            arg = args.args[i * 2 + 1]

            value = None

            if value == None:
                # First try casting it to int
                try:
                    value = int(arg)
                    paramType = TYPE_INT32
                except ValueError:
                    pass

            # Try boolean
            if value == None:
                if arg.lower() in ['true', 'false']:
                    value = True if arg.lower() == 'true' else False
                    paramType = TYPE_BOOL

            # Default to string
            if value == None:
                value = arg
                paramType = TYPE_STRING

            param = Param(paramType, name, value)
            params.append(param)

            logger.debug('Adding param: %s' % str(param))

        params.append(param)

    if args.lang not in supportedLangs:
        logger.error('Invalid language: %r' % args.lang)
        return -1;

    logger.debug('Generating %s ..' % args.lang)

    if args.lang == LANG_JAVA:
        if not args.java_class:
            logger.error('Java class not provided')
            return -1

        if not args.java_package:
            logger.error('Java package not provided')
            return -1
        generator = JavaGenerator(args.java_package, args.java_class, params)
    else:
        raise NotImplementedError("Unsupported lang: %r" % args.lang)

    newContent = generator.generate()

    oldContent = None
    if args.outputFile != '-' and  os.path.exists(args.outputFile):
        with open(args.outputFile, 'r') as fileObj:
            oldContent = fileObj.read()

        if oldContent == newContent:
            logger.debug('File up-to-date')
            return 0

    if args.outputFile != '-':
        outDir = os.path.dirname(args.outputFile)

        if not os.path.exists(outDir):
            os.makedirs(outDir)

        with open(args.outputFile, 'w') as fileObj:
            fileObj.write(newContent)
    else:
        sys.stdout.write(newContent)

    logger.debug('File updated: %r' % args.outputFile)

    return 0


if __name__ == '__main__':
    sys.exit(main())
