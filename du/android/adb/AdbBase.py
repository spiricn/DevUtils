DEFAULT_COMMAND_TIMEOUT_MS = 500

class AdbBase(object):
    def __init__(self):
        pass

    def shell(self, command, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        raise RuntimeError('Not implemented')

    def disconnect(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        raise RuntimeError('Not implemented')

    def reboot(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        raise RuntimeError('Not implemented')

    def pull(self, source, dest, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        raise RuntimeError('Not implemented')

    def push(self, source, dest, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        raise RuntimeError('Not implemented')

    def root(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        raise RuntimeError('Not implemented')

    def remount(self, timeoutMs=DEFAULT_COMMAND_TIMEOUT_MS):
        raise RuntimeError('Not implemented')

    def connect(self, timeoutMs, **kwargs):
        raise RuntimeError('Not implemented')
