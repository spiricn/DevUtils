import argparse
import logging
from pastebin_python import PastebinPython
from pastebin_python.pastebin_constants import PASTE_PUBLIC, EXPIRE_10_MIN, \
    PASTE_UNLISTED, EXPIRE_1_DAY
from pastebin_python.pastebin_exceptions import PastebinBadRequestException, PastebinNoPastesException, PastebinFileException
from pastebin_python.pastebin_formats import FORMAT_NONE, FORMAT_PYTHON, FORMAT_HTML
import sys


def main():
        # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()

    parser.add_argument('key')
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('-file')
    parser.add_argument('-text')
    parser.add_argument('-name')
    parser.add_argument('-format')

    defaultFormat = FORMAT_NONE
    defaultExpiry = EXPIRE_1_DAY
    defaultVisibility = PASTE_UNLISTED

    args = parser.parse_args()

    # TODO format, expiry, visibility arguments

    expiry = defaultExpiry
    visibility = defaultVisibility

    pasteName = 'Untitled'
    if args.name:
        pasteName = args.name

    if args.format:
        textFormat = args.format
    else:
        textFormat = defaultFormat

    try:
        pbin = PastebinPython(api_dev_key=args.key)

        pbin.createAPIUserKey(args.username, args.password)

        res = None

        if args.file:
            res = pbin.createPasteFromFile(args.file, pasteName, textFormat, visibility, expiry)
        elif args.text:
            res = pbin.createPaste(args.text, pasteName, textFormat, visibility, expiry)
        else:
            parser.error('Neither file not text specified')
            return -1
    except Exception as e:
        logger.error(str(e))
        return -1

    print(res)

    return 0

if __name__ == '__main__':
    sys.exit(main())
