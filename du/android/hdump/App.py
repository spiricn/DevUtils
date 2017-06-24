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

    args = parser.parse_args()

    with open(args.dumpFile, 'r') as fileObj:
        heapDumpString = fileObj.read()

    heapDump = HeapDump(heapDumpString, [args.symbolsDir])

    renderers = {
        args.plainOutput : PlainTextRenderer,
        args.htmlOutput : HtmlRenderer,
    }

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

    return 0

if __name__ == '__main__':
    sys.exit(main())
