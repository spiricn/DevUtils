import logging

from du.git import Git


logger = logging.getLogger(__name__)

class RepoNotes:
    def __init__(self, repo):
        self._repo = repo
        self._remoteInfo = Git.lsRemote(repo)
        self._log = Git.getLog(repo)
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
            if commit.hash == self._remoteInfo.head:
                continue

            changeId = Git.getCommitGerritChangeId(Git.getCommitMessage(self._repo, commit.hash))
            change = self.findChange(commit.hash)

            number = '-'
            patchset = '-'

            if change:
                number = '%d' % change.number
                patchset = '%d' % change.patchset

            elif changeId:
                number = changeId

            else:
                logger.warning('Could not find change %s in repo %r' % (commit.hash, self._repo))

            res += ' + %s/%s : %s\n' % (number, patchset, commit.title)

        return res

    def findChange(self, commitHash):
        for item in self._remoteInfo.changes:
            if item.hash == commitHash:
                return item
