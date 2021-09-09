from enum import Enum


class QueryOption(Enum):
    """
    Additional fields can be obtained by adding o parameters, each option requires more database lookups
    and slows down the query response time to the client so they are generally disabled by default

    Source: https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#query-options
    """

    """
    A summary of each label required for submit, and approvers that have granted (or rejected) with that label
    """
    LABELS = "LABELS"

    """
    Detailed label information, including numeric values of all existing approvals, recognized label values,
    values permitted to be set by the current user, all reviewers by state, and reviewers that may be removed by the current user.
    """
    DETAILED_LABELS = "DETAILED_LABELS"

    """
    Describe the current revision (patch set) of the change, including the commit SHA-1 and URLs to fetch from
    """
    CURRENT_REVISION = "CURRENT_REVISION"

    """
    Describe all revisions, not just current
    """
    ALL_REVISIONS = "ALL_REVISIONS"

    """
    Include the commands field in the FetchInfo for revisions. Only valid when the CURRENT_REVISION or ALL_REVISIONS option is selected
    """
    DOWNLOAD_COMMANDS = "DOWNLOAD_COMMANDS"

    """
    Parse and output all header fields from the commit object, including message. Only valid when the CURRENT_REVISION or ALL_REVISIONS option is selected
    """
    CURRENT_COMMIT = "CURRENT_COMMIT"

    """
    Parse and output all header fields from the output revisions. If only CURRENT_REVISION was requested then only the current revision’s commit data will be output
    """
    ALL_COMMITS = "ALL_COMMITS"

    """
    List files modified by the commit and magic files, including basic line counts inserted/deleted per file.
    Only valid when the CURRENT_REVISION or ALL_REVISIONS option is selected
    """
    CURRENT_FILES = "CURRENT_FILES"

    """
    List files modified by the commit and magic files, including basic line counts inserted/deleted per file.
    If only the CURRENT_REVISION was requested then only that commit’s modified files will be output
    """
    ALL_FILES = "ALL_FILES"

    """
    Include _account_id, email and username fields when referencing accounts
    """
    DETAILED_ACCOUNTS = "DETAILED_ACCOUNTS"

    """
    Include updates to reviewers set as ReviewerUpdateInfo entities
    """
    REVIEWER_UPDATES = "REVIEWER_UPDATES"

    """
    Include messages associated with the change
    """
    MESSAGES = "MESSAGES"

    """
    Include information on available actions for the change and its current revision. Ignored if the caller is not authenticated
    """
    CURRENT_ACTIONS = "CURRENT_ACTIONS"

    """
    Include information on available change actions for the change. Ignored if the caller is not authenticated
    """
    CHANGE_ACTIONS = "CHANGE_ACTIONS"

    """
    Include the reviewed field
    """
    REVIEWED = "REVIEWED"

    """
    Skip the 'insertions' and 'deletions' field in ChangeInfo. For large trees, their computation may be expensive
    """
    SKIP_DIFFSTAT = "SKIP_DIFFSTAT"

    """
    Include the submittable field in ChangeInfo, which can be used to tell if the change is reviewed and ready for submit
    """
    SUBMITTABLE = "SUBMITTABLE"

    """
    Include the web_links field in CommitInfo, therefore only valid in combination with CURRENT_COMMIT or ALL_COMMITS
    """
    WEB_LINKS = "WEB_LINKS"

    """
    Include potential problems with the change
    """
    CHECK = "CHECK"

    """
    Include the full commit message with Gerrit-specific commit footers in the RevisionInfo
    """
    COMMIT_FOOTERS = "COMMIT_FOOTERS"

    """
    Include push certificate information in the RevisionInfo. Ignored if signed push is not enabled on the server
    """
    PUSH_CERTIFICATES = "PUSH_CERTIFICATES"

    """
    Include references to external tracking systems as TrackingIdInfo
    """
    TRACKING_IDS = "TRACKING_IDS"
