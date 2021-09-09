from du.gerrit.ssh.Account import Account


class Approval:
    """
    Records the code review approval granted to a patch set

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#approval
    """

    def __init__(self, jsonObject):
        self._type = jsonObject.get("type", None)
        self._description = jsonObject.get("description", None)
        self._value = jsonObject.get("value", None)
        self._oldValue = jsonObject.get("oldValue", None)
        self._grantedOn = jsonObject.get("grantedOn", None)
        self._by = jsonObject.get("by", None)
        if self._by:
            self._by = Account(self._by)

    @property
    def type(self):
        """
        Internal name of the approval given
        """
        return self._type

    @property
    def description(self):
        """
        Human readable category of the approval
        """
        return self._description

    @property
    def value(self):
        """
        Value assigned by the approval, usually a numerical score
        """
        return self._value

    @property
    def oldValue(self):
        """
        The previous approval score, only present if the value changed as a result of this event
        """
        return self._oldValue

    @property
    def grantedOn(self):
        """
        Time in seconds since the UNIX epoch when this approval was added or last updated
        """
        return self._grantedOn

    @property
    def by(self):
        """
        Reviewer of the patch set in account attribute
        """
        return self._by
