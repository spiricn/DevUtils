from du.utils.ShellCommand import ShellCommand, CommandFailedException
from du.Utils import makeDirTree
from du.gerrit.rest.change.ChangeEndpoint import ChangeEndpoint
from du.gerrit.rest.change.QueryOption import QueryOption
from du.gerrit.ssh.Connection import Connection

import logging
import os
from enum import Enum

logger = logging.getLogger(__name__.split(".")[-1])

# Dummy email & user name to be used during cherry-picks, if none is configured
DEFAULT_GIT_EMAIL = "drepo@drepo.com"
DEFAULT_GIT_NAME = "DevUtils Drepo"


class DownloadType(Enum):
    """
    Download action when downloading a change
    """

    CHERRYPICK = "cherrypick"
    MERGE = "merge"
    CHECKOUT = "checkout"

    @classmethod
    def valueList(cls):
        return list(map(lambda c: c.value, cls))


class Commands:
    """
    Collection of git/gerrit high level commands
    """

    # Return code reported by git if we try to add an already existing remote
    GIT_CODE_REMOTE_ALREADY_EXISTS = 128

    @classmethod
    def prepareGit(cls, path, remoteUrl, clean, remoteName="origin"):
        """
        Prepare a git directory

        @param path Local path
        @param remoteUrl Remote URL
        @param clean Indication if clean of the git directory should be preformed
        @param remoteName Name of the remote to be added if it doesn't exist
        """

        if not os.path.exists(os.path.join(path, ".git")):
            # Create an empty git repository
            logger.info("initializing %r" % path)

            try:
                makeDirTree(path)
            except FileExistsError:
                # May fail in case of multiple threads (if another thread crates this directory after the first condition check)
                pass

            ShellCommand.execute(["git", "init"], workingDirectory=path)

        # Add a remote (not strictly needed, but still useful)
        try:
            ShellCommand.execute(
                ["git", "remote", "add", remoteName, remoteUrl], workingDirectory=path
            )
        except CommandFailedException as e:
            if e.command.returnCode != cls.GIT_CODE_REMOTE_ALREADY_EXISTS:
                raise e

            # Update the URL if it already exists
            ShellCommand.execute(
                ["git", "remote", "set-url", remoteName, remoteUrl],
                workingDirectory=path,
            )

        # Reset possible unsuccessful merges/etc.
        ShellCommand.execute(["git", "reset", "--hard"], workingDirectory=path)

        # Clean
        if clean:
            logger.info("cleaning %r" % path)
            ShellCommand.execute(["git", "clean", "-dfx"], workingDirectory=path)

    @staticmethod
    def checkoutBranch(conn, path, branch, fetchUrl, numRetries, fetchArgs=[]):
        """
        Download & checkout a branch

        @param conn Gerrit connection
        @param path Local path
        @param branch Branch name
        @param fetchUrl URL we're fetching from
        @param numRetries How many times should the network commands be re-tried
        @param fetchArgs Additional fetch args
        """

        logger.info("checkout branch %r @ %r" % (branch, path))

        # Fetch only our branch
        ShellCommand.execute(
            ["git", "fetch", fetchUrl, branch] + fetchArgs,
            workingDirectory=path,
            numRetries=numRetries,
            randomRetry=True,
        )

        try:
            ShellCommand.execute(["git", "show-branch", branch], workingDirectory=path)

            # Branch exists so reset it to what we fetched
            ShellCommand.execute(["git", "checkout", branch], workingDirectory=path)
            ShellCommand.execute(
                ["git", "reset", "--hard", "FETCH_HEAD"], workingDirectory=path
            )

        except CommandFailedException:
            # Branch doesn't exist, so just checkout
            ShellCommand.execute(
                ["git", "checkout", "-b", branch, "FETCH_HEAD"],
                workingDirectory=path,
            )

    @staticmethod
    def checkoutTag(conn, path, tag, fetchUrl, numRetries, fetchArgs=[]):
        '''
        Checkout a tag

        @param conn Gerrit connection
        @param path Local path
        @param tag Tag name
        @param fetchUrl URL we're fetching from
        @param numRetries How many times should the network commands be re-tried
        @param fetchArgs Additional fetch args
        """
        '''
        logger.info("checkout tag %r @ %r" % (tag, path))

        # Fetch only our tag
        ShellCommand.execute(
            command=[
                "git",
                "fetch",
                fetchUrl,
                "tag",
                tag,
                "--no-tags",
            ]
            + fetchArgs,
            workingDirectory=path,
            numRetries=numRetries,
            randomRetry=True,
        )

        # Checkout what we fetched
        ShellCommand.execute(["git", "checkout", "FETCH_HEAD"], workingDirectory=path)

    @staticmethod
    def fetchCurrentPatchsetRef(conn, change):
        """
        Fetch current patchset information of given change

        @param conn Gerrit connection (REST or SSH)
        @param change Change

        @return patchset information
        """

        if isinstance(conn, ChangeEndpoint):
            res = conn.query(change, options=[QueryOption.CURRENT_REVISION])
        else:
            res = conn.query(Connection.QUERY_ARG_CURRENT_PATCHSET, change=change)

        if res:
            return res[0].currentRevision.ref

        raise RuntimeError(
            "Could not acquire current patchset of change %s" % str(change)
        )

    @staticmethod
    def downloadChange(
        conn, path, change, fetchUrl, downloadType, numRetries, fetchArgs=[]
    ):
        """
        Download a change into a git folder

        @param conn Gerrit connection
        @param path Project path
        @param fetchUrl Fetch URL
        @param DRepo.DownloadType Type of download (i.e. cherrypick, checkout, merge)
        @param numRetries How many times should the network commands be re-tried
        @param fetchArgs Optional additional fetch arguments
        """
        logger.info("%s %r @ %r" % (downloadType.name, str(change), path))

        ref = Commands.fetchCurrentPatchsetRef(conn, change)

        # Download the change
        ShellCommand.execute(
            ["git", "fetch", fetchUrl, ref] + fetchArgs,
            workingDirectory=path,
            numRetries=numRetries,
            randomRetry=True,
        )

        if downloadType == DownloadType.CHERRYPICK:
            # Check if email is configured (needed for cherry-pick)
            try:
                ShellCommand.execute(
                    ["git", "config", "--get", "user.email"],
                    workingDirectory=path,
                )
            except CommandFailedException:
                logger.warning("User email needed for cherry-pick, creating one..")
                ShellCommand.execute(
                    ["git", "config", "user.email", DEFAULT_GIT_EMAIL],
                    workingDirectory=path,
                )

            # Check if name is configured
            try:
                ShellCommand.execute(["git", "config", "--get", "user.name"])
            except CommandFailedException:
                logger.warning("User name needed for cherry-pick, creating one..")
                ShellCommand.execute(
                    ["git", "config", "user.name", DEFAULT_GIT_NAME],
                    workingDirectory=path,
                )

        command = ["git"]

        # Pick a command based on the download type
        command.append(
            {
                DownloadType.CHERRYPICK: "cherry-pick",
                DownloadType.MERGE: "merge",
                DownloadType.CHECKOUT: "checkout",
            }[downloadType]
        )

        if downloadType == DownloadType.MERGE:
            # Only allow fast-forward merges
            command.append("--ff-only")

        command.append("FETCH_HEAD")

        ShellCommand.execute(command, workingDirectory=path)
