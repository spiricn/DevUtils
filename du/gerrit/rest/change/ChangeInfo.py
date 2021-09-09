from du.gerrit.rest.change.RevisionInfo import RevisionInfo
from du.gerrit.ChangeStatus import ChangeStatus


class ChangeInfo:

    """
    The ChangeInfo entity contains information about a change

    Source: https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#change-info
    """

    def __init__(self, jsonObject):
        self.__currentRevision = jsonObject.get("current_revision", None)

        self.__project = jsonObject.get("project")
        self.__branch = jsonObject.get("branch")
        self.__number = jsonObject.get("_number")
        self.__status = ChangeStatus[jsonObject.get("status")]

        self.__revisions = jsonObject.get("revisions", {})
        self.__revisions = {
            key: RevisionInfo(value) for key, value in self.__revisions.items()
        }

    @property
    def status(self):
        """
        The status of the change
        """
        return self.__status

    @property
    def number(self):
        """
        The legacy numeric ID of the change
        """
        return self.__number

    @property
    def project(self):
        """
        The name of the project
        """
        return self.__project

    @property
    def branch(self):
        """
        The name of the target branch.
        The refs/heads/ prefix is omitted
        """
        return self.__branch

    @property
    def revisions(self):
        """
        All patch sets of this change as a map that maps the commit ID of the patch set to a RevisionInfo entity.
        Only set if the current revision is requested (in which case it will only contain a key for the current revision) or if all revisions are requested
        """
        return self.__revisions

    @property
    def currentRevision(self):
        """
        The RevisionInfo of the current patch set of this change.
        Only set if the current revision is requested or if all revisions are requested
        """
        if self.__currentRevision not in self.__revisions:
            return None

        return self.__revisions[self.__currentRevision]
