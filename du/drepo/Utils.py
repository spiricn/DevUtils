import logging

from du.gerrit.ssh.Connection import Connection

import du.gerrit.rest.Utils as GerritRestUtils
from du.gerrit.rest.change.ChangeEndpoint import ChangeEndpoint
from du.drepo.manifest.Remote import ProtocolType

from urllib.parse import urlparse
from urllib.parse import urlparse, urlunparse, quote

logger = logging.getLogger(__name__.split(".")[-1])


class Utils:
    """
    Collection of drepo utility functions
    """

    @staticmethod
    def createQueryConnection(remote, httpCredentials):
        """
        Create a query connection (HTTP or SSH) based on what's available in the given remote

        @param remote Remote
        @param httpCredentials A map of HTTP credentials
        """

        if remote.ssh:
            # Prioritize SSH if available
            return Connection(remote.ssh)

        elif remote.http:
            hostName = urlparse(remote.http).hostname

            username = None
            password = None

            # Check if we have the credentials for this HTTP server
            if hostName in httpCredentials:
                username = httpCredentials[hostName].username
                password = httpCredentials[hostName].password

            # Create an endpoint
            return ChangeEndpoint(
                GerritRestUtils.getApi(username, password, remote.http)
            )

        raise RuntimeError("Neither SSH nor HTTP defined")

    @staticmethod
    def injectPassword(url, httpCredentials):
        """
        Inject a HTTP username/password into a git URL if possible

        Has no effect on non HTTP URLS

        @param url Fetch URL
        @return URL injected with username/password (e.g. http://username:password@server.com)

        """
        url = urlparse(url)

        # Only do this for HTTP URLs for which we have credentials
        if (
            url.scheme.startswith(ProtocolType.HTTP.value)
            and url.hostname in httpCredentials
        ):
            credentials = httpCredentials[url.hostname]

            # If username is defined via URL, it should match the one from the credentials
            if url.username and url.username != credentials.username:
                raise RuntimeError(
                    "Username mismatch: %r != %r" % (url.username, credentials.username)
                )

            encodedNetloc = url.netloc

            # Username prefix (e.g. user@)
            usernamePrefix = credentials.username + "@"

            if not encodedNetloc.startswith(usernamePrefix):
                # Prepend username
                encodedNetloc = usernamePrefix + encodedNetloc

            tokens = encodedNetloc.split("@")

            # Append password (percent encoded)
            encodedNetloc = (
                tokens[0] + ":" + quote(credentials.password, safe="") + "@" + tokens[1]
            )

            # Replace the netloc with the one encoded with a password
            url = url._replace(netloc=encodedNetloc)

        return urlunparse(url)
