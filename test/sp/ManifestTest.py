import unittest

from du.smartpush.ArtifactManifest import ArtifactManifest


class ManifestTest(unittest.TestCase):
    def setUp(self):
        pass

    def testBasic(self):
        manifestSource = '''\
def getArtifacts():
    # Variable exposed by us
    print('My var test: %r' % MY_VAR)

    # Make sure it's accessible without importing
    print(Artifact)

    artifacts = []

    artifacts += [ Artifact('source', 'dest', 0) ]
    artifacts += [ Artifact('source', 'dest', 0) ]
    artifacts += [ Artifact('source', 'dest', 0) ]

    return artifacts

'''

        env = {'MY_VAR' : 'myvar'}
        manifest = ArtifactManifest.parseSource(manifestSource, env)

        artifcats = manifest.artifacts

        self.assertEqual(3, len(artifcats))


    def testError(self):
        manifestSource = '''\
        ERROR
'''

        try:
            ArtifactManifest.parseSource(manifestSource)
            self.fail()
        except:
            pass
