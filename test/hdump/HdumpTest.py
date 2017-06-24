from du.android.hdump.App import main as hdumpMain
from test.TestBase import TestBase


class HdumpTest(TestBase):
    def setUp(self):
        pass

    def testHdump(self):
        res = self.callAppMain(hdumpMain,
           'hdump/heap_dump.txt',
           '-plainOutput', self.getTempPath('hdump/dump.txt'),
           '-htmlOutput', self.getTempPath('hdump/dump.html'),
        )

        self.assertEqual(0, res)
