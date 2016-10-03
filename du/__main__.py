import sys

import du
from du.android.smartpush.AndroidArtifactTool import main as artifactMain
from du.android.smartpush.AndroidSmartPushApp import main as smartpushMain
from du.drepo.App import main as drepoMain
from du.drepo.indexer.App import main as indexerMain


def main():
    apps = {
        'drepo' : drepoMain,
        'sp' : smartpushMain,
        'drepo-index' : indexerMain,
        'artifact' : artifactMain,
        'version' : lambda: sys.stdout.write(du.__version__ + '\n')
    }

    if len(sys.argv) < 2:
        print('Available apps: ' + str(apps.keys()))
        return -1

    appName = sys.argv[1]

    if appName not in apps:
        print('Invalid app name: %r' % appName)
        return -1
    else:
        sys.argv.pop(1)
        return apps[appName]()

if __name__ == '__main__':
    sys.exit(main())
