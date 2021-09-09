class Dependency:
    """
    Information about a change or patchset dependency

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#dependency
    """

    def __init__(self, jsonObject):
        self._id = jsonObject.get("id", None)
        self._number = jsonObject.get("number", None)
        self._revision = jsonObject.get("revision", None)
        self._ref = jsonObject.get("ref", None)
        self._isCurrentPatchSet = jsonObject.get("isCurrentPatchSet", None)

    @property
    def id(self):
        """
        Change identifier
        """
        return self._id

    @property
    def number(self):
        """
        Change number
        """
        return self._number

    @property
    def revision(self):
        """
        Patchset revision
        """
        return self._revision

    @property
    def ref(self):
        """
        Ref name
        """
        return self._ref

    @property
    def isCurrentPatchSet(self):
        """
        If the revision is the current patchset of the change
        """
        return self._isCurrentPatchSet
