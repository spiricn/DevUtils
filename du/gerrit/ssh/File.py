from enum import Enum


class File:
    """
    Information about a patch on a file

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#file
    """

    class Type(Enum):
        """
        The type of change
        """

        # The file is being created/introduced by this patch.
        ADDED = 0

        # The file already exists, and has updated content
        MODIFIED = 1

        # The file existed, but is being removed by this patch.
        DELETED = 2

        # The file is renamed.
        RENAMED = 3

        # The file is copied from another file
        COPIED = 4

        # Sufficient amount of content changed to claim the file was rewritten
        REWRITE = 5

    def __init__(self, jsonObject):
        self._file = jsonObject.get("file", None)
        self._fileOld = jsonObject.get("fileOld", None)
        self._type = jsonObject.get("type", None)
        if self._type:
            self._type = self.Type[self._type]

        self._insertions = jsonObject.get("insertions", None)
        self._deletions = jsonObject.get("deletions", None)

    @property
    def file(self):
        """
        The name of the file. If the file is renamed, the new name
        """
        return self._file

    @property
    def fileOld(self):
        """
        The old name of the file, if the file is renamed
        """
        return self._fileOld

    @property
    def type(self):
        """
        The type of change
        """
        return self._type

    @property
    def insertions(self):
        """
        number of insertions of this patch
        """
        return self._insertions

    @property
    def deletions(self):
        """
        number of deletions of this patch
        """
        return self._deletions
