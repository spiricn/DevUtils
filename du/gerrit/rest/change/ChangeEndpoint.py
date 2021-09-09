from du.gerrit.rest.change.QueryOption import QueryOption
from du.gerrit.rest.change.ChangeInfo import ChangeInfo

import logging
import pprint

logger = logging.getLogger(__name__.split(".")[-1])


class ChangeEndpoint:
    """
    Change related REST endpoints

    Source: https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html
    """

    ENDPOINT = "/changes/"

    def __init__(self, rest):
        """ """

        self.__rest = rest

    def query(self, *args, options=[], **kwargs):
        """
        Execute a query

        @param options A list of QueryOption values

        Source: https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#list-changes
        """

        params = self.ENDPOINT

        params += "?q="

        # Add all arguments
        for arg in args:
            params += str(arg) + "+"

        # Add all key/value pairs
        for key, value in kwargs.items():
            params += "%s:%s+" % (str(key), str(value))

        # Remove the last +
        if params.endswith("+"):
            params = params[:-1]

        # Add the options
        for opt in options:
            params += "&o=" + opt.name

        logger.debug("params: %r" % params)

        response = self.__rest.get(params)

        logger.debug("response:\n%s" % pprint.pformat(response, indent=2))

        # Execute the query & parse the results
        return [ChangeInfo(jsonObject) for jsonObject in response]
