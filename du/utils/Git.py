from collections import namedtuple
import re

from du.Utils import shellCommand

LogItem = namedtuple('LogItem', 'hash, title')
gerritChangeIdRegex = re.compile(r'^Change-Id: (I[a-fA-F0-9]+)$')

Tag = namedtuple('Tag', 'hash, name')

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

def getTag(repo):
    # Get the tag ID
    cmdRes = shellCommand(['git', '-C', repo, 'rev-parse', 'HEAD'])
    if cmdRes.rc != 0:
        raise RuntimeError('Command failed (%d): %r' % (cmdRes.rc, cmdRes.strStderr))
    tagHash = cmdRes.strStdout.rstrip()

    # Get tag name
    cmdRes = shellCommand(['git', '-C', repo, 'describe', '--exact-match', '--tags', tagHash])
    if cmdRes.rc != 0:
        return None

    tagName = cmdRes.strStdout

    return Tag(tagHash, tagName)

def getLog(repo):
    cmdRes = shellCommand(['git', '-C', repo, 'log', '--pretty=oneline'])

    if cmdRes.rc != 0:
        raise RuntimeError('Command failed (%d): %r' % (cmdRes.rc, cmdRes.strStderr))

    items = []

    for line in cmdRes.strStdout.splitlines():
        spliter = line.find(' ')

        commitHash = line[:spliter].strip()
        commitMessage = line[spliter + 1:].rstrip()

        items.append(LogItem(commitHash, commitMessage))

    return items

def getCommitMessage(repo, commitHash):
    assert(len(commitHash) == 40)

    cmdRes = shellCommand(['git', '-C', repo, 'show', '-s', '--format=%B', commitHash])
    if cmdRes.rc != 0:
        raise RuntimeError('Command failed (%d): %r' % (cmdRes.rc, cmdRes.strStderr))

    message = ''
    for line in cmdRes.strStdout:
        message += line

    return message

def getCommitGerritChangeId(message):
    for line in reversed(message.splitlines()):
        matches = gerritChangeIdRegex.findall(line)

        if len(matches) != 1:
            continue

        return matches[0]

    return None

