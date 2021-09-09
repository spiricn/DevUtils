from du.drepo.manifest.Common import OPT_CLEAN, OPT_RESET, ProjectOption
from du.drepo.manifest.Remote import Remote
from du.drepo.manifest.Project import Project
from du.drepo.manifest.Build import Build
from du.drepo.manifest.Manifest import Manifest
from du.manifest.Exceptions import *
from du.manifest.ManifestDict import ManifestDict
from du.manifest.ManifestParser import ManifestParser

from du.gerrit.Utils import Utils

from collections import namedtuple

import sys
import os


class Parser:
    """
    Manifest parser
    """

    # Root remotes attribute name(s)
    KEY_REMOTES = ("remotes", "DREPO_REMOTES")

    # Root builds attribute name(s)
    KEY_BUILDS = ("builds", "DREPO_BUILDS")

    # Root projects attribute name(s)
    KEY_PROJECTS = ("projects", "DREPO_PROJECTS")

    # Root build attribute name(s)
    KEY_BUILD = ("build", "DREPO_SELECTED_BUILD")

    # Constant for "ssh" string
    KEY_REMOTE_SSH = "ssh"

    # Constant for "fetch" string
    KEY_REMOTE_FETCH = "fetch"

    # Project name attribute name
    KEY_NAME = "name"

    # Project remote name attribute name
    KEY_REMOTE = "remote"

    # Projet pat attribute name
    KEY_PATH = "path"

    # Project branch attribute name
    KEY_BRANCH = "branch"

    # Project options attribute name
    KEY_OPTS = "opts"

    # Root path attribute name
    KEY_ROOT = "root"

    # Cherrypicks attribute name
    KEY_CHERRYPICKS = "cherrypicks"

    # Checkouts attribute name
    KEY_CHECKOUTS = ("final_touches", "checkouts")

    # Tags attribute name
    KEY_TAGS = "tags"

    # Pulls attribute name
    KEY_PULLS = "pulls"

    @classmethod
    def parseString(cls, string):
        """
        Parse a manifest string

        @param string
        @return Manifest object
        """

        # Expose options to the manifest script
        manifestLocals = {
            # Project option (indicates that git repo should be cleaned)
            "OPT_CLEAN": OPT_CLEAN,
            # TODO Deprecated, should be removed
            "OPT_RESET": OPT_RESET,
            # Allow the manifests to acquire environment variables
            "DREPO_GET_ENV": cls.__getEnvVar,
        }

        ManifestParser.executeString(string, manifestLocals)

        manifestLocals = ManifestDict(manifestLocals)

        # Parse remotes
        rawRemotes = manifestLocals.getDict(cls.KEY_REMOTES)
        remotes = []
        for name, url in rawRemotes.raw.items():
            # Simple format (remote contains only one url which is used for both ssh and fetching)
            if type(url) == str:
                remotes.append(Remote(name, url))
            elif type(url) == dict:
                sshUrl = None
                fetchUrl = None
                for dictName, dictUrl in url.items():
                    # Advanced format (remote object is actualy dictionaty of two url's: ssh and fetch)
                    if type(dictUrl) == str:
                        # Allow only ssh and fetch url names
                        if dictName == cls.KEY_REMOTE_SSH:
                            sshUrl = dictUrl
                        elif dictName == cls.KEY_REMOTE_FETCH:
                            fetchUrl = dictUrl
                        else:
                            raise ManifestParseError(
                                'Expected string "'
                                + cls.KEY_REMOTE_SSH
                                + '" or "'
                                + cls.KEY_REMOTE_FETCH
                                + '" for remote dictName value, got "%s"' % dictName
                            )
                    else:
                        raise ManifestParseError(
                            "Expected string for remote dictUrl type, got %s"
                            % type(dictUrl)
                        )
                # fetch url is mandatory
                if not fetchUrl:
                    raise ManifestParseError(
                        "Fetch url in remotes dictionary is mandatory"
                    )
                remotes.append(Remote(name, fetchUrl, sshUrl))
            else:
                raise ManifestParseError(
                    "Expected string for remote url type, got %s" % type(url)
                )

        # Parse projects
        rawProjects = manifestLocals.getList(cls.KEY_PROJECTS, dict)
        projects = []
        for rawProject in [ManifestDict(i) for i in rawProjects]:
            projects.append(cls.__parseProject(rawProject, remotes))

        # Parse builds
        rawBuilds = manifestLocals.getDict(cls.KEY_BUILDS)
        builds = []
        for buildName, rawBuild in rawBuilds.raw.items():
            builds.append(cls.__parseBuild(buildName, ManifestDict(rawBuild), projects))

        buildName = manifestLocals.getStr(cls.KEY_BUILD)

        # Find the selected build
        try:
            selectedBuild = next(filter(lambda build: build.name == buildName, builds))
        except StopIteration:
            raise ManifestLogicError("Could not find active build named %r" % buildName)

        return Manifest(remotes, projects, builds, selectedBuild)

    @classmethod
    def __getEnvVar(cls, name):
        """
        Get environment. Throw if it doesn't exist

        @param name Variable name
        """

        value = os.getenv(name)

        if not value:
            raise RuntimeError("Environment variable %r not defined" % name)
        return value

    @classmethod
    def __parseBuild(cls, buildName, rawBuild, projects):
        """
        Parse a build entry

        @param buildName Build name
        @param rawBuild Raw build dictionary
        @param projects Parsed projects list

        @return parsed Build
        """

        # Buidl root path
        root = rawBuild.getStr(cls.KEY_ROOT)

        # List of cherry picks
        cherrypicks = cls.__parseProjectMap(
            rawBuild, projects, cls.KEY_CHERRYPICKS, cls.__cherryPickListValidator
        )

        # Checkouts map
        checkouts = cls.__parseProjectMap(
            rawBuild, projects, cls.KEY_CHECKOUTS, cls.__changeValidator
        )

        # Pulls map
        pulls = cls.__parseProjectMap(
            rawBuild, projects, cls.KEY_PULLS, cls.__changeValidator
        )

        # Tags map
        tags = cls.__parseProjectMap(
            rawBuild, projects, cls.KEY_TAGS, cls.__tagValidator
        )

        return Build(buildName, root, cherrypicks, checkouts, tags, pulls)

    @classmethod
    def __parseProjectMap(cls, rawBuild, projects, key, validator):
        """
        Parser a project : value map

        @param rawBuild Raw build
        @param projects List of projects
        @param key Map key
        @param validator Validator function used to check if value is ok
        """

        rawProjectMap = {}
        try:
            rawProjectMap = rawBuild.getDict(key).raw
        except ManifestFieldMissingError:
            return rawProjectMap

        projectMap = {}
        for projectName, value in rawProjectMap.items():
            # Value OK ?
            validator(value)

            # Find a project with this name
            try:
                buildProject = next(
                    filter(lambda project: project.name == projectName, projects)
                )
            except StopIteration:
                raise ManifestLogicError("Could not find project %r" % projectName)

            projectMap[buildProject] = value

        return projectMap

    @classmethod
    def __tagValidator(cls, tag):
        """
        Checks if given object is a valid tag name

        @param tag Tag name
        """

        if not isinstance(tag, str):
            raise ManifestParseError("Expected string for tag name, got %s" % type(tag))

    @classmethod
    def __cherryPickListValidator(cls, changeList):
        """
        Checks received object is a valid list of cherrypicks

        @param changeList Change list
        """

        if not isinstance(changeList, list) and not isinstance(changeList, tuple):
            raise ManifestParseError(
                "Expected list for cherrypicks, got %r" % type(changeList)
            )

        # Check individual changes
        for change in changeList:
            cls.__changeValidator(change)

    @classmethod
    def __changeValidator(cls, change):
        """
        Check if the change specifier is valid

        @param change Change specifier
        """
        if type(change) == str:
            # If it's a string, it has to be a Change-ID
            if not Utils.isValidChangeId(change):
                raise ManifestParseError("Invalid change ID %r" % change)

        elif type(change) != int:
            # If not a Change-ID string, then it has to be an integer change number
            raise ManifestParseError(
                "Invalid change number, expected int got: %s" % type(change)
            )

    @classmethod
    def __parseProject(cls, rawProject, remotes):
        """
        Parse project entry

        @param rawProject Raw project dictionary
        @param remotes Parsed remotes list

        @return parsed Project object
        """

        # Project name
        name = rawProject.getStr(cls.KEY_NAME)

        # Remote name
        remoteName = rawProject.getStr(cls.KEY_REMOTE)

        # Try to find remote with this name
        try:
            projectRemote = next(
                filter(lambda remote: remote.name == remoteName, remotes)
            )
        except StopIteration:
            raise ManifestLogicError(
                "Could not find remote named %r for project %r" % (remoteName, name)
            )

        # Project path
        path = rawProject.getStr(cls.KEY_PATH)

        # Project branch
        branch = rawProject.getStr(cls.KEY_BRANCH)

        # Project options
        opts = []
        try:
            opts = rawProject.getList(cls.KEY_OPTS, ProjectOption)
        except ManifestFieldMissingError:
            pass

        return Project(name, projectRemote, path, branch, opts)
