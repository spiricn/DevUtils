from enum import Enum
from du.gerrit.ssh.Label import Label
from du.gerrit.ssh.Requirement import Requirement


class SubmitRecord:
    """
    Information about the submit status of a change

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#submitRecord
    """

    class Status(Enum):
        """
        Current submit status
        """

        # The change is ready for submission or already submitted
        OK = 0

        # The change is missing a required label
        NOT_READY = 1

        # An internal server error occurred preventing computation
        RULE_ERROR = 2

    def __init__(self, jsonObject):
        self._status = jsonObject.get("status", None)
        if self._status:
            self._status = self.Status[self._status]

        self._labels = jsonObject.get("labels", None)
        if self._labels:
            self._labels = [Label(i) for i in self._labels]

        self._requirements = jsonObject.get("requirements", None)
        if self._requirements:
            self._requirements = [Requirement(i) for i in self._requirements]
