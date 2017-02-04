from collections import namedtuple
import re

from du.Utils import shellCommand


RemoteHead = namedtuple('RemoteBranch', 'hash, name')
RemoteItem = namedtuple('RemoteItem', 'hash, number, patchset')
RemoteInfo = namedtuple('RemoteInfo', 'head, changes, heads')
LogItem = namedtuple('LogItem', 'hash, title')
gerritChangeIdRegex = re.compile(r'^Change-Id: (I[a-fA-F0-9]+)$')

class Change:
    def __init__(self, arg):
        if isinstance(arg, int):
            self.number = arg
            self.ps = None
        elif isinstance(arg, str):
            if '/' in arg:
                self.number, self.ps = [int(i) for i in i.split('/')]
            else:
                self.number = int(i)
                self.ps = None

    def __str__(self):
        return '<Change: number=%d%s>' % (self.number, ' ps=%d' % self.ps if self.ps != None else '')

def getLog(repo):
    cmdRes = shellCommand(['git', '-C', repo, 'log', '--pretty=oneline'])

    if cmdRes.rc != 0:
        raise RuntimeError('Command failed (%d): %r' % (cmdRes.rc, cmdRes.stderr))

    items = []

    for line in cmdRes.stdout.splitlines():
        spliter = line.find(' ')

        commitHash = line[:spliter].strip()
        commitMessage = line[spliter + 1:].rstrip()

        items.append(LogItem(commitHash, commitMessage))

    return items

def getChangeHash(repo, change, remotes=None):
    remotes = lsRemote(repo) if not remotes else remotes

    if change.ps == None:
        latestPs = getLatestPatchset(repo, change.number, remotes)
        for i in remotes.changes:
            if i.patchset == latestPs and change.number == i.number:
                return i.hash
    else:
        for i in remotes.changes:
            if i.number == change.number and i.patchset == change.ps:
                return i.hash

    return None

def findRemote(repo, commitHash, remotes=None):
    remotes = lsRemote(repo) if not remotes else remotes

    for change in remotes.changes:
        if change.hash == commitHash:
            return change

    return None

def lsRemote(repo):
    cmdRes = shellCommand(['git', 'ls-remote', repo])
    if cmdRes.rc != 0:
        raise RuntimeError('Command failed (%d): %r' % (cmdRes.rc, cmdRes.stderr))
    heads = []
    head = ''
    changes = []

    for line in cmdRes.stdout.splitlines():
        commitHash, info = line.split('\t')

        if 'refs/changes' in info:
            tokens = info.split('/')

            number = int(tokens[-2])

            patchset = int(tokens[-1])

            changes.append(RemoteItem(commitHash.strip(), number, patchset))

        elif 'HEAD' in info:
            head = commitHash

        elif 'refs/heads' in info:
            tokens = info.split('/')

            name = tokens[-1]

            heads.append(RemoteHead(commitHash, name))

    return RemoteInfo(head, changes, heads)

def getCommitMessage(repo, commitHash):
    assert(len(commitHash) == 40)

    cmdRes = shellCommand(['git', '-C', repo, 'show', '-s', '--format=%B', commitHash])
    if cmdRes.rc != 0:
        raise RuntimeError('Command failed (%d): %r' % (cmdRes.rc, cmdRes.stderr))

    message = ''
    for line in cmdRes.stdout:
        message += line

    return message

def getCommitGerritChangeId(message):
    for line in reversed(message.splitlines()):
        matches = gerritChangeIdRegex.findall(line)

        if len(matches) != 1:
            continue

        return matches[0]

    return None

def getLatestPatchset(remoteUrl, change, remotes=None):
    patchsets = []

    remotes = lsRemote(remoteUrl) if not remotes else remotes

    for i in remotes.changes:
        if i.number == change:
            patchsets.append(i.patchset)

    if patchsets:
        return max(patchsets)
    else:
        return None

