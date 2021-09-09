class TrackingId:
    """
    A link to an issue tracking system

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#trackingid
    """

    def __init__(self, jsonObject):
        self._system = jsonObject.get("system", None)
        self._id = jsonObject.get("id", None)

    @property
    def system(self):
        """
        Name of the system. This comes straight from the gerrit.config file
        """
        return self._system

    @property
    def id(self):
        """
        Id number as scraped out of the commit message
        """
        return self._id
