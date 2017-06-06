from copy import deepcopy
import os
import shutil
import sys

from du.smartpush.App import main as smartpushMain
from test.TestBase import TestBase


class FileProtocolTest(TestBase):
    def setUp(self):
        pass

    def testBasic(self):
        manifestSource = '''\
def getArtifacts():
    artifacts = []

    artifacts += [Artifact(1, 'artifacts_source/artifact1.txt', '%s')]
    artifacts += [Artifact(1, 'artifacts_source/artifact2.txt', '%s')]

    return {'main_set' : artifacts}
''' % (self.getTempPath('artifacts_dest/artifact1.txt'), self.getTempPath('artifacts_dest/artifact2.txt'))


        # Save args
        args = deepcopy(sys.argv)

        sys.argv = sys.argv[:1]

        os.chdir(os.path.dirname(__file__))

        timestampsDir = self.getTempPath('timestamps')

        # Protocol
        sys.argv.append('file')
        sys.argv += ['-manifest_source', manifestSource]
        sys.argv += ['-timestamps', timestampsDir]
        sys.argv += ['-set', 'main_set']

        if os.path.exists(timestampsDir):
            shutil.rmtree(timestampsDir)

        res = smartpushMain()
        if res != 0:
            self.fail('Main failed: %d' % res)

        self.assertTrue(os.path.exists(self.getTempPath('artifacts_dest/artifact1.txt')))
        self.assertTrue(os.path.exists(self.getTempPath('artifacts_dest/artifact2.txt')))

        self.assertTrue(os.path.exists(timestampsDir))
        self.assertTrue(os.path.isdir(timestampsDir))

        # Restore args
        sys.argv = args

