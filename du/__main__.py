import sys
import du
import importlib


def main():
    apps = {
        "version": lambda: sys.stdout.write(du.__version_name__ + "\n"),
        "drepo": "du.drepo.App",
        "ctee": "du.ctee.App",
        "cgen": "du.cgen.App",
        "hdump": "du.android.hdump.App",
        "docker": "du.docker.App",
        "afact": "du.afact.App",
        "denv": "du.denv.App",
        "adb": "du.android.adb.App",
    }

    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "help", "--h"]:
        print("Available apps: " + str(apps.keys()))
        return -1

    appName = sys.argv[1]

    if appName not in apps:
        print("Invalid app name: %r" % appName)
        return -1

    sys.argv.pop(1)

    return importlib.import_module(apps[appName]).main()


if __name__ == "__main__":
    sys.exit(main())
