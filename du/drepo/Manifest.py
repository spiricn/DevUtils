import logging

from du.utils.Git import Change


class Remote:
    PROTOCOL_HTTPS, \
    PROTOCOL_SSH \
 = range(2)

    def __init__(self, name, fetch):
        self.name = name
        self.fetch = fetch

        if not fetch.startswith('ssh://'):
            raise RuntimeError('Unsupported protocol: %r' % fetch)

        self.protocol = self.PROTOCOL_SSH

        self.username = fetch.split('ssh://')[1].split('@')[0]

        self.server = fetch.split('@')[1].split(':')[0]

        self.port = int(fetch.split(':')[-1])



class Project:
    def __init__(self, name, remote, path, branch, url, opts):
        self.name = name
        self.remote = remote
        self.path = path
        self.branch = branch
        self.url = url
        self.opts = opts

class Build:
    def __init__(self, name, root, cherrypicks, finalTouches):
        self.name = name
        self.root = root
        self.cherrypicks = cherrypicks
        self.finalTouches = finalTouches


OPT_CLEAN, OPT_RESET = range(2)

PROJECTS_VAR_NAME = 'projects'
REMOTES_VAR_NAME = 'remotes'
PROJECT_REMOTE_KEY = 'remote'
PROJECT_PATH_KEY = 'path'
PROJECT_BRANCH_KEY = 'branch'
CHERRY_PICKS_KEY = 'cherrypicks'
FINAL_TOUCHES_KEY = 'final_touches'
PROJECT_OPTS_KEY = 'opts'
BUILDS_VAR_NAME = 'builds'
BUILD_VAR_NAME = 'build'
ROOT_VAR_NAME = 'root'

logger = logging.getLogger(__name__.split('.')[-1])

class Manifest:
    def __init__(self, code):
        self._locals = {
            'OPT_CLEAN' : OPT_CLEAN,
            'OPT_RESET' : OPT_RESET,
        }

        exec(code, self._locals)

        self._builds = []

        self._build = None

        buildName = self.get(BUILD_VAR_NAME)

        for name, desc in self.get(BUILDS_VAR_NAME).items():
            root = desc[ROOT_VAR_NAME]

            # Parse cherry picks
            cherrypicks = desc[CHERRY_PICKS_KEY] if CHERRY_PICKS_KEY in desc else {}
            for proj, changes in cherrypicks.items():
                tmp = []

                for i in changes:
                    tmp.append(Change(i))

                cherrypicks[proj] = tmp


            # Parse final touches
            finalTouches = desc[FINAL_TOUCHES_KEY] if FINAL_TOUCHES_KEY in desc else {}
            for proj, ft in finalTouches.items():
                finalTouches[proj] = Change(ft)


            build = Build(name, root, cherrypicks, finalTouches)

            if name == buildName:
                self._build = build

            logger.debug('Adding build: %r' % str(build))

            self._builds.append(build)

        if not self._build:
            raise RuntimeError('Could not find active build %r in %s var' % (buildName, BUILDS_VAR_NAME))

        logger.debug('Selecting build: %r' % str(self._build))

        # Parse remotes
        self._remotes = []
        for name, fetch in self.get(REMOTES_VAR_NAME).items():
            remote = Remote(name, fetch)
            self._remotes.append(remote)
            logger.debug('Adding remote: %r' % str(remote))

        # Parse projects
        self._projects = []
        for name, desc in self.get(PROJECTS_VAR_NAME).items():
            remoteName = desc[PROJECT_REMOTE_KEY]

            remote = None
            for i in self._remotes:
                if i.name == remoteName:
                    remote = i
            if not remote:
                raise RuntimeError('Invalid remote name %r' % remoteName)

            path = desc[PROJECT_PATH_KEY]
            branch = desc[PROJECT_BRANCH_KEY]

            url = remote.fetch + '/' + name

            opts = desc[PROJECT_OPTS_KEY] if PROJECT_OPTS_KEY in desc else []

            proj = Project(name, remote, path, branch, url, opts)

            logger.debug('Adding project: %r' % str(proj))
            self._projects.append(proj)

    def get(self, name):
        if name in self._locals:
            return self._locals[name]
        else:
            raise RuntimeError('Required var %r missing from manifest' % name)

    def getCherrypicks(self, proj):
        return self._build.cherrypicks[proj.name]

    def findProjectsWithOpt(self, opt):
        projects = []
        for proj in self._projects:
            if opt in proj.opts:
                projects.append(proj)
        return projects

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
    def builds(self):
        return self._builds

    @property
    def remotes(self):
        return self._remotes

    @property
    def root(self):
        return self._build.root

    @property
    def build(self):
        return self._build

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
