import logging
import os

from du.drepo.Gerrit import Gerrit
from du.drepo.Manifest import  OPT_CLEAN
from du.utils.ShellCommand import  ShellFactory
from du.Utils import makeDirTree


logger = logging.getLogger(__name__.split('.')[-1])

class DRepo:
    def __init__(self, manifest):
        self._manifest = manifest
        self._sf = ShellFactory(raiseOnError=True, commandOutput=True)

    def run(self):
        for project in self._manifest.projects:
            gr = Gerrit(project.remote.username, project.remote.port, project.remote.server, self._sf)

            projAbsPath = os.path.join(self._manifest.build.root, project.path)

            if not os.path.exists(os.path.join(projAbsPath, '.git')):
                # Clone
                logger.debug('cloning %r' % project.name)

                makeDirTree(projAbsPath)

                self._sf.spawn(['git', 'init'], projAbsPath)
                self._sf.spawn(['git', 'remote', 'add', 'origin', project.url], projAbsPath)
                self._sf.spawn(['git', 'pull', 'origin', 'master'], projAbsPath)

            # Make sure GIT doesn't attempt to create merge commits
            self._sf.spawn(['git', 'config', 'pull.ff', 'only'], projAbsPath)

            # Fetch
            logger.debug('fetching %r' % project.name)
            self._sf.spawn(['git', 'fetch'], cwd=projAbsPath)

            # Clean
            if OPT_CLEAN in project.opts:
                logger.debug('cleaning %r' % project.name)

                self._sf.spawn(['git', 'clean', '-dfx'], cwd=projAbsPath)

            # Reset
            logger.debug('resetting %r' % project.name)
            self._sf.spawn(['git', 'reset', '--hard', 'origin/%s' % project.branch], cwd=projAbsPath)

            # Pull final touch
            finalTouch = self._manifest.build.finalTouches[project.name] if project.name in self._manifest.build.finalTouches else None
            if finalTouch:
                logger.debug('pulling final touch %s for %r' % (str(finalTouch), project.name))

                ref = gr.getPatchset(finalTouch.number, finalTouch.ps)['ref']

                self._sf.spawn(['git', 'pull', 'origin', ref], cwd=projAbsPath)

            # Download cherry picks
            cherryPicks = self._manifest.build.cherrypicks[project.name] if project.name in self._manifest.build.cherrypicks else []
            for cp in cherryPicks:
                logger.debug('downloading cherry pick %s for %r' % (str(cp), project.name))

                ref = gr.getPatchset(cp.number, cp.ps)['ref']

                self._sf.spawn(['git', 'fetch', 'origin', ref], cwd=projAbsPath)
                self._sf.spawn(['git', 'cherry-pick', 'FETCH_HEAD'], cwd=projAbsPath)
