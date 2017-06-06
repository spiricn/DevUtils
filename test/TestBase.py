import os
import unittest


class TestBase(unittest.TestCase):
    TEMP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp_dir')

    def setUp(self):
        pass

    @classmethod
    def getTempPath(cls, name):
        return os.path.join(cls.TEMP_DIR, name)
