class RevisionInfo:
    """
    The RevisionInfo entity contains information about a patch set. Not all fields are returned by default.
    Additional fields can be obtained by adding o parameters as described in Query Changes

    Source: https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#revision-info
    """

    def __init__(self, jsonObject):
        self.__ref = jsonObject.get("ref")

        self.__number = jsonObject.get("_number")

    @property
    def number(self):
        """
        The patch set number, or edit if the patch set is an edit
        """
        return self.__number

    @property
    def ref(self):
        """
        The Git reference for the patch set
        """

        return self.__ref
