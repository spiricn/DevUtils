from du.gerrit.ssh.Account import Account
from du.gerrit.ssh.Approval import Approval
from du.gerrit.ssh.File import File
from du.gerrit.ssh.PatchSetComment import PatchSetComment


class PatchSet:
    """
    Refers to a specific patchset within a change

    Schema described here
    https://gerrit-review.googlesource.com/Documentation/json.html#patchSet
    """

    def __init__(self, jsonObject):
        self._number = jsonObject.get("number", None)
        self._revision = jsonObject.get("revision", None)
        self._parents = jsonObject.get("parents", None)
        self._ref = jsonObject.get("ref", None)
        self._uploader = jsonObject.get("uploader", None)
        if self._uploader:
            self._uploader = Account(self._uploader)

        self._author = jsonObject.get("author", None)
        if self._author:
            self._author = Account(self._author)

        self._createdOn = jsonObject.get("createdOn", None)
        self._kind = jsonObject.get("kind", None)
        self._approvals = jsonObject.get("approvals", None)
        if self._approvals:
            self._approvals = [Approval(i) for i in self._approvals]

        self._comments = jsonObject.get("comments", None)
        if self._comments:
            self._comments = [PatchSetComment(i) for i in self._comments]

        self._files = jsonObject.get("files", None)
        if self._files:
            self._files = [File(i) for i in self._files]

        self._sizeInsertions = jsonObject.get("sizeInsertions", None)
        self._sizeDeletions = jsonObject.get("sizeDeletions", None)

    @property
    def number(self):
        """
        The patchset number
        """
        return self._number

    @property
    def revision(self):
        """
        Git commit for this patchset
        """
        return self._revision

    @property
    def parents(self):
        """
        List of parent revisions
        """
        return self._

    @property
    def ref(self):
        """
        Git reference pointing at the revision. This reference is available through the Gerrit Code Review server’s Git interface for the containing change
        """
        return self._ref

    @property
    def uploader(self):
        """
        Uploader of the patch set in account attribute
        """
        return self._uploader

    @property
    def author(self):
        """
        Author of this patchset in account attribute
        """
        return self._author

    @property
    def createdOn(self):
        """
        Time in seconds since the UNIX epoch when this patchset was created
        """
        return self._createdOn

    @property
    def kind(self):
        """
        Kind of change uploaded.

        REWORK
        Nontrivial content changes.

        TRIVIAL_REBASE
        Conflict-free merge between the new parent and the prior patch set.

        MERGE_FIRST_PARENT_UPDATE
        Conflict-free change of first (left) parent of a merge commit.

        NO_CODE_CHANGE
        No code changed; same tree and same parent tree.

        NO_CHANGE
        No changes; same commit message, same tree and same parent tree
        """
        return self._kind

    @property
    def approvals(self):
        """
        The approval attribute granted
        """
        return self._approvals

    @property
    def comments(self):
        """
        All comments for this patchset in patchsetComment attributes
        """
        return self._comments

    @property
    def files(self):
        """
        All changed files in this patchset in file attributes
        """
        return self._files

    @property
    def sizeInsertions(self):
        """
        Size information of insertions of this patchset
        """
        return self._sizeInsertions

    @property
    def sizeDeletions(self):
        """
        Size information of deletions of this patchset
        """
        return self._sizeDeletions
