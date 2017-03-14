import argparse
import logging
import sys
import traceback

from du.drepo.DRepo import DRepo
from du.drepo.Gerrit import Gerrit
from du.drepo.Manifest import Manifest
from du.drepo.ReleaseNoteGenerator import ReleaseNoteGenerator


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('username')
    parser.add_argument('server')
    parser.add_argument('port')
    
    parser.add_argument('--change')
    parser.add_argument('--change_ref', action='store_true')

    args = parser.parse_args()
    
    gr = Gerrit(args.username, args.port, args.server)
    
    if args.change:
        change = gr.getPatchset(args.change)

        if args.change_ref:
            sys.stdout.write(change['ref'])

            return 0

    return -1


if __name__ == '__main__':
    sys.exit(main())
