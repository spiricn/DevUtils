import argparse
import os
import sys
import traceback

from du.drepo.DRepo import DRepo
from du.drepo.Manifest import Manifest
from du.drepo.indexer.JenkinsManifestExtractor import extractManifest, \
    processVars
from du.utils.ShellCommand import ShellCommand

def syncSource(manifest):
    manifest = Manifest(manifest)

    try:
        drepo = DRepo(manifest)
        drepo.run()

    except Exception:
        traceback.print_exc(file=sys.stdout)

def indexSource(grok, grokRoot):
    ShellCommand.run(['sudo', grok, 'index', grokRoot])

def main():
    # Parser command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('grok')
    parser.add_argument('grokRoot')
    parser.add_argument('jenkinsJob')
    parser.add_argument('paramName')
    parser.add_argument('vars')
    parser.add_argument('-sync', action='store_true')

    args = parser.parse_args()

    manifestPath = os.path.join(args.jenkinsJob, 'config.xml')

    manifest = extractManifest(manifestPath, args.paramName)

    manifest = processVars(manifest, eval(args.vars))

    if args.sync:
        syncSource(manifest)

    indexSource(args.grok, args.grokRoot)

    return 0

if __name__ == '__main__':
    sys.exit(main())
