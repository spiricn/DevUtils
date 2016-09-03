from collections import namedtuple

from du.utils.Git import Change


Remote = namedtuple('Remote', 'name, fetch')
Project = namedtuple('Project', 'name, remote, path, branch, cherry_picks, url')

class Manifest:
    PROJECTS_VAR_NAME = 'projects'
    REMOTES_VAR_NAME = 'remotes'

    PROJECT_REMOTE_KEY = 'remote'
    PROJECT_PATH_KEY = 'path'
    PROJECT_BRANCH_KEY = 'branch'
    PROJECT_CHERRY_PICKS_KEY = 'cherry-picks'

    ROOT_VAR_NAME = 'root'

    def __init__(self, code):
        self._locals = {}

        exec(code, self._locals)

        # Parse remotes
        self._remotes = []
        for name, fetch in self._locals[self.REMOTES_VAR_NAME].iteritems():
            remote = Remote(name, fetch)
            self._remotes.append(remote)


        # Parse projects
        self._projects = []
        for name, desc in self._locals[self.PROJECTS_VAR_NAME].iteritems():
            remote = desc[self.PROJECT_REMOTE_KEY]
            path = desc[self.PROJECT_PATH_KEY]
            branch = desc[self.PROJECT_BRANCH_KEY]

            cherry_picks = desc[self.PROJECT_CHERRY_PICKS_KEY]

            tmp = []
            for i in cherry_picks:
                if isinstance(i, int):
                    change = Change(i, None)
                else:
                    if '/' in i:
                        number, ps = i.split('/')
                        change = Change(int(number), int(ps))
                    else:
                        change = Change(int(i), None)
                tmp.append(change)

            cherry_picks = tmp

            url = self.getRemote(remote).fetch + '/' + name


            proj = Project(name, remote, path, branch, cherry_picks, url)

            self._projects.append(proj)

        self._root = self._locals[self.ROOT_VAR_NAME]

    def getRemote(self, name):
        for i in self._remotes:
            if i.name == name:
                return i
        return None

    def getProject(self, name):
        for i in self._projects:
            if i.name == name:
                return i
        return None


    @property
    def projects(self):
        return self._projects

    @property
    def remotes(self):
        return self._remotes

    @property
    def root(self):
        return self._root

    @property
    def repoManifestXml(self):
        manifestXml = ''

        manifestXml += '<manifest>'

        manifestXml += '<default revision="refs/heads/master" sync-j="4" />'

        # Remotes
        for remote in self._remotes:
            manifestXml += '<remote name="%s" fetch="%s"/>' % (remote.name, remote.fetch)

        # Projects
        for proj in self._projects:
            manifestXml += '<project name="%s" remote="%s" path="%s" revision="refs/heads/%s"/>' % (proj.name, proj.remote, proj.path, proj.branch)

        manifestXml += '</manifest>'

        return manifestXml
