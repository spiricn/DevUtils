import argparse
import logging
import os
import sys
import traceback

from du.drepo.DRepo import DRepo
from du.drepo.Manifest import Manifest
from du.drepo.indexer.JenkinsManifestExtractor import extractManifest, \
    processVars
from du.utils.ShellCommand import ShellCommand

logger = logging.getLogger(__name__.split('.')[-1])

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
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s/%(name)s: %(message)s')

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

    logger.debug('parsing manifest ..')
    try:
        manifest = extractManifest(manifestPath, args.paramName)
        manifest = processVars(manifest, eval(args.vars))

        if args.sync:
            logger.debug('syncing sources ..')
            syncSource(manifest)

        logger.debug('indexing ..')
        indexSource(args.grok, args.grokRoot)
    except:
        traceback.print_exc(file=sys.stdout)
        logger.error('-----------------------------------')
        logger.error('indexing failed')
        return -1


    logger.debug('-------------------------------')
    logger.debug('done')

    return 0

if __name__ == '__main__':
    sys.exit(main())
