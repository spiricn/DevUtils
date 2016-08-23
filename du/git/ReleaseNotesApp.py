import argparse
from collections import namedtuple
import logging
import sys

from du.git.RepoNotes import RepoNotes


Repo = namedtuple('Repo', 'name, path, url')

class ReleaseNotes:
    def __init__(self):
        self._repos = []

    def addRepo(self, name, url, path):
        self._repos.append(Repo(name, path, url))

    def buildNotes(self, title):
        res = title + '\n\n'

        for repo in self._repos:
            notes = RepoNotes(repo.path, repo.url)

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
    assert(len(args.repos) % 3 == 0)

    for i in range(0, len(args.repos), 3):
        name = args.repos[i]
        url = args.repos[i + 1]
        path = args.repos[i + 2]

        notes.addRepo(name, url, path)

    with open(args.output, 'wb') as fileObj:
        fileObj.write(notes.buildNotes(args.title))

    return  0

if __name__ == '__main__':
    sys.exit(main())

