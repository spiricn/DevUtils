from enum import Enum
from du.gerrit.ssh.Account import Account


class Label:
    """
    Information about a code review label for a change

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#label
    """

    class Status(Enum):
        """
        The status of the label.
        """

        # This label provides what is necessary for submission
        OK = 0

        # This label prevents the change from being submitted
        REJECT = 1

        # The label is required for submission, but has not been satisfied
        NEED = 2

        # The label may be set, but it’s neither necessary for submission nor does it block submission if set
        MAY = 3

        # The label is required for submission, but is impossible to complete. The likely cause is access has not been granted correctly by the project owner or site administrator
        IMPOSSIBLE = 4

    def __init__(self, jsonObject):
        self._label = jsonObject.get("label", None)
        self._status = jsonObject.get("status", None)
        if self._status:
            self._status = self.Status[self._status]

        self._by = jsonObject.get("by", None)
        if self._by:
            self._by = Account(self._by)

    @property
    def label(self):
        """
        The name of the label
        """
        return self._label

    @property
    def status(self):
        """
        The status of the label
        """
        return self._status

    @property
    def by(self):
        """
        The account that applied the label
        """
        return self._by
