import re


class Utils:
    """
    Collection of gerrit utility functions
    """

    # Pattern which matches a Gerrit change ID
    CHANGE_ID_VALUE_PATTERN = r"I[0-9a-fA-F]{40}"

    # Regex which matches a Gerrit change ID
    CHANGE_ID_VALUE_REGEX = re.compile(r"^%s$" % CHANGE_ID_VALUE_PATTERN)

    # Regex which matches a Gerrit change ID git message
    CHANGE_ID_MESSAGE_REGEX = re.compile(r"Change-Id: (%s)" % CHANGE_ID_VALUE_PATTERN)

    @staticmethod
    def isValidChangeId(changeId):
        """
        Checks if a given string is a valid gerrit change ID

        @param changeId Change ID string
        @return True if valid
        """

        return Utils.CHANGE_ID_VALUE_REGEX.match(changeId) != None

    @staticmethod
    def extractChangeId(commitMessage):
        """
        Extract change ID from a git commit message

        @param commitMessage Git commit message

        @return change ID, or None
        """
        for line in commitMessage.splitlines():
            match = Utils.CHANGE_ID_MESSAGE_REGEX.match(line)
            if match:
                return match.group(1)

        return None
