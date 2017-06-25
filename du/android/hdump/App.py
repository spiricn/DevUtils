import argparse
import logging
import sys

from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.renderer.HtmlRenderer import HtmlRenderer
from du.android.hdump.renderer.PlainTextRenderer import PlainTextRenderer



logger = logging.getLogger(__name__.split('.')[-1])

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    parser = argparse.ArgumentParser()

    parser.add_argument('dumpFile')
    parser.add_argument('-symbolsDir')
    parser.add_argument('-plainOutput')
    parser.add_argument('-htmlOutput')
    parser.add_argument('--qt', action='store_true')

    args = parser.parse_args()

    with open(args.dumpFile, 'r') as fileObj:
        heapDumpString = fileObj.read()

    renderers = {
        args.plainOutput : PlainTextRenderer,
        args.htmlOutput : HtmlRenderer,
    }

    if args.qt:
        try:
            from du.android.hdump.renderer.qt.QtRenderer import QtRenderer
        except ImportError as e:
            pyVersion = '%d.%d.%d' % (sys.version_info.major,
                                      sys.version_info.minor,
                                      sys.version_info.micro)
            logger.fatal(e)
            logger.fatal('#' * 40)
            logger.fatal('PyQt not installed for Python %s; install it with: sudo apt-get install python3-pyqt4' % pyVersion)
            return -1

    heapDump = HeapDump(heapDumpString, [args.symbolsDir])

    for filePath, rendererCls in renderers.items():
        if not filePath:
            continue

        if filePath == '-':
            fileObj = sys.stdout
        else:
            fileObj = open(filePath, 'w')

        rendererCls().render(fileObj, heapDump)
        if filePath != '-':
            fileObj.close()

    if args.qt:
        QtRenderer().render(heapDump)

    return 0

if __name__ == '__main__':
    sys.exit(main())
