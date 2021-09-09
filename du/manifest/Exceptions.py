class ManifestParseError(Exception):
    """
    Generic manifest parser error
    """

    def __init__(self, message):
        """
        Constructor

        @param message Error message
        """
        Exception.__init__(self, message)


class ManifestFieldMissingError(Exception):
    """
    Error indicating a mandatory field is missing from the manifest
    """

    def __init__(self, message):
        """
        Constructor

        @param message Error message
        """
        Exception.__init__(self, message)


class ManifestLogicError(Exception):
    """
    Logic error which happened during manifest parsing
    """

    def __init__(self, message):
        """
        Constructor

        @param message Error message
        """
        Exception.__init__(self, message)
