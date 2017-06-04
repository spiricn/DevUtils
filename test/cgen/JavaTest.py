from copy import deepcopy
import sys
import unittest

from du.cgen.App import main as cgenMain


class CgenJavaTest(unittest.TestCase):
    def setUp(self):
        pass

    def testNoArgs(self):
        # Save args
        args = deepcopy(sys.argv)

        sys.argv = sys.argv[:1]

        sys.argv.append('java')
        sys.argv.append('CgenTestNoArgs.java')
        sys.argv += ['-java_package', 'com.cgen.test']
        sys.argv += ['-java_class', 'CgenTestNoArgs']

        res = cgenMain()
        if res != 0:
            self.fail('Main failed: %d' % res)

        # Restore args
        sys.argv = args

        return

    def testArgs(self):
        # Save args
        args = deepcopy(sys.argv)

        sys.argv = sys.argv[:1]

        sys.argv.append('java')
        sys.argv.append('CgenTestArgs.java')
        sys.argv += ['-java_package', 'com.cgen.test']
        sys.argv += ['-java_class', 'CgenTestArgs']

        sys.argv += ['-args',
                     'stringArg', 'test',
                     'intArg', '42',
                     'boolArg', 'false'
        ]

        res = cgenMain()
        if res != 0:
            self.fail('Main failed: %d' % res)

        # Restore args
        sys.argv = args

        return
