from du.Utils import shellCommand

class Ssh:
    def __init__(self, server, user):
        self._server = server
        self._user = user

    def push(self, source, destination):
        res = shellCommand(['scp', source, self._getRemoteDest(destination)])
        if res.rc != 0:
            raise RuntimeError('%r' % res.stderr)


    def _getRemoteDest(self, destination):
        return '%s@%s:%s' % (self._user, self._server, destination)

    def shell(self, command):
        return shellCommand(['ssh', '%s@%s' % (self._user, self._server)] + command)
