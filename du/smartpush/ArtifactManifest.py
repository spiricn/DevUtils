from copy import deepcopy

from du.smartpush.Artifact import Artifact


class ArtifactManifest:
    GET_ARTIFACTS_FNC_NAME = 'getArtifacts'

    def __init__(self, artifacts):
        self._artifacts = artifacts

    @staticmethod
    def parseSource(source, env=None):
        if env:
            env = deepcopy(env)
        else:
            env = {}

        env['Artifact'] = Artifact

        exec(bytes(source, 'utf-8'), env)

        if ArtifactManifest.GET_ARTIFACTS_FNC_NAME not in env:
            raise RuntimeError('Function %r not found' % (ArtifactManifest.GET_ARTIFACTS_FNC_NAME))

        artifacts = env[ArtifactManifest.GET_ARTIFACTS_FNC_NAME]()

        return ArtifactManifest(artifacts)

    @staticmethod
    def parseFile(path, env=None):
        with open(path, 'r') as fileObj:
            source = fileObj.read()

            return ArtifactManifest.parseSource(source, env)

    @property
    def artifacts(self):
        return self._artifacts
