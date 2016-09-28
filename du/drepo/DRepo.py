import logging
import os
import shutil

from du.drepo.ReleaseNoteWriter import ReleaseNotesHtmlWriter
from du.utils import Git
from du.utils.Git import Change
from du.utils.ShellCommand import ShellCommand
from du.drepo.Manifest import OPT_CLEAN, OPT_RESET

logger = logging.getLogger(__name__.split('.')[-1])

class DRepo:
    REPO_REMOTE_NAME = '.repo_remote'
    REPO_NAME = '.repo'
    MANIFEST_NAME = 'default.xml'

    def __init__(self, manifest):
        self._manifest = manifest

    def run(self):
        # Create repo remote
        if not os.path.exists(self.repoRemotePath):
            logger.debug('creating remote repo at %r ..' % self.repoRemotePath)

            os.makedirs(self.repoRemotePath)
            ShellCommand.run('git init --bare', cwd=self.repoRemotePath)

        logger.debug('updating manifest ..')
        self._updateManifest()

        # Create repo
        repoDir = os.path.join(self._manifest.root, self.REPO_NAME)
        if not os.path.exists(repoDir):
            logger.debug('initializing repo at %r ..' % repoDir)
            ShellCommand.run(('repo',  'init', '-u', self.repoRemotePath, '--no-clone-bundle'), self._manifest.root)
        else:
            cleanProjects = self._manifest.findProjectsWithOpt(OPT_CLEAN)
            if cleanProjects:
                logger.debug('cleaning projects (%s)..', ','.join(proj.name for proj in cleanProjects))
                regex = '^('
                for proj in cleanProjects:
                        regex += proj.name + '|'
                if regex.endswith('|'):
                    regex = regex[:-1]
                regex += ')$'

                logger.debug(ShellCommand.run(['repo', 'forall', '-r', regex, '-c', 'git clean -dfx'], self._manifest.root).stdoutStr)

            resetProjects = self._manifest.findProjectsWithOpt(OPT_RESET)
            if resetProjects:
                logger.debug('resetting projects (%s)..', ','.join(proj.name for proj in resetProjects))
                regex = '^('
                for proj in resetProjects:
                        regex += proj.name + '|'
                if regex.endswith('|'):
                    regex = regex[:-1]
                regex += ')$'

                logger.debug(ShellCommand.run(['repo', 'forall', '-r', regex, '-c', 'git reset --hard'], self._manifest.root).stdoutStr)

        logger.debug('synchronizing ..')
        ShellCommand.run('repo sync -j8', self._manifest.root)

        logger.debug('applying cherry-picks ..')
        self._applyCherryPicks()

    def _updateManifest(self):
        res = ShellCommand.run('mktemp -d')
        tmpDirPath = res.stdoutStr.strip()

        repoLocalDir = os.path.join(tmpDirPath, os.path.basename(self.repoRemotePath))

        res = ShellCommand.run('git clone ' + self.repoRemotePath, tmpDirPath)

        with open(os.path.join(repoLocalDir, self.MANIFEST_NAME), 'w') as fileObj:
            fileObj.write(self._manifest.repoManifestXml)

        ShellCommand.run('git add ' + self.MANIFEST_NAME, repoLocalDir)

        res = ShellCommand.run('git diff --cached --name-only', repoLocalDir)
        if res.stdoutStr.strip():
            ShellCommand.run('git commit -a -m "update"', repoLocalDir)
            ShellCommand.run('git push origin master', repoLocalDir)

        shutil.rmtree(tmpDirPath)

    def _applyCherryPicks(self):
        for proj in self._manifest.projects:
            if not proj.cherry_picks:
                continue

            logger.debug('for %s ..' % proj.name)

            remotes = Git.lsRemote(proj.url)

            for change in proj.cherry_picks:
                if change.ps == None:
                    ps = Git.getLatestPatchset(proj.url, change.number, remotes)
                    change = Change(change.number, ps)

                logger.debug('applying %d/%d ..', change.number, change.ps)

                ShellCommand.run('repo download -c %s %d/%d' % (proj.name, change.number, change.ps), self._manifest.root)

    @staticmethod
    def generateNotes(manifest, outputFile):
        writer = ReleaseNotesHtmlWriter(manifest)

        historyLength = 15

        writer.start(manifest)

        for proj in manifest.projects:
            logger.debug('for %s ..' % proj.name)
            writer.startProject(proj)

            localDir = os.path.join(manifest.root, proj.path)

            log = Git.getLog(localDir)[:-1]

            remotes = Git.lsRemote(proj.url)

            cherryPickHashes = []

            for change in reversed(proj.cherry_picks):
                commitHash = Git.getChangeHash(proj.url, change, remotes)
                assert(commitHash != None)

                res = ShellCommand.run('git log --format=%s -n 1 ' + commitHash, os.path.join(manifest.root, proj.path))

                title = res.stdoutStr.strip()

                assert(title)

                ps = change.ps

                if ps == None:
                    ps = Git.getLatestPatchset(proj.url, change.number, remotes)

                writer.addChange(change.number, ps, title, cherryPick=True)

                cherryPickHashes.append(commitHash)

                entry = log.pop(0)


                logger.debug('cp %s %s' % (entry.title, title))

            maxHistory = 15

            for entry in log:
                remoteItem = Git.findRemote(proj.url, entry.hash, remotes)
                if remoteItem:
                    writer.addChange(remoteItem.number, remoteItem.patchset, entry.title, cherryPick=False)
                    historyLength -= 1

                    if not historyLength:
                        break
                else:
                    changeId = Git.getCommitGerritChangeId(Git.getCommitMessage(localDir, entry.hash))

                    logger.warning('Could not find change for %s, changeId=%s' % (str(entry), changeId))
                    writer.addChange(-1, -1, entry.title, cherryPick=False)

                maxHistory -= 1

                if maxHistory == 0:
                    break

            writer.endProject()

        writer.end()

        with open(outputFile, 'wb') as fileObj:
            fileObj.write(writer.notes)

            logger.debug('notes written to %r' % outputFile)

    @property
    def repoRemotePath(self):
        return os.path.join(self._manifest.root, self.REPO_REMOTE_NAME)

    @property
    def root(self):
        return self._manifest.root
