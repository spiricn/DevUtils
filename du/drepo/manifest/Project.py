class Project:
    """
    Manifest project entry containing path, branches, etc.

    TODO: Branch should be moved to the Build class
    """

    def __init__(self, name, remote, path, branch, opts):
        """
        Constructor

        @param name See Project.name
        @param remote See Project.remote
        @param path See Project.path
        @param branch See Project.branch
        @param opts See Project.opts
        """

        self._name = name
        self._remote = remote
        self._path = path
        self._branch = branch
        self._opts = opts

    @property
    def name(self):
        """
        Project name
        """
        return self._name

    @property
    def remote(self):
        """
        Project remote
        """
        return self._remote

    @property
    def path(self):
        """
        Path relative to the build root
        """
        return self._path

    @property
    def branch(self):
        """
        Project branch
        """
        return self._branch

    @property
    def remoteUrl(self):
        """
        Remote URL
        """
        return self._remote.fetch + "/" + self._name

    @property
    def opts(self):
        """
        Project options list
        """
        return self._opts
