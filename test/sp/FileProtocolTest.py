from copy import deepcopy
import os
import shutil
import sys
import unittest

from du.smartpush.App import main as smartpushMain


class FileProtocolTest(unittest.TestCase):
    def setUp(self):
        pass

    def testBasic(self):
        # Save args
        args = deepcopy(sys.argv)

        sys.argv = sys.argv[:1]

        os.chdir(os.path.dirname(__file__))

        timestampsDir = 'timestamps'

        # Protocol
        sys.argv.append('file')
        sys.argv.append('artifacts_source/manifest.py')
        sys.argv += ['-timestamps', timestampsDir]

        if os.path.exists(timestampsDir):
            shutil.rmtree(timestampsDir)

        res = smartpushMain()
        if res != 0:
            self.fail('Main failed: %d' % res)

        self.assertTrue(os.path.exists('artifacts_dest/artifact1.txt'))
        self.assertTrue(os.path.exists('artifacts_dest/artifact2.txt'))

        self.assertTrue(os.path.exists(timestampsDir))
        self.assertTrue(os.path.isdir(timestampsDir))

        # Restore args
        sys.argv = args

