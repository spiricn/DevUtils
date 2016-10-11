from du.android.adb.AdbBase import AdbBase, DEFAULT_COMMAND_TIMEOUT_MS
from du.utils.ShellCommand import ShellCommand


class BinaryAdb(AdbBase):
    ADB = '/usr/bin/adb'

    def __init__(self, **kwargs):
        super(BinaryAdb, self).__init__()

        self._adb = self.ADB

        self._addr = kwargs.pop('address')
        self._port = kwargs.pop('port')

    @property
    def _id(self):
        return '%s:%d' % (self._addr, self._port)

    @property
    def _baseCommand(self):
        return [self._adb, '-s', self._id]

    def shell(self, command, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        return ShellCommand.run(self._baseCommand + ['shell', command]).stdoutStr

    def disconnect(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        ShellCommand.run(self._baseCommand + ['disconnect'])

    def reboot(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        ShellCommand.run([self._adb, 'reboot'])

    def pull(self, source, dest, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        ShellCommand.run([self._adb, 'pull', source, dest])

    def push(self, source, dest, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        ShellCommand.run([self._adb, 'push', source, dest])

    def root(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        ShellCommand.run(self._baseCommand + ['root'])

        self.disconnect()
        self.connect()

    def remount(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        ShellCommand.run([self._adb, 'remount'])

    def connect(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        ShellCommand.run([self._adb, 'disconnect'])

        res = ShellCommand.run([self._adb, 'connect', '%s:%d' % (self._addr, self._port)])

        if res.stdoutStr.strip() != 'connected to %s:%d' % (self._addr, self._port):
            raise RuntimeError('command failed')


adb = BinaryAdb(address='192.168.234.39', port=5555)
print(adb.connect())
adb.root()
print('%r' % adb.shell('ls'))

print(adb.disconnect())
