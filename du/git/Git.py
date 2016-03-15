from collections import namedtuple
import re
import subprocess
from du.Utils import shellCommand


RemoteHead = namedtuple('RemoteBranch', 'hash, name')
RemoteItem = namedtuple('RemoteItem', 'hash, number, patchset')
RemoteInfo = namedtuple('RemoteInfo', 'head, changes, heads')
LogItem = namedtuple('LogItem', 'hash, title')
gerritChangeIdRegex = re.compile(r'^Change-Id: (I[a-fA-F0-9]+)$')

def getLog(repo):
    cmdRes = shellCommand(['git', 'log', '--pretty=oneline'])

    if cmdRes.rc != 0:
        return None

    items = []

    for line in cmdRes.stdout:
        spliter = line.find(' ')

        commitHash = line[:spliter].strip()
        commitMessage = line[spliter + 1:].rstrip()

        items.append(LogItem(commitHash, commitMessage))

    return items

def lsRemote(repo):
    cmdRes = shellCommand(['git', 'ls-remote'])

    heads = []
    head = ''
    changes = []

    for line in cmdRes.stdout:
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
    cmdRes = shellCommand(['git', 'show', '-s', '--format=%B', commitHash])

    message = ''
    for line in cmdRes.stdout:
        message += line

    return message

def getCommitGerritChangeId(message):
    lastLine = message.splitlines(False)[-1]

    matches = gerritChangeIdRegex.findall(lastLine)

    if len(matches) != 1:
        return None

    return matches[0]

