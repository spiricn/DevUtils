from collections import namedtuple
import logging
import os

from du.Utils import shellCommand


logger = logging.getLogger(__name__.split('.')[-1])


Symbol = namedtuple('Symbol', 'file, function, line')

class SymbolResolver:
    UNKOWN_SYMBOL = Symbol('??', '??', 0)

    def __init__(self, directories):
        self._libraries = {}

        if directories:
            directories = [i for i in directories if i]

            for directory in directories:
                for root, dirs, files in os.walk(directory):
                    for fileName in files:
                        if os.path.splitext(fileName)[1] == '.so':
                            fullPath = os.path.abspath(os.path.join(root, fileName))
                            name = os.path.basename(fileName)

                            self._libraries[name] = fullPath

    def resolve(self, library, address):
        libraryName = os.path.basename(library)

        if libraryName not in self._libraries:
            return self.UNKOWN_SYMBOL

        libraryPath = self._libraries[libraryName]

        address = address

        cmd = shellCommand(['addr2line', '-C', '-f', '-e', libraryPath, hex(address)])
        if cmd.rc != 0:
            logger.error('command failed (%d): %r' % (cmd.rc, cmd.strStderr))
            return self.UNKOWN_SYMBOL
        lines = cmd.strStdout.splitlines()

        function = lines[0]

        file, line = lines[1].split(':')

        return Symbol(file, function, line)


