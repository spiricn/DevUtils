import argparse
import sys

from du.android.smartpush.AndroidSmartPushApp import main as smartpushMain
from du.drepo.App import main as drepoMain
from du.drepo.indexer.App import main as indexerMain


def main():
    apps = {
        'drepo' : drepoMain,
        'sp' : smartpushMain,
        'drepo-index' : indexerMain
    }



    parser = argparse.ArgumentParser()

    parser.add_argument('appName',
                        help='Available apps: ' + str(apps.keys()))

    args = parser.parse_args()

    if args.appName not in apps:
        print('Invalid app name: %r' % args.appName)
        return -1
    else:
        sys.argv.pop(1)
        return apps[args.appName]()

if __name__ == '__main__':
    sys.exit(main())
