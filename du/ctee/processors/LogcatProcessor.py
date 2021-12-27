from du.android import LogcatParser
from du.android.LogcatParser import INVERSE_LOGCAT_LEVEMAP
from du.ctee.processors.BaseProcessor import BaseProcessor


class LogcatProcessor(BaseProcessor):
    def __init__(self, stylesheet=None):
        BaseProcessor.__init__(self, stylesheet)
        self._maxTagLen = 0

    def getStyle(self, line):
        parsed = LogcatParser.parseLine(line)
        if not parsed:
            return ((line, self._findStyle(line)),)

        meta = ""
        ms = str(int(parsed.time.microsecond / 1000.0)).zfill(4)

        meta += parsed.time.strftime("%H:%M:%S") + "." + ms

        paddingSize = 5 - len(str(parsed.pid))

        self._maxTagLen = max(self._maxTagLen, len(parsed.tag))
        fmt = "{:>" + str(self._maxTagLen) + "}"

        paddedPid = (paddingSize * "0") + str(parsed.pid)
        meta += (
            " "
            + INVERSE_LOGCAT_LEVEMAP[parsed.level]
            + " "
            + paddedPid
            + " "
            + fmt.format(parsed.tag)
            + ":"
        )

        return (
            (meta, self.stylesheet["meta"]),
            (" ", None),
            (parsed.message, self._findStyle(line)),
        )

    def _findStyle(self, line):
        if "V/" in line:
            return self.stylesheet["verbose"]
        elif "E/" in line:
            return self.stylesheet["error"]
        elif "D/" in line:
            return self.stylesheet["debug"]
        elif "W/" in line:
            return self.stylesheet["warning"]
        elif "F/" in line:
            return self.stylesheet["fatal"]
        elif "I/" in line:
            return self.stylesheet["info"]

        return None
