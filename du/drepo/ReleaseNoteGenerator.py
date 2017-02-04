import logging
import os

from du.drepo.Gerrit import Gerrit
from du.drepo.ReleaseNoteWriter import ReleaseNotesHtmlWriter
from du.utils import Git
from du.utils.ShellCommand import ShellFactory


logger = logging.getLogger(__name__.split('.')[-1])

class ReleaseNoteGenerator:
    def __init__(self, manifest):
        self._manifest = manifest
        self._sf = ShellFactory(raiseOnError=True, commandOutput=False)

    def run(self, outputFile, writer=ReleaseNotesHtmlWriter):
        writer = writer(self._manifest)

        historyLength = 15

        writer.start()

        for proj in self._manifest.projects:
            gr = Gerrit(proj.remote.username, proj.remote.port, proj.remote.server, self._sf)

            logger.debug('for %s ..' % proj.name)
            writer.startProject(proj)

            localDir = os.path.join(self._manifest.root, proj.path)

            log = Git.getLog(localDir)[:-1]

            cherryPickHashes = []

            for change in reversed(self._manifest.getCherrypicks(proj)):
                # Get cherry pick remote hash
                hash = gr.getPatchset(change.number, change.ps)['revision']

                # Get title
                res = self._sf.spawn(['git', 'log', '--format=%s', '-n', '1', hash], os.path.join(self._manifest.root, proj.path))
                title = res.stdoutStr.strip()

                # Get patchset
                ps = change.ps
                if ps == None:
                    ps = int(gr.getPatchset(change.number)['number'])

                writer.addChange(change.number, ps, title, cherryPick=True)

                cherryPickHashes.append(hash)

                entry = log.pop(0)

                logger.debug('cp %s %s' % (entry.title, title))

            maxHistory = 15

            for entry in log:
#                 remoteItem = Git.findRemote(proj.url, entry.hash, remotes)
#                 if remoteItem:
#                     writer.addChange(remoteItem.number, remoteItem.patchset, entry.title, cherryPick=False)
#                     historyLength -= 1
#
#                     if not historyLength:
#                         break
#                 else:
#                     changeId = Git.getCommitGerritChangeId(Git.getCommitMessage(localDir, entry.hash))
#
#                     logger.warning('Could not find change for %s, changeId=%s' % (str(entry), changeId))
#                     writer.addChange(-1, -1, entry.title, cherryPick=False)
#
                maxHistory -= 1
#
                if maxHistory == 0:
                    break

            writer.endProject()

        writer.end()

        with open(outputFile, 'wb') as fileObj:
            fileObj.write(writer.notes)

            logger.debug('notes written to %r' % outputFile)
