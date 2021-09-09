import logging

logger = logging.getLogger(__name__.split(".")[-1])

# Indication that pygerrit2 is installed
pygerrit2Installed = False

try:
    from requests.exceptions import RequestException

    from pygerrit2 import GerritRestAPI
    from pygerrit2 import HTTPDigestAuthFromNetrc, HTTPBasicAuthFromNetrc
    from pygerrit2 import HTTPBasicAuth, HTTPDigestAuth

    pygerrit2Installed = True
except ImportError as e:
    logger.error("pygerrit2 not installed: %r" % str(e))


def getApi(username, password, server):
    """
    Get REST API

    @param username Username
    @param password Password
    @param server Server
    """

    if not pygerrit2Installed:
        raise RuntimeError(
            'pygerrit2 not installed, HTTP remotes not supported. To install run "pip3 install pygerrit2"'
        )

    return GerritRestAPI(url=server, auth=HTTPBasicAuth(username, password))
