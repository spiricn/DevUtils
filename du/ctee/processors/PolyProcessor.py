from du.android import LogcatParser
from du.ctee.processors.BaseProcessor import BaseProcessor
import re

MESSAGE_REGEX = re.compile(r"^(\d+\-\d+\-\d+ \d+:\d+:\d+.\d+)\s+(\w+)\s+(\w+): (.*$)")

STYLE_MAP = {
    "DEBUG": "debug",
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
    "VERBOSE": "verbose",
    "CRITICAL": "fatal",
}


class PolyProcessor(BaseProcessor):
    def __init__(self, stylesheet=None):
        BaseProcessor.__init__(self, stylesheet)

        self._maxTagLen = 0

    def getStyle(self, line):

        match = re.match(MESSAGE_REGEX, line)
        if not match:
            return ()

        self._maxTagLen = max(self._maxTagLen, len(match[3]))
        fmt = "{:>" + str(self._maxTagLen) + "}"

        meta = match[1] + " " + match[2][0] + " " + fmt.format(match[3]) + ":"

        return [
            (meta, self.stylesheet["meta"]),
            (" ", None),
            (match[4], self.stylesheet[STYLE_MAP[match[2]]]),
        ]
