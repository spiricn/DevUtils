from copy import deepcopy
import os
import sys
import unittest


class TestBase(unittest.TestCase):
    TEMP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp_dir')

    def setUp(self):
        pass

    @classmethod
    def getTempPath(cls, name):
        fullPath = os.path.join(cls.TEMP_DIR, name)

        dirPath = os.path.dirname(fullPath)

        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)

        return fullPath

    @classmethod
    def callAppMain(cls, main, *args):
        # Save current args
        oldArgs = deepcopy(sys.argv)

        sys.argv = ['python']
        sys.argv += args

        oldCwd = os.getcwd()
        os.chdir(os.path.dirname(__file__))

        exception = None
        try:
            res = main()
        except Exception as e:
            # Remember the exception and raise it later
            exception = e

        # Restore args & wd
        os.chdir(oldCwd)
        sys.argv = oldArgs

        # Re-raise the exception if occurred (after restoring args & wd)
        if exception:
            raise exception

        return res
