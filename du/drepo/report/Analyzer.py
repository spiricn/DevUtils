import logging
import os
from collections import namedtuple
import threading

from du.gerrit.Utils import Utils as GerritUtils
from du.utils.ShellCommand import ShellCommand, CommandFailedException
from du.gerrit.rest.change.ChangeEndpoint import ChangeEndpoint
from du.gerrit.ssh.Connection import Connection
from du.gerrit.ssh.Change import Change
from du.drepo.Utils import Utils
from du.gerrit.rest.change.QueryOption import QueryOption
from du.gerrit.ChangeStatus import ChangeStatus
from du.drepo.report.Types import *
import concurrent.futures

logger = logging.getLogger(__name__.split(".")[-1])


class Analyzer:
    """
    DRepo repositories cls. Uses the manifest and goes trough all local repositories buildling metadata along the way
    """

    @classmethod
    def analyze(
        cls, manifest, httpCredentials, numMergedCommits, tagPattern=None, numThreads=1
    ):
        """
        Analyze projects

        @param manifest Input manifest
        @param httpCredentials Credentials used for REST calls to Gerrit
        @param numMergedCommits Number of merged commits to include in the report
        @param tagPattern Tag pattern to match
        """

        projectInfoResults = {}

        projectsToAnalyze = [proj for proj in manifest.projects]

        with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
            # Launch threads
            futures = []
            for i in range(numThreads):
                futures.append(
                    executor.submit(
                        cls.__analyzer,
                        projectsToAnalyze,
                        manifest,
                        httpCredentials,
                        tagPattern,
                        numMergedCommits,
                    )
                )

            # Wait for results
            for future in futures:
                for projectInfo in future.result():
                    projectInfoResults[projectInfo.manifestProject] = projectInfo

            executor.shutdown()

        # Sort the results in the same order as defined in the manifest
        projectsInfo = []
        for project in manifest.projects:
            if project in projectInfoResults:
                projectsInfo.append(projectInfoResults[project])

        # Host name
        hostName = ShellCommand.execute(["hostname"]).stdoutStr.strip()

        # User name
        userName = ShellCommand.execute(["whoami"]).stdoutStr.strip()

        return ReportInfo(manifest, projectsInfo, hostName, userName)

    @classmethod
    def __analyzer(
        cls, projectsToAnalyze, manifest, httpCredentials, tagPattern, numMergedCommits
    ):
        """
        Project analyzer thread

        @param projectsToAnalyze List of projects that are not yet analyzed (shared between threads
        @param manifest see cls.analyze#manifest
        @param httpCredentials see cls.analyze#httpCredentials
        @param tagPattern see cls.analyze#tagPattern
        @param numMergedCommits Number of merged commits to include in the report
        """

        threadName = threading.current_thread().name

        logger.debug("[%s] start analyzer" % threadName)

        result = []

        while projectsToAnalyze:
            # Take next available project
            try:
                project = projectsToAnalyze.pop()
            except IndexError:
                break

            logger.debug("[%s] analyzing %r" % (threadName, project.name))

            # Process
            projectInfo = cls.__analyzeProject(
                manifest, project, httpCredentials, tagPattern, numMergedCommits
            )
            if projectInfo:
                result.append(projectInfo)

            logger.debug("[%s] done analyzing %r" % (threadName, project.name))

        return result

    @classmethod
    def __analyzeProject(
        cls, manifest, proj, httpCredentials, tagPattern, numMergedCommits
    ):
        logger.debug("processing %r .." % proj.name)

        # Local project directory
        localDir = os.path.join(manifest.selectedBuild.root, proj.path)

        logger.debug("directory %r" % localDir)

        # Don't crash in case one of the projects was deleted from the disk, just report a warning
        if not os.path.isdir(localDir) or not os.path.isdir(
            os.path.join(localDir, ".git")
        ):
            logger.warning("not valid git directory, skpping ..")
            return None

        # Create a connnection for Gerrit communication
        conn = Utils.createQueryConnection(proj.remote, httpCredentials)

        # Get tag name
        tagInfo = cls.__getTagInfo(localDir, tagPattern)

        # Get commit log of the project
        log = cls.__getGitLog(localDir)

        historyLength = numMergedCommits

        commits = []

        # Go trough the log
        for logItem in log:
            # Extract full message from the local .git
            message = ShellCommand.execute(
                ["git", "show", "-s", "--format=%B", logItem.hash],
                workingDirectory=localDir,
            ).stdoutStr

            # Extract author (TODO Can we get message & author in a single command?)
            author = ShellCommand.execute(
                ["git", "log", "--format=%an", logItem.hash + "^!"],
                workingDirectory=localDir,
            ).stdoutStr

            # Extract gerrit change from local .git message
            changeId = GerritUtils.extractChangeId(message)

            # Gerrit change info
            gerritChangeInfo = None

            if not changeId:
                # No change ID (not a gerrit commmit ?)
                logger.warning(
                    "could not extract Gerrit change ID, for commit %r from message %r"
                    % (logItem.hash, message)
                )
            else:
                # Fetch information about this change
                gerritChangeInfo = cls.__fetchGerritChangeInfo(
                    conn, changeId, proj.name, logItem.hash
                )

            commitInfo = CommitInfo(
                logItem.title,
                logItem.hash,
                logItem.shortHash,
                author,
                gerritChangeInfo,
            )
            commits.append(commitInfo)

            if (
                commitInfo.gerritChangeInfo
                and commitInfo.gerritChangeInfo.status == ChangeStatus.MERGED
            ):
                historyLength -= 1

            if historyLength == 0:
                # Reached allowed number of merged commits depth
                logger.debug("Maximum history length reached %d" % numMergedCommits)
                break

        return ProjectInfo(proj, tagInfo, commits)

    @classmethod
    def __fetchGerritChangeInfo(cls, conn, changeId, projectName, commitHash):
        """
        Fetch a change from specific project

        @conn Gerrit connection
        @param changeId Change ID
        @param projectName Project name
        @param commitHash Local commit hash

        @return Change information
        """

        # Fetch data from server
        if isinstance(conn, ChangeEndpoint):
            changes = conn.query(
                changeId,
                options=[QueryOption.ALL_REVISIONS, QueryOption.CURRENT_COMMIT],
            )
        else:
            changes = conn.query(
                Connection.QUERY_ARG_PATCHSETS,
                Connection.QUERY_ARG_CURRENT_PATCHSET,
                change=changeId,
            )

        # Find a change in the project we're processing now
        patchsetNumber = None
        changeInfo = None
        for change in changes:
            # Ignore changes which do not belong to our project
            if change.project != projectName:
                continue

            changeInfo = change

            # Try to figure out the patchset number, by comparing hash values
            if isinstance(conn, ChangeEndpoint):
                for revisionHash, revision in change.revisions.items():
                    if revisionHash == commitHash:
                        patchsetNumber = revision.number
                        break

            else:
                for i in change.patchSets:
                    if i.revision == commitHash:
                        patchsetNumber = i.number
                        break

            if patchsetNumber:
                # Found exactly this hash on Gerrit
                break

        if not changeInfo:
            logger.warning(
                "could find change %r in project %r" % (changeId, projectName)
            )
            return None

        return GerritChangeInfo(
            changeInfo.number,
            patchsetNumber,
            changeInfo.status,
            changeInfo.currentRevision.number,
        )

    @classmethod
    def __getGitLog(cls, directory):
        """
        Get a list of git commits for given directory

        @param directory Directory path

        @return a list of log items
        """

        LogItem = namedtuple("LogItem", "hash, shortHash, title")

        # List the logs long/short hashes and their subjects
        cmd = ShellCommand.execute(
            ["git", "log", "--pretty=%H %h %s"], workingDirectory=directory
        )

        items = []

        for line in cmd.stdoutStr.splitlines():
            # Find the first whitespace, indicating the start of the short hash
            longHashEndPos = line.find(" ")

            # Find the first whitespace after that, indicating the start of subject
            shortHashEndPos = line.find(" ", longHashEndPos + 1)

            commitLongHash = line[:longHashEndPos].strip()
            commitShortHash = line[longHashEndPos + 1 : shortHashEndPos]
            commitMessage = line[shortHashEndPos + 1 :].rstrip()

            items.append(LogItem(commitLongHash, commitShortHash, commitMessage))

        return items

    @classmethod
    def __getTagInfo(cls, directory, tagPattern=None):
        """
        @param directory Git directory
        @param tagPattern Tag pattern to look for, in order to provide matchedTagName/cleanMatchedTagName fields
        """

        tagName = None
        tagCleanName = None

        # Get HEAD hash ID
        headHash = ShellCommand.execute(
            ["git", "rev-parse", "--short", "HEAD"], workingDirectory=directory
        ).stdoutStr.rstrip()

        # Get head name (if it's tagged)
        headTagName = None
        try:
            headTagName = ShellCommand.execute(
                ["git", "describe", "--exact-match", "--tags", headHash],
                workingDirectory=directory,
            ).stdoutStr.rstrip()
        except CommandFailedException:
            pass

        tagRefHash = None
        if headTagName:
            tagRefHash = ShellCommand.execute(
                ["git", "show-ref", headTagName, "--hash"], workingDirectory=directory
            ).stdoutStr.rstrip()

        # Find a tag which matches given pattern (may be dirty if commits are present before this tag)
        # For example if we're looking for "master*" tags we could get "master-0.32.0-1-g9298258bf" as a result
        # because there are commits after the "master-0.32" tag
        matchedTagName = None
        if tagPattern:
            try:
                matchedTagName = ShellCommand.execute(
                    ["git", "describe", "--match", tagPattern, "--tags"],
                    workingDirectory=directory,
                ).stdoutStr.rstrip()
            except CommandFailedException:
                logger.warning("Could not find any tags which match %r" % tagPattern)

        # We're looking for the last clean tag name which matches the patter nabove (e.g. instead of "master-0.32.0-1-g9298258bf", we'll get "master-0.32")
        cleanMatchedTagName = None
        if tagPattern:
            try:
                cleanMatchedTagName = ShellCommand.execute(
                    ["git", "describe", "--match", tagPattern, "--tags", "--abbrev=0"],
                    workingDirectory=directory,
                ).stdoutStr.rstrip()
            except CommandFailedException:
                logger.warning("Could not find any tags which match %r" % tagPattern)

        return TagInfo(
            headHash, tagRefHash, headTagName, matchedTagName, cleanMatchedTagName
        )
