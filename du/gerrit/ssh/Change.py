from du.gerrit.ssh.Account import Account
from du.gerrit.ssh.Message import Message
from du.gerrit.ssh.PatchSet import PatchSet
from du.gerrit.ssh.Dependency import Dependency
from du.gerrit.ssh.SubmitRecord import SubmitRecord
from du.gerrit.ssh.TrackingId import TrackingId
from du.gerrit.ChangeStatus import ChangeStatus

from enum import Enum


class Change:
    """
    The Gerrit change being reviewed, or that was already reviewed

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#change
    """

    def __init__(self, jsonObject):
        self._project = jsonObject.get("project", None)
        self._branch = jsonObject.get("branch", None)
        self._topic = jsonObject.get("topic", None)
        self._id = jsonObject.get("id", None)
        self._number = jsonObject.get("number", None)
        self._subject = jsonObject.get("subject", None)
        self._owner = jsonObject.get("owner", None)
        if self._owner:
            self._owner = Account(self._owner)

        self._url = jsonObject.get("url", None)
        self._commitMessage = jsonObject.get("commitMessage", None)
        self._hashtags = jsonObject.get("hashtags", [])
        self._createdOn = jsonObject.get("createdOn", None)
        self._lastUpdated = jsonObject.get("lastUpdated", None)
        self._open = jsonObject.get("open", None)
        self._status = jsonObject.get("status", None)
        if self._status:
            self._status = ChangeStatus[self._status]

        self._private = jsonObject.get("private", None)
        self._wip = jsonObject.get("wip", None)
        self._comments = jsonObject.get("comments", None)
        if self._comments:
            self._comments = [Message(i) for i in self._comments]

        self._trackingIds = jsonObject.get("trackingIds", None)
        if self._trackingIds:
            self._trackingIds = [TrackingId(i) for i in self._trackingIds]

        self._currentPatchSet = jsonObject.get("currentPatchSet", None)
        if self._currentPatchSet:
            self._currentPatchSet = PatchSet(self._currentPatchSet)

        self._patchSets = jsonObject.get("patchSets", None)
        if self._patchSets:
            self._patchSets = [PatchSet(i) for i in self._patchSets]

        self._dependsOn = jsonObject.get("dependsOn", None)
        if self._dependsOn:
            self._dependsOn = Dependency(self._dependsOn)

        self._neededBy = jsonObject.get("neededBy", None)
        if self._neededBy:
            self._neededBy = Dependency(self._neededBy)

        self._submitRecords = jsonObject.get("submitRecords", None)
        if self._submitRecords:
            self._submitRecords = [SubmitRecord(i) for i in self._submitRecords]

        self._allReviewers = jsonObject.get("allReviewers", None)
        if self._allReviewers:
            self._allReviewers = [Account(reviewer) for reviewer in self._allReviewers]

    @property
    def project(self):
        """
        Project path in Gerrit
        """
        return self._project

    @property
    def branch(self):
        """
        Branch name within project
        """
        return self._branch

    @property
    def topic(self):
        """
        Topic name specified by the uploader for this change series
        """
        return self._topic

    @property
    def id(self):
        """
        Change identifier, as scraped out of the Change-Id field in the commit message, or as assigned by the server if it was missing
        """
        return self._id

    @property
    def number(self):
        """
        Change number (deprecated).
        """
        return self._number

    @property
    def subject(self):
        """
        Description of change
        """
        return self._subject

    @property
    def owner(self):
        """
        Owner in account attribute
        """
        return self._owner

    @property
    def url(self):
        """
        Canonical URL to reach this change
        """
        return self._url

    @property
    def commitMessage(self):
        """
        The full commit message for the change’s current patch set
        """
        return self._commitMessage

    @property
    def hashtags(self):
        """
        List of hashtags associated with this change
        """
        return self._hashtags

    @property
    def createdOn(self):
        """
        Time in seconds since the UNIX epoch when this change was created
        """
        return self._createdOn

    @property
    def lastUpdated(self):
        """
        Time in seconds since the UNIX epoch when this change was last updated
        """
        return self._lastUpdated

    @property
    def open(self):
        """
        Boolean indicating if the change is still open for review
        """
        return self._open

    @property
    def status(self):
        """
        Current state of this change
        """
        return self._status

    @property
    def private(self):
        """
        Boolean indicating if the change is private
        """
        return self._private

    @property
    def wip(self):
        """
        Boolean indicating if the change is work in progress
        """
        return self._wip

    @property
    def comments(self):
        """
        All inline/file comments for this change in message attributes
        """
        return self._

    @property
    def trackingIds(self):
        """
        Issue tracking system links in trackingid attributes, scraped out of the commit message based on the server’s trackingid sections
        """
        return self._trackingIds

    @property
    def currentPatchSet(self):
        """
        Current patchSet attribute
        """
        return self._currentPatchSet

    @property
    def currentRevision(self):
        """
        Alias for .currentPatchSet
        """
        return self.currentPatchSet

    @property
    def patchSets(self):
        """
        All patchSet attributes for this change
        """
        return self._patchSets

    @property
    def dependsOn(self):
        """
        List of changes that this change depends on in dependency attributes
        """
        return self._dependsOn

    @property
    def neededBy(self):
        """
        List of changes that depend on this change in dependency attributes
        """
        return self._neededBy

    @property
    def submitRecords(self):
        """
        The submitRecord attribute contains information about whether this change has been or can be submitted
        """
        return self._

    @property
    def allReviewers(self):
        """
        List of all reviewers in account attribute which are added to a change
        """
        return self._allReviewers

    def __str__(self):
        return "{Change: number=%s, project=%s, branch=%s, id=%s}" % (
            str(self.number),
            str(self.project),
            str(self.branch),
            str(self.id),
        )
