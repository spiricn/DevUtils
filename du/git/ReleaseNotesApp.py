import argparse
from collections import namedtuple
import logging
import sys

from du.git.RepoNotes import RepoNotes


Repo = namedtuple('Repo', 'name, path')

class ReleaseNotes:
    def __init__(self):
        self._repos = []

    def addRepo(self, name, path):
        self._repos.append(Repo(name, path))

    def buildNotes(self, title):
        res = title + '\n\n'

        for repo in self._repos:
            notes = RepoNotes(repo.path)

            res += 'Git %s HEAD : %s\n' % (repo.name, notes.remoteInfo.head)
            res += notes.buildNotes() + '\n'

        return res

def main():
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('repos', nargs='+')
    parser.add_argument('title')
    parser.add_argument('output')

    args = parser.parse_args()

    notes = ReleaseNotes()
    assert(len(args.repos) % 2 == 0)

    for i in range(0, len(args.repos), 2):
        name = args.repos[i]
        path = args.repos[i + 1]

        notes.addRepo(name, path)

    with open(args.output, 'wb') as fileObj:
        fileObj.write(notes.buildNotes(args.title))

    return  0

if __name__ == '__main__':
    sys.exit(main())

