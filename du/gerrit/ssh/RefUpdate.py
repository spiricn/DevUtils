class RefUpdate:
    """
    Information about a ref that was updated

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#refUpdate
    """

    def __init__(self, jsonObject):
        self._oldRev = jsonObject.get("oldRev", None)
        self._newRev = jsonObject.get("newRev", None)
        self._refName = jsonObject.get("refName", None)
        self._project = jsonObject.get("project", None)

    @property
    def oldRev(self):
        """
        The old value of the ref, prior to the update
        """
        return self._oldRev

    @property
    def newRev(self):
        """
        The new value the ref was updated to. Zero value (0000000000000000000000000000000000000000) indicates that the ref was deleted
        """
        return self._newRev

    @property
    def refName(self):
        """
        Full ref name within project
        """
        return self._refName

    @property
    def project(self):
        """
        Project path in Gerrit
        """
        return self._project
