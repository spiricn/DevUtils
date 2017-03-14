import json

from du.utils.ShellCommand import ShellFactory


COMMIT_TYPE_INVALID, \
COMMIT_TYPE_UNKOWN, \
COMMIT_TYPE_CP, \
COMMIT_TYPE_PULL, \
COMMIT_TYPE_MERGED = range(5)

class Gerrit:
    CHANGE_ID_LENGTH = 41

    def __init__(self, username, port, server, sf=None):
        self._username = username
        self._port = port
        self._server = server

        if not sf:
            sf = ShellFactory(raiseOnError=True, commandOutput=False)

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

    def getChange(self, change):
        return self.query(change=change)

    def getPatchsets(self, change):
        return self.query('--patch-sets', change=change)['patchSets']

    def getPatchset(self, change, ps=None):
        if ps == None:
            res = self.query('--current-patch-set', change=change)

            return res['currentPatchSet'] if 'currentPatchSet' in res else None
        else:
            if not isinstance(ps, int):
                raise RuntimeError('Invalid patchset number: %r' % str(ps))

            patchsets = self.getPatchsets(change)

            for i in patchsets:
                if i['number'] == str(ps):
                    return i

            return None

