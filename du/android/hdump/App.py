import argparse
import logging
import sys

from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.HeapDumpDiff import HeapDumpDiff
from du.android.hdump.renderer.HtmlRenderer import HtmlRenderer
from du.android.hdump.renderer.PlainTextRenderer import PlainTextRenderer


logger = logging.getLogger(__name__.split('.')[-1])

def displayDump(dump):
    pass

def displayDiff(dump1, dump2):
    pass

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

    parser = argparse.ArgumentParser()

    parser.add_argument('-dump_files', nargs='+', required=True)
    parser.add_argument('-symbol_dirs', nargs='+')
    parser.add_argument('-plain_output')
    parser.add_argument('-html_output')
    parser.add_argument('--qt', action='store_true')

    args = parser.parse_args()

    # Verify dump file input
    if len(args.dump_files) not in[1, 2]:
        logger.error('Invalid number of input files: %d' % len(args.dump_files))
        return -1

    dumps = []

    for file in args.dump_files:
        with open(file, 'r') as fileObj:
            dumps.append(HeapDump(fileObj.read(), args.symbol_dirs))

    if len(dumps) == 1:
        renderObj = dumps[0]
    else:
        renderObj = HeapDumpDiff(dumps[0], dumps[1])

    renderers = (
        (args.plain_output, PlainTextRenderer),
        (args.html_output, HtmlRenderer),
    )

    for filePath, rendererCls in renderers:
        if not filePath:
            continue

        if filePath == '-':
            fileObj = sys.stdout
        else:
            fileObj = open(filePath, 'w')

        rendererCls().render(fileObj, renderObj)
        if filePath != '-':
            fileObj.close()

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

        QtRenderer.render(renderObj)

    return 0

if __name__ == '__main__':
    sys.exit(main())
