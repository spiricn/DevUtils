class Build:
    """
    Manifest build instance, representing collection of final touches, tags, cherry picks etc.
    """

    def __init__(self, name, root, cherrypicks, checkouts, tags, pulls):
        """
        Constructor

        @param name See Build.name
        @param root See Build.root
        @param cherrypicks See Build.cherrypicks
        @param checkouts See Build.checkouts
        @param tags See Build.tags
        @param pulls See Build.pulls
        """

        self._name = name
        self._root = root
        self._cherrypicks = cherrypicks
        self._checkouts = checkouts
        self._tags = tags
        self._pulls = pulls

    @property
    def name(self):
        """
        Build name
        """
        return self._name

    @property
    def root(self):
        """
        Build root directory
        """
        return self._root

    @property
    def cherrypicks(self):
        """
        Map cherrypick lists (project name -> change list)
        """
        return self._cherrypicks

    @property
    def checkouts(self):
        """
        Map of checkouts (project name -> change)
        """
        return self._checkouts

    @property
    def tags(self):
        """
        Map of tags (project name -> tag name)
        """
        return self._tags

    @property
    def pulls(self):
        """
        Map of changes to be pulled (merged) on top of the base
        """
        return self._pulls
