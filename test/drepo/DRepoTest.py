import os
import logging
from test.TestBase import TestBase
from urllib.parse import urlparse
import tempfile
import shutil

from du.drepo.DRepo import DRepo, Credentials
from du.drepo.manifest.Parser import Parser as ManifestParser
from du.drepo.report.HtmlGenerator import HtmlGenerator
from du.drepo.report.VersionGenerator import VersionGenerator
from du.utils.ShellCommand import ShellCommand

logger = logging.getLogger(__name__.split(".")[-1])


class DRepoTest(TestBase):
    """
    DRepo integration tests
    """

    # SSH remote env var
    ENV_VAR_SSH_REMOTE = "DREPO_TEST_SSH_REMOTE"

    # HTTP remote env var
    ENV_VAR_HTTP_REMOTE = "DREPO_TEST_HTTP_REMOTE"

    # HTTP username
    ENV_VAR_HTTP_USERNAME = "DREPO_TEST_HTTP_USERNAME"

    # HTTP password
    ENV_VAR_HTTP_PASSWORD = "DREPO_TEST_HTTP_PASSWORD"

    # Test project #1
    ENV_VAR_TEST_PROJECT_1 = "DREPO_TEST_PROJECT_1"

    # Test project #2
    ENV_VAR_TEST_PROJECT_2 = "DREPO_TEST_PROJECT_2"

    # Test change number  env variable
    ENV_VAR_CHANGE_NUMBER = "DREPO_TEST_GERRIT_CHANGE_NUMBER"

    def testClone(self):
        vectors = (
            # SSH vector
            (
                self.getEnvVar(self.ENV_VAR_SSH_REMOTE),
                self.getEnvVar(self.ENV_VAR_TEST_PROJECT_1),
                self.getEnvVar(self.ENV_VAR_TEST_PROJECT_2),
                self.getEnvVar(self.ENV_VAR_CHANGE_NUMBER),
                {},
            ),
            # HTTP vector
            (
                self.getEnvVar(self.ENV_VAR_HTTP_REMOTE),
                self.getEnvVar(self.ENV_VAR_TEST_PROJECT_1),
                self.getEnvVar(self.ENV_VAR_TEST_PROJECT_2),
                self.getEnvVar(self.ENV_VAR_CHANGE_NUMBER),
                {
                    urlparse(
                        self.getEnvVar(self.ENV_VAR_HTTP_REMOTE)
                    ).hostname: Credentials(
                        self.getEnvVar(self.ENV_VAR_HTTP_USERNAME),
                        self.getEnvVar(self.ENV_VAR_HTTP_PASSWORD),
                    )
                },
            ),
        )

        # Run clone tests for both
        for remote, project1, project2, changeNumber, httpCredentials in vectors:
            self.__testClone(remote, project1, project2, changeNumber, httpCredentials)

    def __testClone(self, remote, project1, project2, changeNumber, httpCredentials):
        rootDir = tempfile.mkdtemp()

        cloneBuildRoot = os.path.join(rootDir, "clone_build_root")

        cherryPickBuildRoot = os.path.join(rootDir, "cherry_pick_build_root")

        pullBuildRoot = os.path.join(rootDir, "pull_build_root")

        manifest = ManifestParser.parseString(
            '''
DREPO_REMOTES = {
    'test_remote' : "'''
            + remote
            + '''"
}

DREPO_PROJECTS = [
    {
        'name' :  "'''
            + project1
            + '''",
        'remote' : 'test_remote',
        'path' : 'test_root_1',
        'branch' : 'master',
        'opts' : [],
    },

    {
        'name' :  "'''
            + project2
            + '''",
        'remote' : 'test_remote',
        'path' : 'test_root_2',
        'branch' : 'master',
        'opts' : [],
    },
]

DREPO_BUILDS = {
    'test_default_clone_build' : {
        'root' :  "'''
            + cloneBuildRoot
            + '''"
    },

    'test_cherrypick_build' : {
        'root' :  "'''
            + cherryPickBuildRoot
            + '''",
        'cherry_picks' : { "'''
            + project1
            + """" : ["""
            + changeNumber
            + '''] },
    },

    'test_pull_build' : {
        'root' :  "'''
            + pullBuildRoot
            + '''",
        'final_touches' : { "'''
            + project1
            + """" : """
            + changeNumber
            + """ },
    },
}

DREPO_SELECTED_BUILD = 'test_default_clone_build'
        """
        )

        drepo = DRepo(manifest, httpCredentials=httpCredentials)

        def generateReport():
            # Generate notes
            for generator in (VersionGenerator.generate, HtmlGenerator.generate):
                notesFile = os.path.join(cloneBuildRoot, str(generator))
                logger.info("generating notes to %r" % notesFile)

                drepo.generateReport(notesFile, generator)

                self.assertTrue(os.path.isfile(notesFile))

        # Sync
        drepo.sync()

        self.assertTrue(os.path.isdir(os.path.join(cloneBuildRoot, "test_root_1")))
        self.assertTrue(os.path.isdir(os.path.join(cloneBuildRoot, "test_root_1/.git")))

        self.assertTrue(os.path.isdir(os.path.join(cloneBuildRoot, "test_root_2")))
        self.assertTrue(os.path.isdir(os.path.join(cloneBuildRoot, "test_root_2/.git")))

        # Double sync
        drepo.sync()

        # Crete a dummy commit which is not on Gerrit
        ShellCommand.execute(
            ["git", "commit", "--allow-empty", "-m", "dummy empty commit"],
            workingDirectory=os.path.join(cloneBuildRoot, "test_root_1"),
        )

        generateReport()

        drepo.sync("test_cherrypick_build")
        generateReport()

        drepo.sync("test_pull_build")
        generateReport()

        # Cleanup
        shutil.rmtree(rootDir)
