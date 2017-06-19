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

        directories = [i for i in directories if i]

        if directories:
            logger.debug('scanning %d directories ..' % len(directories))

            for directory in directories:
                logger.debug('scanning %r ..' % directory)

                for root, dirs, files in os.walk(directory):
                    for fileName in files:
                        if os.path.splitext(fileName)[1] == '.so':
                            fullPath = os.path.abspath(os.path.join(root, fileName))
                            name = os.path.basename(fileName)

                            if name in self._libraries:
                                logger.warning('duplicate library found: %r' % name)

                            self._libraries[name] = fullPath

        logger.debug('libraries found: %d' % len(self._libraries))


    def resolve(self, library, address):
        libraryName = os.path.basename(library)

        if libraryName not in self._libraries:
            return self.UNKOWN_SYMBOL

        libraryPath = self._libraries[libraryName]

        cmd = shellCommand(['objdump', '-w', '-j', '.text', '-h', libraryPath])
        if cmd.rc != 0:
            logger.error('command failed (%d): %r' % (cmd.rc, cmd.strStderr))
            return self.UNKOWN_SYMBOL

        fileOffset = None
        for line in cmd.strStdout.splitlines():
            tokens = line.split()

            if len(tokens) > 5 and tokens[1] == '.text':
                fileOffset = int(tokens[5], 16)

        if not fileOffset:
            logger.error('could not find file offest')
            return self.UNKOWN_SYMBOL

        address = address

        cmd = shellCommand(['addr2line', '-C', '-f', '-e', libraryPath, hex(address)])
        if cmd.rc != 0:
            logger.error('command failed (%d): %r' % (cmd.rc, cmd.strStderr))
            return self.UNKOWN_SYMBOL
        lines = cmd.strStdout.splitlines()

        function = lines[0]

        file, line = lines[1].split(':')

        return Symbol(file, function, line)


