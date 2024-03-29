import logging

logger = logging.getLogger(__name__.split(".")[-1])


class AllocationRecord:
    def __init__(self, zygoteChild, size, number, backtrace):
        self.zygoteChild = zygoteChild
        self.size = size
        self.number = number
        self.backtrace = backtrace


class PidMapEntry:
    def __init__(self, startAddress, endAddress, perms, offset, dev, inode, pathname):
        self.startAddress = startAddress
        self.endAddress = endAddress
        self.perms = perms
        self.offset = offset
        self.dev = dev
        self.inode = inode
        self.pathname = pathname


class HeapDumpDoc:
    HEADER = "Android Native Heap Dump v"
    VERSION = "1.0"
    MAPS_START = "MAPS"
    MAPS_END = "END"
    ZYGOTE_CHILD_ID = "z"
    SIZE_ID = "sz"
    NUMBER_ID = "num"
    BACKTRACE_ID = "bt"
    WARNING_PREFIX = "WARNING: "

    def __init__(self, string):
        self._warnings = []

        self._parseString(string)

    @property
    def allocationRecords(self):
        return self._allocationRecords

    @property
    def pidMaps(self):
        return self._pidMaps

    @property
    def version(self):
        return self._version

    @property
    def totalMemory(self):
        return self._totalMemory

    @classmethod
    def _parseAllocationRecord(cls, line):
        tokens = [line for line in line.split(" ") if line]

        # Zygote child
        if tokens[0] != cls.ZYGOTE_CHILD_ID:
            return None

        zygoteChild = True if int(tokens[1]) == 1 else False

        # Size
        if tokens[2] != cls.SIZE_ID:
            return None
        size = int(tokens[3])

        # Number
        if tokens[4] != cls.NUMBER_ID:
            return None
        num = int(tokens[5])

        # Backtrace
        if tokens[6] != cls.BACKTRACE_ID:
            return None

        backtrace = []
        for bt in tokens[7:]:
            if len(bt) != 8:
                return None

            backtrace.append(int(bt, 16))

        return AllocationRecord(zygoteChild, size, num, backtrace)

    @staticmethod
    def _parsePidMap(line):
        # format: address           perms offset  dev   inode   pathname
        tokens = [i for i in line.split(" ") if i]

        address = tokens[0]
        if len(address) != 8 * 2 + 1:
            logger.error("Invalid address format: %r" % address)
            return None

        startAddress, endAddress = [int(i, 16) for i in address.split("-")]

        permissions = tokens[1]
        offset = int(tokens[2], 16)
        device = tokens[3]
        inode = tokens[4]

        if len(tokens) == 6:
            path = tokens[5]
        else:
            path = None

        return PidMapEntry(
            startAddress, endAddress, permissions, offset, device, inode, path
        )

    def _parseString(self, string):
        lines = [line.rstrip() for line in string.splitlines()]

        header = lines.pop(0)
        if not header.startswith(self.HEADER):
            raise RuntimeError("Invalid header: %r" % header)
        self._version = header[len(self.HEADER) :]

        if self._version != self.VERSION:
            raise RuntimeError("Unsupported version: %r" % self._version)

        # Empty line
        if len(lines.pop(0)):
            raise RuntimeError("Unexpected token")

        self._totalMemory = int(lines.pop(0).split(":")[1])
        self._numAllocationRecords = int(lines.pop(0).split(":")[1])

        # Empty line
        while lines:
            line = lines.pop(0)

            if not line:
                break
            elif line.startswith(self.WARNING_PREFIX):
                self._warnings.append(line.split(self.WARNING_PREFIX)[1])

        self._allocationRecords = []
        self._pidMaps = []

        mapsStarted = False

        for lineNumber, line in enumerate(lines):
            if line.startswith(self.ZYGOTE_CHILD_ID):
                allocRecord = self._parseAllocationRecord(line)
                if not allocRecord:
                    raise RuntimeError("Error parsing allocation record: %r" % line)

                self._allocationRecords.append(allocRecord)

            elif line == self.MAPS_START:
                if mapsStarted:
                    raise RuntimeError("Maps already started")

                mapsStarted = True

            elif len(line) > 20 and line[8] == "-":
                if not mapsStarted:
                    raise RuntimeError("Maps not started")

                pidMap = self._parsePidMap(line)
                if not pidMap:
                    raise RuntimeError("Error parsing pid map: %r" % line)

                self._pidMaps.append(pidMap)

            elif line == self.MAPS_END:
                if not mapsStarted:
                    raise RuntimeError("Maps not started")

                mapsStarted = False
            else:
                raise RuntimeError("unexpected line %d: %r" % (lineNumber, line))

            lineNumber += 1

    def __str__(self):
        return "{HeapDump version=%r totalMemory=%d numRecords=%d numMaps=%d}" % (
            self._version,
            self._totalMemory,
            self._numAllocationRecords,
            len(self._pidMaps),
        )
