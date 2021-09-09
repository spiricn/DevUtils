from du.android.hdump.App import main as hdumpMain
from test.TestBase import TestBase


class HdumpTest(TestBase):
    def setUp(self):
        pass

    def testHdump(self):
        res = self.callAppMain(
            hdumpMain,
            "-dump_files",
            "hdump/heap_dump1.txt",
            "-plain_output",
            self.getTempPath("hdump/dump.txt"),
            "-html_output",
            self.getTempPath("hdump/dump.html"),
        )

        self.assertEqual(0, res)

    def testHdumpDiff(self):
        res = self.callAppMain(
            hdumpMain,
            "-dump_files",
            "hdump/heap_dump1.txt",
            "hdump/heap_dump2.txt",
            "-plain_output",
            self.getTempPath("hdump/dump_diff.txt"),
            "-html_output",
            self.getTempPath("hdump/dump_diff.html"),
        )

        self.assertEqual(0, res)
