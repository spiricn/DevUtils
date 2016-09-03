class ReleaseNotesWriterBase:
    def __init__(self):
        self._notes = ''

    def start(self):
        raise NotImplementedError()

    def startProject(self, proj):
        raise NotImplementedError()

    def endProject(self):
        raise NotImplementedError()

    def addChange(self, number, ps, title):
        raise NotImplementedError()

    def end(self):
        raise NotImplementedError()

    def write(self, string):
        self._notes += string

    @property
    def notes(self):
        return self._notes

class ReleaseNotesTextWriter(ReleaseNotesWriterBase):
    def __init__(self):
        ReleaseNotesWriterBase.__init__(self)

    def start(self):
        pass

    def startProject(self, proj):
        self.write(proj.url + '\n')

    def endProject(self):
        pass

    def addChange(self, number, ps, title):
        self.write(' + %d/%d : %s\n' % (number, ps, title))

    def end(self):
        pass

class ReleaseNotesHtmlWriter(ReleaseNotesWriterBase):
    def __init__(self, manifest):
        ReleaseNotesWriterBase.__init__(self)
        self._manifest = manifest

    def start(self):
        self.write('<html><body>')

    def startProject(self, proj):
        self._proj = proj
        self._remoteHttpUrl = 'http://' + self._manifest.getRemote(self._proj.remote).fetch.split('/')[-1].split(':')[0]

        projLink = self._remoteHttpUrl + '/#/admin/projects/%s' % proj.name

        self.write('<hr/><br/>')
        self.write('<table>')

        self.write('<tr>')

        self.write('<th>Project</th>')
        self.write('<td colspan="2"><a href="%s" target="_blank">%s</a></td></tr>' % (projLink, proj.name))

        self.write('<tr><td><br/></td></tr>')

    def endProject(self):
        self.write('</table><br/>')

    def addChange(self, number, ps, title):
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
