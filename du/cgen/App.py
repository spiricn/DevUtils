import argparse
import logging
from os.path import os
import sys

from du.cgen.Generator import TYPE_BOOL, TYPE_INT32, TYPE_STRING, Param
from du.cgen.JavaGenerator import JavaGenerator


LANG_JAVA = 'java'

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    logger = logging.getLogger(__name__.split('.')[-1])

    parser = argparse.ArgumentParser()

    parser.add_argument('lang')
    parser.add_argument('outputFile')
    parser.add_argument('-java_class')
    parser.add_argument('-java_package')
    parser.add_argument('-args', nargs='+')

    langs = [LANG_JAVA]

    args = parser.parse_args()

    params = []
    for i in range(int(len(args.args) / 2)):
        name = args.args[i * 2 + 0]
        arg = args.args[i * 2 + 1]

        value = None

        if value == None:
            try:
                value = int(arg)
                paramType = TYPE_INT32
            except ValueError:
                pass

        if value == None:
            if arg.lower() in ['true', 'false']:
                value = True if arg.lower() == 'true' else False
                paramType = TYPE_BOOL

        if value == None:
            value = arg
            paramType = TYPE_STRING

        param = Param(paramType, name, value)

        logger.debug('Adding param: %s' % str(param))

        params.append(param)

    if args.lang not in langs:
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
    if os.path.exists(args.outputFile):
        with open(args.outputFile, 'r') as fileObj:
            oldContent = fileObj.read()

    if oldContent == newContent:
        logger.debug('File up-to-date')
        return 0

    with open(args.outputFile, 'w') as fileObj:
        fileObj.write(newContent)

    logger.debug('File updated: %r' % args.outputFile)

    return 0


if __name__ == '__main__':
    sys.exit(main())
