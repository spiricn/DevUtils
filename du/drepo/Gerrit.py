import json

from du.utils.ShellCommand import ShellCommand


class Gerrit:
    def __init__(self, username, port, server, sf):
        self._username = username
        self._port = port
        self._server = server
        self._sf = sf

    def query(self, *args, **kwargs):
        query = ''

        for key, val in kwargs.items():
            query += '%s:%s ' % (str(key), str(val))


        for arg in args:
            query += str(arg) + ' '

        query += '--format=JSON'

        cmd = self._sf.spawn(['ssh', '-p', str(self._port), self._username + '@' + self._server, 'gerrit', 'query', query])

        return json.loads(cmd.stdout.splitlines()[0])

    def getPatchset(self, changeNumber, psNumber=None):
        if psNumber == None:
            res = self.query('--current-patch-set', change=changeNumber)

            return res['currentPatchSet']
        else:
            res = self.query('--patch-sets', change=changeNumber)

            return res['patchSets'][str(psNumber)]

