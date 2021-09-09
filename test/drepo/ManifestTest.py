from du.drepo.manifest.Parser import Parser, ManifestParseError, ManifestLogicError
from test.TestBase import TestBase
from du.drepo.manifest.Common import ProjectOption


class ManifestTest(TestBase):
    def testParserMalformed(self):
        with self.assertRaises(ManifestParseError) as context:
            Parser.parseString("error")

        with self.assertRaises(ManifestParseError) as context:
            Parser.parseString("!@#$")

    def testParserMinimal(self):
        test = """
remotes = {
}

builds = {
    'test' : {
        'root' : ''
    }
}

projects = [
]

build = 'test'
"""
        self.assertTrue(Parser.parseString(test))

    def testInvalidBuildName(self):
        test = """
remotes = {
}

builds = {
    'test' : {
        'root' : ''
    }
}

projects = [
]

build = 'asdf'
"""

        with self.assertRaises(ManifestLogicError) as context:
            Parser.parseString(test)

    def testMissingRemote(self):
        test = """
remotes = {
}

builds = {
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'libiwu',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'test'
"""
        with self.assertRaises(ManifestLogicError) as context:
            Parser.parseString(test)

    def testInvalidCherrypicksType(self):
        test = """
remotes = {
}

builds = {
    'test' : {
        'root' : '',
        'cherrypicks' : []
    }
}

projects = [
]

build = 'test'
"""

        with self.assertRaises(ManifestParseError) as context:
            Parser.parseString(test)

    def testInvalidCherrypicksChangeType(self):
        test = """
remotes = {
    'iwedia' : 'ssh://dummy@gerrit.iwedia.com:29418'
}

builds = {
    'test' : {
        'root' : '',
        'cherrypicks' : {
            'libiwu' : ['asdf']
        }
    }
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'project_path',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'test'
"""

        with self.assertRaises(ManifestParseError) as context:
            Parser.parseString(test)

    def testInvalidCherrypicksProjectName(self):
        test = """
remotes = {
    'iwedia' : 'ssh://dummy@gerrit.iwedia.com:29418'
}

builds = {
    'test' : {
        'root' : '',
        'cherrypicks' : {
            'missing' : ['asdf']
        }
    }
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'project_path',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'test'
"""

        with self.assertRaises(ManifestParseError) as context:
            Parser.parseString(test)

    def testInivalidTagType(self):
        test = """
remotes = {
    'iwedia' : 'ssh://dummy@gerrit.iwedia.com:29418'
}

builds = {
    'test' : {
        'root' : '',
        'tags' : {
            'libiwu' : 5
        }
    }
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'project_path',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'test'
"""

        with self.assertRaises(ManifestParseError) as context:
            Parser.parseString(test)

    def testInivalidTagProjectName(self):
        test = """
remotes = {
    'iwedia' : 'ssh://dummy@gerrit.iwedia.com:29418'
}

builds = {
    'test' : {
        'root' : '',
        'tags' : {
            'missing' : 'ok'
        }
    }
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'project_path',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'test'
"""

        with self.assertRaises(ManifestLogicError) as context:
            Parser.parseString(test)

    def testInvalidCheckoutTouchType(self):
        test = """
remotes = {
    'iwedia' : 'ssh://dummy@gerrit.iwedia.com:29418'
}

builds = {
    'test' : {
        'root' : '',
        'checkouts' : {
            'libiwu' : 'invalid'
        }
    }
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'project_path',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'test'
"""

        with self.assertRaises(ManifestParseError) as context:
            Parser.parseString(test)

    def testInvalidCheckoutProjectName(self):
        test = """
remotes = {
    'iwedia' : 'ssh://dummy@gerrit.iwedia.com:29418'
}

builds = {
    'test' : {
        'root' : '',
        'checkouts' : {
            'missing' : 1234
        }
    }
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'project_path',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'test'
"""

        with self.assertRaises(ManifestLogicError) as context:
            Parser.parseString(test)

    def testFull(self):
        test = """
remotes = {
    'iwedia' : 'ssh://dummy@gerrit.iwedia.com:29418'
}

builds = {
    'main' : {
        'checkouts' : {
            'libiwu' : 1234
        },

        'cherrypicks' : {
            'libiwu' : [1234, 5678]
        },

        'tags' : {
            'libiwu' : 'tag_name'
        },
        'root' : 'build/root'
    }
}

projects = [
    {
        'name' : 'libiwu',
        'remote' : 'iwedia',
        'path' : 'project_path',
        'branch' : 'master',
        'opts' : [OPT_RESET],
    }
]

build = 'main'
"""

        manifest = Parser.parseString(test)
        self.assertTrue(manifest)

        # Remotes
        self.assertEqual(len(manifest.remotes), 1)
        self.assertEqual(manifest.remotes[0].name, "iwedia")
        self.assertEqual(
            manifest.remotes[0].fetch, "ssh://dummy@gerrit.iwedia.com:29418"
        )

        # Projects
        self.assertEqual(len(manifest.projects), 1)
        self.assertEqual(manifest.projects[0].name, "libiwu")
        self.assertEqual(manifest.projects[0].remote, manifest.remotes[0])
        self.assertEqual(manifest.projects[0].path, "project_path")
        self.assertEqual(manifest.projects[0].branch, "master")
        self.assertEqual(manifest.projects[0].opts, [ProjectOption.RESET])

        # Builds
        self.assertEqual(len(manifest.builds), 1)

        self.assertEqual(manifest.builds[0], manifest.selectedBuild)
        self.assertEqual(manifest.selectedBuild.name, "main")
        self.assertEqual(manifest.selectedBuild.checkouts, {manifest.projects[0]: 1234})
        self.assertEqual(
            manifest.selectedBuild.cherrypicks, {manifest.projects[0]: [1234, 5678]}
        )
        self.assertEqual(
            manifest.selectedBuild.tags, {manifest.projects[0]: "tag_name"}
        )
        self.assertEqual(manifest.selectedBuild.root, "build/root")
