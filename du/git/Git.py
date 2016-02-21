from collections import namedtuple
import re
import subprocess


RemoteHead = namedtuple('RemoteBranch', 'hash, name')
RemoteItem = namedtuple('RemoteItem', 'hash, number, patchset')
RemoteInfo = namedtuple('RemoteInfo', 'head, changes, heads')
LogItem = namedtuple('LogItem', 'hash, title')
gerritChangeIdRegex = re.compile(r'^Change-Id: (I[a-fA-F0-9]+)$')

def getLog(repo):
    pipe = subprocess.Popen(['git', 'log', '--pretty=oneline'], stdout=subprocess.PIPE, cwd=repo)

    items = []

    for line in pipe.stdout:
        spliter = line.find(' ')

        commitHash = line[:spliter].strip()
        commitMessage = line[spliter + 1:].rstrip()

        items.append(LogItem(commitHash, commitMessage))

    return items

def lsRemote(repo):
    pipe = subprocess.Popen(['git', 'ls-remote'], stdout=subprocess.PIPE, cwd=repo)

    heads = []
    head = ''
    changes = []

    for line in pipe.stdout:
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
    pipe = subprocess.Popen(['git', 'show', '-s', '--format=%B', commitHash], stdout=subprocess.PIPE, cwd=repo)

    message = ''
    for line in pipe.stdout:
        message += line

    return message

def getCommitGerritChangeId(message):
    lastLine = message.splitlines(False)[-1]

    matches = gerritChangeIdRegex.findall(lastLine)

    if len(matches) != 1:
        return None

    return matches[0]

