class Manifest:
    """
    Build manifest which is an aggregate of projects, remotes and builds
    """

    def __init__(self, remotes, projects, builds, selectedBuild):
        """
        Constructor

        @param remotes See Manifest.remotes
        @param projects See Manifest.projects
        @param builds See Manifest.builds
        @param builds See Manifest.builds
        @param selectedBuild See Manifest.selectedBuild
        """

        self._remotes = remotes
        self._projects = projects
        self._builds = builds
        self._selectedBuild = selectedBuild

    @property
    def remotes(self):
        """
        Gerrit remote server list
        """
        return self._remotes

    @property
    def projects(self):
        """
        Projects list
        """
        return self._projects

    @property
    def builds(self):
        """
        Builds list
        """
        return self._builds

    @property
    def selectedBuild(self):
        """
        Selected build
        """
        return self._selectedBuild
