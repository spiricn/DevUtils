from du.cgen.App import main as cgenMain
from test.TestBase import TestBase


class CgenJavaTest(TestBase):
    def setUp(self):
        pass

    def testNoArgs(self):
        res = self.callAppMain(cgenMain,
                              'java',
                              self.getTempPath('cgen/CgenTestNoArgs.java'),
                              '-java_package', 'com.cgen.test',
                              '-java_class', 'CgenTestNoArgs'
        )
        self.assertEqual(0, res)

    def testArgs(self):
        res = self.callAppMain(cgenMain,
                         'java',
                         self.getTempPath('cgen/CgenTestArgs.java'),
                         '-java_package', 'com.cgen.test',
                         '-java_class', 'CgenTestArgs',
                         '-args',
                         'stringArg', 'test',
                         'intArg', '42',
                         'boolArg', 'false'
        )
        self.assertEqual(0, res)
