from collections import namedtuple
import logging
import socket
import time
import traceback

from du.android.adb.GooglePythonADB import GooglePythonADB, \
    DEFAULT_COMMAND_TIMEOUT_MS


ProcessInfo = namedtuple('ProcessInfo', 'name, pid')
ServiceInfo = namedtuple('ServiceInfo', 'name, interface')
PackageInfo = namedtuple('PackageInfo', 'name')
InstrumentationInfo = namedtuple('InstrumentationInfo', 'package, className, target')
MemoryInfo = namedtuple('MemoryInfo', 'total, used, free')

logger = logging.getLogger(__name__)

class ADB(GooglePythonADB):
    def __init__(self, opqaue):
        super(ADB, self).__init__(opqaue)

    @classmethod
    def connect(cls, addr, port, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        opaque = GooglePythonADB._connect(addr, port, timeoutMs)

        return ADB(opaque)

    @classmethod
    def waitUntilOnline(cls, address, port):
        while True:
            try:
                logger.debug('Attempting to connect to \'%s:%d\' ..' % (address, port))

                adb = ADB.connect(address, port)

                logger.debug('Connected')

                if adb.ping():
                    return adb

            except socket.error:
                # Expected error while the device is offline, so just wait a bit and try again
                time.sleep(0.5)
                continue

            except Exception:
                logger.error(traceback.format_exc())
                return None

    def clearLogcat(self):
        return self.shell('logcat -c')

    def deleteFile(self, path):
        return self.shell('rm %s' % path)

    def broadcast(self, args):
        return self.shell('am broadcast %s' % args)

    def rebootAndWait(self):
        self.reboot()

        # Wait until the device goes offline
        while self.ping():
            pass

        self.disconnect()

        return ADB.waitUntilOnline()

    def fileExists(self, path, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        rc = int(self.shell('[ -f %s ] ; echo $?' % path, timeoutMs))

        return True if rc == 0 else False

    def getProcesses(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        res = self.shell('ps', timeoutMs)

        if not res:
            return None

        lines = res.splitlines(False)

        processes = []

        # Default ps output headers
        outputHeaders = ['USER', 'PID', 'PPID', 'VSIZE', 'RSS', 'WCHAN', 'PC', '', 'NAME']

        for line in lines:
            # Format:
            tokens = [i for i in line.split(' ') if i.strip()]

            if len(tokens) != len(outputHeaders):
                continue

            processes.append(ProcessInfo(int(tokens[1]), tokens[-1]))

        return processes

    def getServices(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        res = self.shell('service list', timeoutMs)

        if not res:
            return None

        services = []

        for line in res.splitlines(False):
            if '[' in line:
                name = line.split(':')[0].split('\t')[1]

                interface = line.split('[')[1].split(']')[0]

                services.append(ServiceInfo(name, interface))

        return services

    def getPackages(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        res = self.shell('pm list packages', timeoutMs)

        if not res:
            return None

        packages = []

        for line in res.splitlines(False):
            packages.append(PackageInfo(line.split(':')[1]))

        return packages

    def getInstrumentations(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        # # instrumentation:com.iwedia.comedia.test/com.zutubi.android.junitreport.JUnitReportTestRunner (target=com.iwedia.comedia.test)
        res = self.shell('pm list instrumentation')

        if res == None:
            return None

        instrumentations = []

        for line in res.splitlines(False):
            package = line.split(':')[1].split('/')[0]
            className = line.split('/')[1].split(' ')[0]
            target = line.split('=')[1][:-1]

            instrumentations.append(InstrumentationInfo(package, className, target))

        return instrumentations

    def getProductModel(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        return self.shell('getprop ro.product.model').strip()

    def ping(self):
        magic = 42

        res = self.shell('echo %d' % magic, timeoutMs=5).strip()

        if res != str(magic):
            logger.error('Ping failed: %r != %r' % (res, str(magic)))
            return False

        return True

    def getMemoryInfo(self):
        # Otherwise use /proc/meminfo
        res = self.shell('cat /proc/meminfo')

        memTotal = 0
        memFree = 0

        for line in res.splitlines(False):
            if 'MemFree' in line:
                memFree = int(line.split(' ')[-2])
            elif 'MemTotal' in line:
                memTotal = int(line.split(' ')[-2])

        return MemoryInfo(memTotal, memTotal - memFree, memFree)

    def getProp(self, prop, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        return self.shell('getprop %s' % prop, timeoutMs)

    def saveScreenshot(self, destination, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        tmpFilePath = '/sdcard/.__tmp_screencap.png'
        self.shell('screencap -p %s' % tmpFilePath)

        if not self.fileExists(tmpFilePath, timeoutMs):
            raise RuntimeError('Error creating remote file %r' % tmpFilePath)

        self.pull(tmpFilePath, destination, timeoutMs)

        self.deleteFile(tmpFilePath)
