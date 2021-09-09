from du.gerrit.ssh.Account import Account


class Message:
    """
    Comment added on a change by a reviewer

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#message
    """

    def __init__(self, jsonObject):
        self._timestamp = jsonObject.get("timestamp", None)
        self._reviewer = jsonObject.get("reviewer", None)
        if self._reviewer:
            self._reviewer = Account(self._reviewer)

        self._message = jsonObject.get("message", None)

    @property
    def timestamp(self):
        """
        Time in seconds since the UNIX epoch when this comment was added
        """
        return self._timestamp

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
