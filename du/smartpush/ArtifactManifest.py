from copy import deepcopy

from du.smartpush.Artifact import Artifact


class ArtifactManifest:
    GET_ARTIFACTS_FNC_NAME = 'getArtifacts'

    def __init__(self, path):
        self._path = path

    def parse(self, env=None):
        if env:
            env = deepcopy(env)
        else:
            env = {}

        env['Artifact'] = Artifact

        with open(self._path, 'rb') as fileObj:
            exec(fileObj.read(), env)

            if self.GET_ARTIFACTS_FNC_NAME not in env:
                raise RuntimeError('Function %r not found in %r' % (self.GET_ARTIFACTS_FNC_NAME, self._path))

        self._env = env

        return self.artifacts

    @property
    def artifacts(self):
        return self._env[self.GET_ARTIFACTS_FNC_NAME]()