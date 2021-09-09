import du

from du.gerrit.ChangeStatus import ChangeStatus
from urllib.parse import urlparse

# Base64-encoded PNG favicon
FAVICON = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABuklEQVQ4T5WTPW/TYBSFn+NEqFKL2FkYgSCU2gMTMCGByIRw0o8/0AmEVAl1zFgJEBIsMLCmUWzEVEQlJj4GFjsRbcrKwD/go6DaF9klaUyaCN7R5/V577n3uWLKscDbQpj86Nqka5pqEHqfM11+dGqqgRki9NZx0je62d0cXLbQvU0CWogfDb89n6+ROpfxozVl1WWCPTt9nBNzXzBmsOSCGt2uddwKji7mP6b2To24bxtVl3L5A2KP9MdJNfpfhxEs8C4hrUFyB9QELYH+6GaYtUnSJuXyQ8zWVY/e5vH+zmaB20LO0tGZ0w358fKoVjCwVvUcx0ofD18eszdIzsvv7QwUWei9wjgLdh/TTxw9nTYZsBWwGUyriN3MYAs4A/YAtAf/aIBWMT4VIxx0fvu/IoylDN0WTGiiWVv1qNDgYgVh1WWfb5ScJtJiYYxYm/1sjMzK78XDJg4J68zXUOkF2GvVo+sFkH4l77Xc27HAewm6gpPcGBA7CtI9pBXMagNILHBv5bDU48c5sQewbYI9kR/dLYCU70NQmc3wPNyF8WWyTmWOfv+7mqRHkjja1HzEllUQXZ3Exm/WErw7rZ1BDwAAAABJRU5ErkJggg=="


class HtmlGenerator:
    """
    Human readable HTML report generator
    """

    # Report title
    DEFAULT_TITLE = "Report"

    @staticmethod
    def generate(reportInfo):
        result = """

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

"""
        # Title
        result += "<title>%s</title>" % HtmlGenerator.DEFAULT_TITLE

        # Favicon
        result += (
            """
<link id="favicon" rel="shortcut icon" type="image/png" href="data:image/png;base64,%s">
"""
            % FAVICON
        )

        # CSS
        result += """
<style>

/* Global styling */
body {
    font-family: "Courier New", Courier, "Lucida Sans Typewriter", "Lucida Typewriter", monospace;
    font-style: normal;
    font-variant: normal;
}

/* Project branch */
.branch {
    background-color:#9AD2CB;
    font-size: small;
}

/* Project tag hash */
.commit {
    background-color:#FEFFBE;
    font-size: small;
}

/* Project tag name */
.tag {
    background-color:#EBD494;
    font-size: small;
}

/* Commits table heading */
.changes_heading {
    font-size: small;
    background-color: #E5E5E5;
}

/* Emphasis of a word */
.emphasis {
    font-style: italic;
}

/* Cherrypicked changes */
.change_cherrypicked {
    font-size: small;
    background-color: #FFF486;
}

/* Merged changes */
.change_merged {
    font-size: small;
    color: #206696;
}

/* Pulled changes */
.change_pulled {
    font-size: small;
    background-color: #BEE599;
}

/* Local changes, not on Gerrit */
.change_local {
    font-size: small;
    background-color: #FFBC86;
}

/* Legend table */
.legend {
    border: 1px solid black;
}

/* URL style */
a {
  color: #206696;
}

/* Generic table value */
.generic_table_value {
    font-size: small;
    font-style: oblique;
    padding-left: 50px;
}

</style>
"""
        result += """
</head>

<body>
"""

        result += (
            '<hr/><h3> DRepo <span style="font-size:x-small; color: gray; vertical-align: middle">v%s</span> </h3>\n'
            % du.__version_name__
        )

        result += "<hr/> <table>"
        result += (
            '<tr><td>Build name </td> <td class="generic_table_value"> %s</td></tr>\n'
            % reportInfo.manifest.selectedBuild.name
        )
        result += (
            '<tr><td>Build path </td> <td class="generic_table_value"> %s</td></tr>\n'
            % reportInfo.manifest.selectedBuild.root
        )
        result += (
            '<tr><td>Node</td> <td class="generic_table_value"> %s@%s</td></tr>\n'
            % (
                reportInfo.userName,
                reportInfo.hostName,
            )
        )

        result += "</table> <hr/>\n"

        # Generate a list of all the projects (with anchor links)
        result += "<table>\n"

        result += '<tr class="changes_heading"> <th>Project</th> <th>Path</th> </tr>\n'

        for idx, proj in enumerate(reportInfo.projects):

            result += "<tr>\n"

            # Name
            result += '<td><a href="#%s">%s</a></td>\n' % (
                proj.manifestProject.name,
                proj.manifestProject.name,
            )

            # Path
            result += (
                '<td class="generic_table_value">/%s</td>\n' % proj.manifestProject.path
            )

            result += "</tr>\n"

        result += "</table>\n"

        # Generate information per-project
        for proj in reportInfo.projects:
            result += HtmlGenerator.__generateProjectHtml(proj)

        result += "<hr/><br/><br/>"

        # Table legend
        result += """
<hr/>

<table class="legend">
<tr><th> Legend </th></tr>
<tr class="change_pulled"> <td> Change was found on Gerrit, was not merged and the hash matches a remote patchet (most likely checked-out, or fast-forward pulled)</td> </tr>
<tr class="change_cherrypicked"> <td> Change was found on Gerrit, was not merged and the commit hash wasn't matched with anything on remote (most likely cherrypicked) </td> </tr>
<tr class="change_local"> <td> Change was not found on Gerrit (possibly missing the 'Change-Id' attribute in the message)</td> </tr>
<tr class="change_merged"> <td> Change was found on Gerrit and it was merged </td> </tr>
</table>
"""

        result += "</body></html>"

        return result

    @staticmethod
    def __generateProjectHtml(projectInfo):
        """
        Generate project specific HTML

        @param projectInfo Project info
        """

        result = ""

        remoteHttpUrl = projectInfo.manifestProject.remote.http

        result += "<hr/><br/>"

        gerritUrl = (
            "https://" + urlparse(projectInfo.manifestProject.remote.http).netloc
        )

        # Gitweb URL for this project
        projectGitwebUrl = gerritUrl + "/gitweb?p=%s.git;" % (
            projectInfo.manifestProject.name,
        )

        result += '<h3 id="%s">' % projectInfo.manifestProject.name
        result += '<a href="%s" target="_blank">%s</a>' % (
            projectGitwebUrl,
            projectInfo.manifestProject.name,
        )

        result += "("

        # Gitweb URL for this branch
        branchGitWebUrl = projectGitwebUrl + "a=shortlog;h=refs%%2Fheads%%2F%s" % (
            projectInfo.manifestProject.branch,
        )

        # Branch
        result += (
            '<span class="branch"> <span class="emphasis">branch</span>: <a href="%s" target="_blank">%s</a></span>\n'
            % (branchGitWebUrl, projectInfo.manifestProject.branch)
        )

        # Tag name
        if projectInfo.tagInfo.headTagName:
            tagGitwebUrl = projectGitwebUrl + "a=tag;h=" + projectInfo.tagInfo.refHash

            result += (
                " <span class='tag'><span class='emphasis'>tag</span>: <a href=\"%s\" target=\"_blank\">%s</a></span>\n"
                % (tagGitwebUrl, projectInfo.tagInfo.headTagName)
            )

        # Head
        headGitWebUrl = projectGitwebUrl + "a=commit;h=" + projectInfo.tagInfo.headHash
        result += (
            "  <span class='commit'><span class='emphasis'>head</span>: <a href=\"%s\" target=\"_blank\">%s</a></span>\n"
            % (headGitWebUrl, projectInfo.tagInfo.headHash)
        )

        result += ")"

        result += "</h3>"

        result += """
<table>
<tr class="changes_heading"> <th>Subject</th> <th style="padding-left:30px; padding-right:30px">Commit</th><th style="padding-left:30px; padding-right:30px"> Change </th> <th>Author</th> </tr>
"""

        # Generate a list of analyzed commits
        for commit in projectInfo.commitsInfo:
            result += HtmlGenerator.__generateCommitHtml(
                gerritUrl, projectGitwebUrl, projectInfo, commit
            )

        result += "</table><br/>"

        return result

    @staticmethod
    def __generateCommitHtml(gerritUrl, gitwebUrl, projectInfo, commitInfo):
        """
        Generate commit specific HTML

        @param gerritUrl Gerrit HTTP URL
        @param gitwebUrl Gitweb HTTP URL
        @param projectInfo Parent project info
        @param commitInfo Commit info
        """

        result = ""

        # Default color (for commits )
        changeStyle = None

        gerritChangeNumberText = ""
        commitGerritUrl = None

        # Commit on gerrit ?
        if commitInfo.gerritChangeInfo:
            gerritChangeNumberText = str(commitInfo.gerritChangeInfo.number)

            commitGerritUrl = gerritUrl + "/c/%d" % commitInfo.gerritChangeInfo.number

            if commitInfo.gerritChangeInfo.patchSetNumber:
                gerritChangeNumberText += "/" + str(
                    commitInfo.gerritChangeInfo.patchSetNumber
                )

                commitGerritUrl += "/%d" % commitInfo.gerritChangeInfo.patchSetNumber

                # We have the exact patchset number

                if commitInfo.gerritChangeInfo.status == ChangeStatus.MERGED:
                    # Commit was merged
                    changeStyle = "change_merged"
                else:
                    # Commit was pulled, but not merged
                    changeStyle = "change_pulled"

            else:
                # We found the commit on gerrit, but don't know the exact patchset (may have been cherry-picked)
                changeStyle = "change_cherrypicked"
        else:
            # Commit not on gerrit
            changeStyle = "change_local"

        result += '<tr class="%s">' % changeStyle

        # Title
        result += "<td>%s</td>" % commitInfo.title

        # Hash/gitweb URL
        commitGitwebUrl = gitwebUrl + "a=commit;h=" + commitInfo.hash
        result += (
            '<td style="text-align:center"> <a href="%s" target="_blank">%s</a></td>'
            % (commitGitwebUrl, commitInfo.shortHash)
        )

        # Change number/gerrit URL
        result += '<td style="text-align:center">'
        if commitGerritUrl:
            result += '<a href="%s" target="_blank">%s</a>' % (
                commitGerritUrl,
                gerritChangeNumberText,
            )
        else:
            result += gerritChangeNumberText

        result += "</td>"

        # Author
        result += "<td>%s</td>" % commitInfo.author

        result += "</tr>"

        return result
