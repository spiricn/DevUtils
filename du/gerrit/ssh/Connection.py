import json
from du.gerrit.ssh.Change import Change
from du.gerrit.ssh.Exception import QueryFailedException
from du.utils.ShellCommand import ShellCommand

from urllib.parse import urlparse


class Connection:

    # Include information about the current patch set in the results
    # Note that the information will only be included when the current patch set is visible to the caller.
    QUERY_ARG_CURRENT_PATCHSET = "--current-patch-set"

    # Include information about all patch sets visible to the caller.
    # If combined with the --current-patch-set flag then the current patch set information will be output twice, once in each field.
    QUERY_ARG_PATCHSETS = "--patch-sets"

    # Query response type attribute key
    QUERY_KEY_TYPE = "type"

    # Query response message attribute key
    QUERY_KEY_MESSAGE = "message"

    # Error response type
    QUERY_TYPE_ERROR = "error"

    # Stats response type
    QUERY_TYPE_STATS = "stats"

    # Number of connection retries
    NUM_CONNECTION_RETRIES = 3

    # Time range for random connection retries
    RETRY_CONNECTION_RANGE_SEC = (0.5, 3)

    def __init__(self, server):
        """
        Constructor

        @param server Server address
        """

        self._server = server

    def query(self, *args, **kwargs):
        """
        Preform a gerrit query, passing on all arguments

        @return Parsed list of JSON objects
        """

        query = ""

        # Additional query arguments
        for arg in args:
            query += str(arg) + " "

        # Key arguments
        for key, val in kwargs.items():
            query += "%s:%s " % (str(key), str(val))

        parsedUrl = urlparse(self._server)

        rawCommand = ["ssh"]

        if parsedUrl.port:
            rawCommand += ["-p", str(parsedUrl.port)]

        hostName = parsedUrl.hostname

        # Prepend username if necessary
        if parsedUrl.username:
            hostName = parsedUrl.username + "@" + parsedUrl.hostname

        rawCommand += [hostName, "gerrit", "query", "--format=JSON", query]

        cmd = ShellCommand.execute(
            rawCommand,
            numRetries=self.NUM_CONNECTION_RETRIES,
            randomRetry=True,
            retryRange=self.RETRY_CONNECTION_RANGE_SEC,
        )

        # SSH responds with a list of JSON objects, so parse each one
        parsedResponse = [json.loads(line) for line in cmd.stdoutStr.splitlines()]

        # The last one contains a result, describing the status of the query
        result = parsedResponse.pop()

        # Check if there was an error
        responseType = result[self.QUERY_KEY_TYPE]

        if responseType == self.QUERY_TYPE_STATS:
            # All good, return response objects
            return [Change(i) for i in parsedResponse]

        elif responseType == self.QUERY_TYPE_ERROR:
            # Query failed
            raise QueryFailedException(
                " ".join(rawCommand), result[self.QUERY_KEY_MESSAGE]
            )

        else:
            # Sanity check
            raise RuntimeError("Unexpected query response type %r" % responseType)
