class Account:
    """
    A user account

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#account
    """

    def __init__(self, jsonObject):
        self._name = jsonObject.get("name", None)
        self._email = jsonObject.get("email", None)
        self._username = jsonObject.get("username", None)

    @property
    def name(self):
        """
        User’s full name, if configured
        """
        return self._name

    @property
    def email(self):
        """
        User’s preferred email address
        """
        return self._email

    @property
    def username(self):
        """
        User’s username, if configured
        """
        return self._username
