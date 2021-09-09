import sys

import du
from du.android.hdump.App import main as hdumpMain
from du.cgen.App import main as cgenMain
from du.ctee.App import main as cteeMain
from du.drepo.App import main as drepoMain
from du.docker.App import main as dockerMain
from du.afact.App import main as afactMain
from du.denv.App import main as denvMain
from du.android.adb.App import main as adbMain


def main():
    apps = {
        "drepo": drepoMain,
        "version": lambda: sys.stdout.write(du.__version_name__ + "\n"),
        "ctee": cteeMain,
        "cgen": cgenMain,
        "hdump": hdumpMain,
        "docker": dockerMain,
        "afact": afactMain,
        "denv": denvMain,
        "adb": adbMain,
    }

    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "help", "--h"]:
        print("Available apps: " + str(apps.keys()))
        return -1

    appName = sys.argv[1]

    if appName not in apps:
        print("Invalid app name: %r" % appName)
        return -1

    sys.argv.pop(1)
    return apps[appName]()


if __name__ == "__main__":
    sys.exit(main())
