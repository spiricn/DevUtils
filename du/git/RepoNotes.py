import logging

from du.git import Git


logger = logging.getLogger(__name__)

class RepoNotes:
    def __init__(self, repoDir, repoUrl):
        self._repoDir = repoDir
        self._repoUrl = repoUrl
        self._remoteInfo = Git.lsRemote(self._repoUrl)
        self._log = Git.getLog(self._repoDir)
        self.buildNotes()

    @property
    def log(self):
        return self._log

    @property
    def remoteInfo(self):
        return self._remoteInfo

    @property
    def remoteItems(self):
        return self._remoteItems

    def buildNotes(self, history=25):
        history = min(history, len(self._log), len(self._remoteInfo.changes) + 1)

        res = ''

        for commit in self._log[:history]:
            # skip head
            if commit.hash == self._remoteInfo.head:
                continue

            # check if this change id is in repository remote list
            change = self.findChange(commit.hash)

            number = '-'
            patchset = '-'

            if change:
                # change is on gerrit
                number = '%d' % change.number
                patchset = '%d' % change.patchset

            else:
                # change not on gerrit or cherry picked
                logger.warning('Could not find change %s in repo %r' % (commit.hash, self._repoDir))

            res += ' + %s/%s : %s\n' % (number, patchset, commit.title)

        return res

    def findChange(self, commitHash):
        for item in self._remoteInfo.changes:
            if item.hash == commitHash:
                return item
