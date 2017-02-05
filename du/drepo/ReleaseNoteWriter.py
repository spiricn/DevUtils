from du.drepo.Gerrit import COMMIT_TYPE_MERGED, COMMIT_TYPE_PULL, COMMIT_TYPE_CP, COMMIT_TYPE_UNKOWN


class ReleaseNotesWriterBase:
    def __init__(self):
        self._notes = ''

    def start(self, manifest):
        raise NotImplementedError()

    def startProject(self, proj):
        raise NotImplementedError()

    def endProject(self):
        raise NotImplementedError()

    def addChange(self, number, ps, title, commitType):
        raise NotImplementedError()

    def end(self):
        raise NotImplementedError()

    def write(self, string):
        self._notes += string

    @property
    def notes(self):
        return self._notes

class ReleaseNotesTextWriter(ReleaseNotesWriterBase):
    def __init__(self, manifest):
        ReleaseNotesWriterBase.__init__(self)
        self._manifest = manifest

    def start(self):
        pass

    def startProject(self, proj):
        self.write(proj.url + '\n')

    def endProject(self):
        pass

    def addChange(self, number, ps, title, commitType):
        if commitType == COMMIT_TYPE_MERGED:
            typeStr = 'MERGED'
        elif commitType == COMMIT_TYPE_PULL:
            typeStr = 'PULLED'
        elif commitType == COMMIT_TYPE_CP:
            typeStr = 'PICKED'
        else:
            typeStr = '?'

        self.write(' + %d/%d : %s [%s]\n' % (number, ps, title, typeStr))

    def end(self):
        pass

class ReleaseNotesHtmlWriter(ReleaseNotesWriterBase):
    DEFAULT_TITLE = 'Release Notes'

    def __init__(self, manifest):
        ReleaseNotesWriterBase.__init__(self)
        self._manifest = manifest

    def start(self):
        self.write('<html><head>')

        self.write('<title>%s</title>' % self.DEFAULT_TITLE)

        self.write('<style>')
        self.write('font-family: "Courier New", Courier, "Lucida Sans Typewriter", "Lucida Typewriter", monospace;')
        self.write('font-style: normal;')
        self.write('font-variant: normal;')

        self.write('</style>')

        self.write('</head><body>')

        self.write('<hr/>')

        self.write('<table>')
        for idx, proj in enumerate(self._manifest.projects):

            self.write('<tr>')
            self.write('<td>%d.</td>' % (idx + 1))
            self.write('<td><a href="#%s">%s</a></td>' % (proj.name, proj.name))
            self.write('</tr>')

        self.write('</table>')

    def startProject(self, proj):
        self._proj = proj
        self._remoteHttpUrl = 'http://' + self._proj.remote.server

        projLink = self._remoteHttpUrl + '/#/admin/projects/%s' % proj.name
        branchLink = self._remoteHttpUrl + '/#/q/status:open+project:%s+branch:%s' % (proj.name, proj.branch)

        self.write('<hr/><br/>')

        self.write('<h3>')
        self.write('<a name="%s" href="%s" target="_blank">%s</a>' % (proj.name, projLink, proj.name))
        self.write(' ( <a href="%s" target="_blank">%s</a> )' % (branchLink, proj.branch))
        self.write('</h3>')

        self.write('<table>')

    def endProject(self):
        self.write('</table><br/>')

    def addChange(self, number, ps, title, commitType):
        typeColorMap = {
            COMMIT_TYPE_PULL : '#7cff92',
            COMMIT_TYPE_CP : '#f4dc42',
            COMMIT_TYPE_MERGED : '#FFFFFF',
            COMMIT_TYPE_UNKOWN : '#ce1414',
        }

        if commitType in typeColorMap:
            self.write('<tr bgcolor="%s">' % typeColorMap[commitType])
        else:
            self.write('<tr>')

        changeLink = self._remoteHttpUrl + '/#/c/%d/%d' % (number, ps)


        self.write('<td>%d</td>' % number)
        self.write('<td>%d</td>' % ps)
        self.write('<td><a href="%s" target="_blank"> %s </a> </td>' % (changeLink, title))

        self.write('</td>')

        self.write('</tr>')

    def end(self):
        self.write('<hr/')
        self.write('</body></html>')
