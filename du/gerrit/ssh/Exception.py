class QueryFailedException(Exception):
    """
    Exception thrown when a query fails
    """

    def __init__(self, query, message):
        """
        Constructor

        @Param query Query c ommand
        @param message Detailed failure message
        """

        Exception.__init__(self, message)

        self.query = query
