class Requirement:
    """
    Information about a requirement in order to submit a change

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#requirement
    """

    def __init__(self, jsonObject):
        self._fallbackText = jsonObject.get("fallbackText", None)
        self._type = jsonObject.get("type", None)
        self._data = jsonObject.get("data", None)

    @property
    def fallbackText(self):
        """
        A human readable description of the requirement
        """
        return self._fallbackText

    @property
    def type(self):
        """
        Alphanumerical (plus hyphens or underscores) string to identify what the requirement is and why it was triggered.
        Can be seen as a class: requirements sharing the same type were created for a similar reason, and the data structure will follow one set of rules
        """
        return self._type

    @property
    def data(self):
        """
        (Optional) Additional key-value data linked to this requirement. This is used in templates to render rich status messages
        """
        return self._data
