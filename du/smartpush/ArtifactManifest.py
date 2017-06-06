from copy import deepcopy

from du.smartpush.Artifact import Artifact


class ArtifactManifest:
    GET_ARTIFACTS_FNC_NAME = 'getArtifacts'

    def __init__(self, artifacts):
        self._artifactSets = {}

        if isinstance(artifacts, list):
            # Just a list of artifacts
            self._artifactSets[None] = artifacts

        elif isinstance(artifacts, dict):
            for key, value in artifacts.items():
                if not isinstance(key, str):
                    raise RuntimeError('Expected string for set key, got %r' % str(key))

                if not isinstance(value, list):
                    raise RuntimeError('Expected list for set value, got %r' % str(value))

                self._artifactSets[key] = value

        else:
            raise RuntimeError('Invalid artifact list value: %r' % str(artifacts))

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

    def getArtifactSet(self, name=None):
        return self._artifactSets[name] if name in self._artifactSets else None

    @property
    def artifactSets(self):
        return self._artifactSets.keys()
