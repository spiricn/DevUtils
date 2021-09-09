import os
from du.utils.ShellCommand import ShellCommand, CommandFailedException
from test.TestBase import TestBase


class ShellCommandTest(TestBase):
    def testExecute(self):
        cmd = ShellCommand.execute(["echo", "42"])

        self.assertEqual(cmd.stdoutStr.strip(), "42")
        self.assertFalse(cmd.stderrStr)
        self.assertEqual(ShellCommand.RETURN_CODE_OK, cmd.returnCode)

    def testRaiseOnFail(self):
        with self.assertRaises(CommandFailedException) as context:
            ShellCommand.execute(["cat", "#"])

    def testNotRaiseOnFail(self):
        cmd = ShellCommand.execute(["cat", "#"], raiseOnError=False)
        self.assertNotEqual(cmd.returnCode, 0)
        self.assertTrue(cmd.stderrStr)
        self.assertFalse(cmd.stdoutStr)
