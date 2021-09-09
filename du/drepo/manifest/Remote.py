import logging
from enum import Enum, unique

from urllib.parse import urlparse

logger = logging.getLogger(__name__.split(".")[-1])


@unique
class ProtocolType(Enum):
    """
    Type of the git protocol used
    """

    # HTTP
    HTTP = "http"

    # HTTPS
    HTTPS = "https"

    # SSH
    SSH = "ssh"


class Remote:
    """
    Gerrit remote
    """

    def __init__(self, name, fetch, ssh=None):

        """
        Constructor

        @param name Remote name
        @param fetch Fetch URL used for clones (may be HTTP or SSH)
        @param ssh SSH url used for SSH queries
        """

        self._name = name
        self._fetch = fetch
        self._ssh = ssh

    @property
    def fetch(self):
        """
        URL used for fetch
        """
        return self._fetch

    @property
    def ssh(self):
        """
        SSH Gerrit URL
        """
        if self._ssh:
            return self._ssh

        elif urlparse(self._fetch).scheme.startswith(ProtocolType.SSH.value):
            return self._fetch

    @property
    def http(self):
        """
        HTTP Gerrit URL
        """
        parsedFetch = urlparse(self._fetch)

        if parsedFetch.scheme.startswith(ProtocolType.HTTP.value):
            return self._fetch

        return "%s://%s" % (ProtocolType.HTTPS.value, parsedFetch.hostname)

    @property
    def name(self):
        """
        Remote name
        """
        return self._name
