from du.gerrit.ssh.Account import Account


class PatchSetComment:
    """
    Comment added on a patchset by a reviewer

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#patchsetcomment
    """

    def __init__(self, jsonObject):
        self._file = jsonObject.get("file", None)
        self._line = jsonObject.get("line", None)
        self._reviewer = jsonObject.get("reviewer", None)
        if self._reviewer:
            self._reviewer = Account(self._reviewer)

        self._message = jsonObject.get("message", None)

    @property
    def file(self):
        """
        The name of the file on which the comment was added
        """
        return self._file

    @property
    def line(self):
        """
        The line number at which the comment was added
        """
        return self._line

    @property
    def reviewer(self):
        """
        The account that added the comment
        """
        return self._reviewer

    @property
    def message(self):
        """
        The comment text
        """
        return self._message
