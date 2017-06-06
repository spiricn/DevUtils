import unittest

from du.smartpush.ArtifactManifest import ArtifactManifest


class ManifestTest(unittest.TestCase):
    def setUp(self):
        pass

    def testCustomVar(self):
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

        artifcats = manifest.getArtifactSet()

        self.assertEqual(3, len(artifcats))

    def testSets(self):
        manifestSource = '''\
def getArtifacts():
    set1 = []

    set1 += [ Artifact('source', 'dest', 0) ]
    set1 += [ Artifact('source', 'dest', 0) ]
    set1 += [ Artifact('source', 'dest', 0) ]

    set2 = []

    set2 += [ Artifact('source', 'dest', 0) ]
    set2 += [ Artifact('source', 'dest', 0) ]



    return {'set1' : set1, 'set2' : set2}
'''

        manifest = ArtifactManifest.parseSource(manifestSource)

        self.assertEqual(2, len(manifest.artifactSets))

        self.assertTrue('set1' in manifest.artifactSets)
        self.assertTrue('set2' in manifest.artifactSets)

        self.assertEqual(3, len(manifest.getArtifactSet('set1')))
        self.assertEqual(2, len(manifest.getArtifactSet('set2')))

    def testError(self):
        manifestSource = '''\
        ERROR
'''

        try:
            ArtifactManifest.parseSource(manifestSource)
            self.fail()
        except:
            pass
