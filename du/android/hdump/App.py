import argparse
import logging
import sys

from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.SymbolResolver import SymbolResolver
from du.android.hdump.renderer.PlainTextRenderer import PlainTextRenderer


logger = logging.getLogger(__name__.split('.')[-1])

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    parser = argparse.ArgumentParser()

    parser.add_argument('dumpFile')
    parser.add_argument('-symbolsDir')
    parser.add_argument('-outputFile')

    args = parser.parse_args()

    with open(args.dumpFile, 'r') as fileObj:
        heapDumpString = fileObj.read()

    resolver = SymbolResolver([args.symbolsDir])

    heapDump = HeapDump(heapDumpString, resolver)

    renderer = PlainTextRenderer()

    if not args.outputFile or args.outputFile == '-':
        outputFile = sys.stdout
    else:
        outputFile = open(args.outputFile, 'w')

    renderer.render(outputFile, heapDump.rootNode)

    if args.outputFile and args.outputFile != '-':
        outputFile.close()

    logger.debug('output file: %r' % args.outputFile)

    return 0

if __name__ == '__main__':
    sys.exit(main())
