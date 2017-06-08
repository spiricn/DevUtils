from du.drepo.Manifest import Manifest
from test.TestBase import TestBase


class ManifestTest(TestBase):
    def setUp(self):
        pass

    def testCustomVar(self):
        manifestSource = '''\
remotes = {
   'remote_1' : 'ssh://user@server1:29418',
   'remote_2' : 'ssh://user@server2:29418'
}

projects = {
    'project1' : {
        'remote' : 'remote_1',
        'path' : '/home/test',
        'branch' : 'master',
         'opts' : [OPT_CLEAN, OPT_RESET],
     },

    'project2' : {
        'remote' : 'remote_2',
        'path' : '/home/test',
        'branch' : 'dev',
         'opts' : [OPT_CLEAN, OPT_RESET],
     },
}

build = 'main'

builds = {
    'main' : {
        'root' : '/home/dev/root',

       'final_touches' : {
            'project1' : 14303,
            'project2' : 14507,
        },
    },

    'test' : {
        'root' : '/home/dev/root',
    },
}
'''
        m = Manifest(manifestSource)

        self.assertEqual(2, len(m.remotes))
        self.assertEqual(2, len(m.builds))

        self.assertEqual('main', m.build.name)
        self.assertEqual(2, len(m.projects))
