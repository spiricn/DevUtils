from adb.adb_commands import AdbCommands, M2CryptoSigner
import os


DEFAULT_COMMAND_TIMEOUT_MS = 500

class GooglePythonADB(object):
    '''
    Google python-adb ADB backend
    '''

    DEFAULT_ADB_KEY = '~/.android/adbkey'

    def __init__(self, impl):
        self._impl = impl

    @classmethod
    def _connect(cls, addr, port, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        return AdbCommands.ConnectDevice(None, '%s:%d' % (addr, port), rsa_keys=[M2CryptoSigner(os.path.expanduser(cls.DEFAULT_ADB_KEY))], default_timeout_ms=timeoutMs)

    def shell(self, command, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        return self._impl.Shell(command, timeout_ms=timeoutMs)

    def disconnect(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        self._impl.Close()

    def reboot(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        self._impl.Reboot(timeout_ms=timeoutMs)

    def pull(self, source, dest, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        self._impl.Pull(source, dest, timeout_ms=timeoutMs)

    def push(self, source, dest, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        self._impl.Push(source, dest, timeout_ms=timeoutMs)

    def root(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        self._impl.Root()

    def remount(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        self._impl.Remount()

