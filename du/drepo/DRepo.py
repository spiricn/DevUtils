import logging
import os
import sys
import codecs
import copy
from collections import namedtuple
import threading
import concurrent.futures
import io

from enum import Enum

from du.drepo.Commands import Commands
from du.drepo.Commands import DownloadType

from du.gerrit.ssh.Connection import Connection
from du.gerrit.rest.change.ChangeEndpoint import ChangeEndpoint
from du.gerrit.rest.change.QueryOption import QueryOption
from du.gerrit.ChangeStatus import ChangeStatus
from du.utils.ShellCommand import ShellCommand, CommandFailedException

from du.drepo.Utils import Utils
from du.drepo.manifest.Common import ProjectOption
from du.drepo.report.Analyzer import Analyzer

# Set stdout/stderr encoding top UTF-8 by default
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Username/password pair credentials
Credentials = namedtuple("Credentials", "username, password")

logger = logging.getLogger(__name__.split(".")[-1])


class DRepo:
    # Number of fetch retries
    NUM_FETCH_RETRIES = 3

    # Report encoding
    REPORT_ENCODING = "ISO-8859-1"

    def __init__(
        self,
        manifest,
        ciChange=None,
        ciType=None,
        httpCredentials={},
        fetchDepth=None,
        ciOnly=False,
        tag=None,
    ):
        """
        Constructor

        @param parsed manifest
        @param ciChange(optional) Optional CI change ID, if set checkouts of active
        build are replaced with this change
        @param ciType(optional) Defines how the CI change should be downloaded (i.e. pull/merge, checkout or cherry-pick)
        @param httpCredentials(optional) A server->credential map used when username/password is needed for HTTP calls
        @param fetchDepth(optional) Git history fetch depth. If None, then entire history is downloaded
        @param ciOnly If specified, clones only projects with CI changes
        @param tag Tag to be checkout for all projects
        """

        self._manifest = manifest
        self._ciChange = ciChange
        self._httpCredentials = httpCredentials
        self._fetchDepth = fetchDepth
        self._ciType = ciType
        self._ciOnly = ciOnly
        self._tag = tag

    def sync(self, buildName=None, buildRoot=None, numThreads=1):
        """
        Synchronize everything based on the provided manifest

        @param buildName Build name to synchronize
        @param buildRoot Build root override
        @param numThreads Number of concurrent threads to run the sync on
        """

        self.__build = self.__findBuild(buildName)

        self.__buildRoot = buildRoot if buildRoot else self.__build.root

        # Create connections for all the projects (we'll be using them for queries later on)
        self._connections = {}
        for project in self._manifest.projects:
            self._connections[project] = Utils.createQueryConnection(
                project.remote, self._httpCredentials
            )

        # Find CI changes
        self._ciChanges = self.__findCiChanges(self._ciChange) if self._ciChange else {}

        projectsToProcess = [i for i in self._manifest.projects]

        with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
            # Launch threads
            futures = []
            for i in range(numThreads):
                futures.append(executor.submit(self.__processor, projectsToProcess))

            # Wait for results
            for future in futures:
                future.result()

            executor.shutdown()

    def execute(self, command, buildName=None):
        """
        Execute a command in all project directories

        @param command Command to execute
        @param buildName(optional) Build name
        """

        build = self.__findBuild(buildName)

        for project in self._manifest.projects:
            # Absolute path of this project on disk
            projAbsPath = os.path.join(build.root, project.path)

            if not os.path.exists(projAbsPath):
                continue

            ShellCommand.execute(
                command, workingDirectory=projAbsPath, output=logger.info
            )

    def __findBuild(self, buildName):
        """
        Find a build

        @param buildName Build name. If none, the manifest specified one is used
        """

        if not buildName:
            return self._manifest.selectedBuild

        # Find a build with given name
        try:
            return next(
                build for build in self._manifest.builds if build.name == buildName
            )
        except StopIteration:
            raise RuntimeError("Build not defined: %r" % buildName)

    def __processor(self, projectsToProcess):
        """
        Project processor thread

        @param projectsToProcess List of projects that are not yet processed (shared between multiple threads)
        """

        threadName = threading.current_thread().name

        logger.debug("[%s] start processor" % threadName)

        while projectsToProcess:
            # Take next available project
            try:
                project = projectsToProcess.pop()
            except IndexError:
                break

            logger.debug("[%s] processing %r" % (threadName, project.name))

            # Process
            self.__processProject(project, self.__build)

            logger.debug("[%s] done processing %r" % (threadName, project.name))

    def __processProject(self, project, build):
        """
        Process a single project (checkout branches, download changes, etc.

        @param build Target manifest build
        @param project Target project
        """

        logger.info("\n\t---> processing %r" % project.name)

        # Connection to Gerrit
        conn = self._connections[project]

        # URL we're fetching from
        fetchUrl = Utils.injectPassword(project.remoteUrl, self._httpCredentials)

        # Absolute path of this project on disk
        projAbsPath = os.path.join(self.__buildRoot, project.path)

        # Optional checkout we're using as a base
        checkout = build.checkouts.get(project)

        # List of cherry-picks
        cherryPicks = build.cherrypicks.get(project, [])

        # Pull change
        pullChange = build.pulls.get(project)

        # CI change
        ciChange = self._ciChanges.get(project)

        if self._ciChange and (self._ciOnly and not ciChange):
            # Skip this project, since it doesn't have a CI change
            logger.info("skipping (ci_only) ..")
            return

        # Optional tag we're using as a base
        tag = build.tags.get(project)

        # Don't fetch entire history, just up to self._fetchDepth commits
        fetchDepthArg = []
        if self._fetchDepth:
            fetchDepthArg = ["--depth", self._fetchDepth]

        # No point in having checkout and tag as a base, since they overwrite eachother
        if tag and checkout:
            raise RuntimeError(
                "Tag and checkout defined at the same time for project %r"
                % project.name
            )

        # Prepare local directory (initialize git, clean, etc.)
        Commands.prepareGit(
            projAbsPath, project.remoteUrl, ProjectOption.CLEAN in project.opts
        )

        if self._tag:
            # If tag is specified by the user (e.g. release), just check it out ignoring everything else
            Commands.checkoutTag(
                conn,
                projAbsPath,
                self._tag,
                fetchUrl,
                self.NUM_FETCH_RETRIES,
                fetchDepthArg,
            )
        else:
            # Tag & checkout not defined -> use clean branch as base
            if not tag and not checkout:
                Commands.checkoutBranch(
                    conn,
                    projAbsPath,
                    project.branch,
                    fetchUrl,
                    self.NUM_FETCH_RETRIES,
                    fetchDepthArg,
                )

            # Use tag as base
            elif tag:
                Commands.checkoutTag(
                    conn,
                    projAbsPath,
                    tag,
                    fetchUrl,
                    self.NUM_FETCH_RETRIES,
                    fetchDepthArg,
                )

            # Use checkout as base
            elif checkout:
                Commands.downloadChange(
                    conn,
                    projAbsPath,
                    checkout,
                    fetchUrl,
                    DownloadType.CHECKOUT,
                    DRepo.NUM_FETCH_RETRIES,
                    fetchDepthArg,
                )

            # Pull change on top of the base
            if pullChange:
                Commands.downloadChange(
                    conn,
                    projAbsPath,
                    pullChange,
                    fetchUrl,
                    DownloadType.MERGE,
                    DRepo.NUM_FETCH_RETRIES,
                    fetchDepthArg,
                )

            # Download cherry picks
            for cp in cherryPicks:
                Commands.downloadChange(
                    conn,
                    projAbsPath,
                    cp,
                    fetchUrl,
                    DownloadType.CHERRYPICK,
                    DRepo.NUM_FETCH_RETRIES,
                    fetchDepthArg,
                )

            # Download CI change
            if ciChange:
                Commands.downloadChange(
                    conn,
                    projAbsPath,
                    ciChange.number,
                    fetchUrl,
                    self._ciType,
                    DRepo.NUM_FETCH_RETRIES,
                    fetchDepthArg,
                )

        if not fetchDepthArg:
            # If depth is not specified, fetch all the tags as well (may be used for release note generation later on)
            ShellCommand.execute(
                ["git", "fetch", fetchUrl, project.branch, "--tags", "-f"],
                workingDirectory=projAbsPath,
                numRetries=self.NUM_FETCH_RETRIES,
                randomRetry=True,
            )

    def generateReport(
        self, outputFile, generator, numMergedCommits=3, tagPattern=None, numThreads=1
    ):
        """
        Generate a report file

        @param outputFile Target file name
        @param generator Note generator
        @param numMergedCommits Number of merged commits to include in the report
        @param tagPatern Tag pattern
        @param numThreads Number of threads to run in parallel
        """

        projectsInfo = Analyzer.analyze(
            self._manifest,
            self._httpCredentials,
            numMergedCommits,
            tagPattern,
            numThreads,
        )

        with io.open(outputFile, mode="w", encoding=self.REPORT_ENCODING) as fileObj:
            fileObj.write(generator(projectsInfo))

    def __findCiChanges(self, changeId):
        """
        Fetch a list of all the changes which shared this ID (from all the projects in the manifest)

        @param changeId Change ID shared between one or more changes across potentially multiple projects
        @return a list of change JSON objects
        """

        # Get a list of all the servers we're working with
        tmpUniqueRemotes = []
        remoteProjects = []
        for project in self._manifest.projects:
            if project.remote not in tmpUniqueRemotes:
                tmpUniqueRemotes.append(project.remote)
                remoteProjects.append(project)

        # Try to find changes with this ID on each of the servers
        ciChangeCandidates = []
        for project in remoteProjects:
            conn = self._connections[project]

            changes = conn.query(self._ciChange)

            logger.debug(
                "Fetched CI changes from project %r, %s"
                % (project.name, [str(i) for i in changes])
            )

            ciChangeCandidates += changes

        # Filter out the changes that are either not part of our project list, or not on their respective branches
        result = {}
        for change in ciChangeCandidates:
            for project in self._manifest.projects:
                if (
                    project.name == change.project
                    and project.branch == change.branch
                    and change.status
                    not in [ChangeStatus.ABANDONED, ChangeStatus.MERGED]
                ):
                    result[project] = change

        return result
