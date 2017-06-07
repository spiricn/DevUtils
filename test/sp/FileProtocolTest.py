import os
import shutil

from du.smartpush.App import main as smartpushMain
from test.TestBase import TestBase


class FileProtocolTest(TestBase):
    def setUp(self):
        pass

    def testBasic(self):
        manifestSource = '''\
def getArtifacts():
    artifacts = []

    artifacts += [Artifact(TYPE_CUSTOM, 'sp/artifacts_source/artifact1.txt', '%s')]
    artifacts += [Artifact(TYPE_CUSTOM, 'sp/artifacts_source/artifact2.txt', '%s')]

    return {'main_set' : artifacts}
''' % (self.getTempPath('artifacts_dest/artifact1.txt'), self.getTempPath('artifacts_dest/artifact2.txt'))

        timestampsDir = self.getTempPath('timestamps')

        if os.path.exists(timestampsDir):
            shutil.rmtree(timestampsDir)

        res = self.callAppMain(smartpushMain,
                        'file',
                        '-manifest_source', manifestSource,
                        '-timestamps', timestampsDir,
                        '-set', 'main_set'
        )
        self.assertEqual(0, res)

        self.assertTrue(os.path.exists(self.getTempPath('artifacts_dest/artifact1.txt')))
        self.assertTrue(os.path.exists(self.getTempPath('artifacts_dest/artifact2.txt')))

        self.assertTrue(os.path.exists(timestampsDir))
        self.assertTrue(os.path.isdir(timestampsDir))

