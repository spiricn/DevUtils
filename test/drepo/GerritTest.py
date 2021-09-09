import os
from du.gerrit.ssh.Connection import Connection
from du.gerrit.ssh.Exception import QueryFailedException
from du.gerrit.ssh.Change import Change
from du.gerrit.ssh.Account import Account
from du.gerrit.ssh.PatchSet import PatchSet
from du.gerrit.Utils import Utils
from test.TestBase import TestBase

from du.utils.ShellCommand import CommandFailedException


class GerritTest(TestBase):
    # Test change number  env variable
    ENV_VAR_CHANGE_NUMBER = "DREPO_TEST_GERRIT_CHANGE_NUMBER"

    # Gerrit server env variable
    ENV_VAR_SERVER = "DREPO_TEST_GERRIT_SERVER"

    def setUp(self):
        self._conn = Connection(self.getEnvVar(self.ENV_VAR_SERVER))

        self._testChangeNumber = int(self.getEnvVar(self.ENV_VAR_CHANGE_NUMBER))

    def testExtractChangeId(self):
        self.assertEqual(
            "I993219b99d6be1e9860e7e5cca2f3d3be3429e09",
            Utils.extractChangeId(
                "Commit message title\n\nbody\nChange-Id: I993219b99d6be1e9860e7e5cca2f3d3be3429e09"
            ),
        )

        self.assertFalse(
            Utils.extractChangeId(
                "Commit message title\n\nbody\nChange-Id: I993219b99d6be1e9860e7e5cca2f3d3be3429eV9"
            )
        )
        self.assertFalse(Utils.extractChangeId(""))
        self.assertFalse(Utils.extractChangeId("Test 1234"))

    def testValidChangeId(self):
        self.assertTrue(
            Utils.isValidChangeId("I91ac197f805f6affab787f811e9817ac821901df")
        )

        self.assertFalse(
            Utils.isValidChangeId("91ac197f805f6affab787f811e9817ac821901df")
        )
        self.assertFalse(
            Utils.isValidChangeId("I91ac197f805f6affab787f811e9817ac821901d")
        )
        self.assertFalse(
            Utils.isValidChangeId("I91ac197f805f6affab787f811e9817ac821g01d")
        )
        self.assertFalse(Utils.isValidChangeId(""))

    def testQueryError(self):
        # Query failure
        with self.assertRaises(QueryFailedException) as context:
            self._conn.query("!")
        self.assertTrue(len(context.exception.query) > 0)

        # Command failure (due to empty query)
        with self.assertRaises(CommandFailedException) as context:
            self._conn.query()

    def testQueryChange(self):
        c = Connection(self.getEnvVar(self.ENV_VAR_SERVER))

        result = c.query(change=self._testChangeNumber)
        self.assertEqual(len(result), 1)

        change = result[0]

        # Owner parsed correctly
        self.assertEqual(type(change.owner), Account)

        # Not fetched by default
        self.assertFalse(change.patchSets)
        self.assertFalse(change.currentPatchSet)

    def testPatchSets(self):
        c = Connection(self.getEnvVar(self.ENV_VAR_SERVER))

        result = c.query(
            Connection.QUERY_ARG_PATCHSETS,  # include patchsets
            change=self._testChangeNumber,
        )
        self.assertEqual(len(result), 1)

        change = result[0]

        # Not fetched by default
        self.assertTrue(change.patchSets)

        # Current patchset present
        self.assertEqual(type(change.patchSets[0]), PatchSet)

    def testCurrentPatchset(self):
        c = Connection(self.getEnvVar(self.ENV_VAR_SERVER))

        result = c.query(
            Connection.QUERY_ARG_CURRENT_PATCHSET,  # include current patchset
            change=self._testChangeNumber,
        )
        self.assertEqual(len(result), 1)

        change = result[0]

        # Not fetched by default
        self.assertFalse(change.patchSets)

        # Current patchset present
        self.assertEqual(type(change.currentPatchSet), PatchSet)
