from collections import namedtuple


class TagInfo(
    namedtuple(
        "TagInfo",
        "headHash, refHash, headTagName, matchedTagName, cleanMatchedTagName",
    )
):
    """
    Project tag information

    @param headHash Project shortened head hash
    @parma refHash Tag reference hash
    @param headTagName Head tag name (if tagged, None otherwise)
    @param matchedTagName Matched tag name, if pattern was provided
    @param cleanMatchedTagname Last clean matched tag name, if pattern was provided
    """

    pass


class GerritChangeInfo(
    namedtuple(
        "GerritChangeInfo", "number, patchSetNumber, status, currentPatchSetNumber"
    )
):
    """
    Gerrit information

    @param number Change number
    @param patchSetNumber(optional) Remote patchset number, if any was matched (None otherwise)
    @param currentPatchSetNumber Latest change patchset number
    """

    pass


class CommitInfo(
    namedtuple("CommitInfo", "title, hash, shortHash, author, gerritChangeInfo")
):
    """
    Commit information

    @param title Commit title
    @param hash Commit hash
    @param shortHash Commit abbreivated hash
    @param author Commit author name
    @param gerritChangeInfo Optional gerrit change information (if found)
    """

    pass


class ProjectInfo(namedtuple("ProjectInfo", "manifestProject, tagInfo, commitsInfo")):
    """
    Project information

    @param manifestProject Manifest reference
    @param tagInfo Tag information
    @param commitsInfo List of analyzed commits
    """

    pass


class ReportInfo(namedtuple("ReportInfo", "manifest, projects, hostName, userName")):
    """
    Report input information

    @param manifest DRepo manifest
    @param project List of project infos
    @param hostName Host name the build is located on
    @param userName Name of the user who generated the report
    """

    pass
