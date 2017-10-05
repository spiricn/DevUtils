import logging
import os

from du.drepo.Gerrit import Gerrit, COMMIT_TYPE_INVALID, COMMIT_TYPE_CP, COMMIT_TYPE_MERGED, COMMIT_TYPE_PULL, COMMIT_TYPE_UNKOWN
from du.drepo.ReleaseNoteWriter import ReleaseNotesHtmlWriter
from du.utils import Git
from du.utils.ShellCommand import ShellFactory


logger = logging.getLogger(__name__.split('.')[-1])

class ReleaseNoteGenerator:
    def __init__(self, manifest):
        self._manifest = manifest
        self._sf = ShellFactory(raiseOnError=True, commandOutput=True)

    def run(self, outputFile, writer=ReleaseNotesHtmlWriter):
        writer = writer(self._manifest)

        writer.start()

        for proj in self._manifest.projects:
            logger.debug('processing %r ..' % proj.name)

            localDir = os.path.join(self._manifest.root, proj.path)

            projectTag = None

            try:
                projectTag = Git.getTag(proj.path)
            except Exception as e:
                logger.warn('Could not get project tag: %s' % str(e))

            writer.startProject(proj, projectTag)

            gr = Gerrit(proj.remote.username, proj.remote.port, proj.remote.server, self._sf)

            # Get commit log of the project
            log = Git.getLog(localDir)[:-1]

            # Number of merged commits to display
            historyLength = 5

            for logItem in log:
                # Full commit message
                message = Git.getCommitMessage(localDir, logItem.hash)

                # Gerrit change ID extracted from the message
                changeId = Git.getCommitGerritChangeId(message)

                commitType = COMMIT_TYPE_INVALID

                if not changeId:
                    logger.warning('could not find changeId, for commit %r' % logItem.hash)
                    commitType = COMMIT_TYPE_UNKOWN

                if commitType != COMMIT_TYPE_UNKOWN:
                    patchsets = gr.getPatchsets(changeId)
                    if not patchsets:
                        logger.warning('could not acquire patchset info from gerrit, for commit %r' % logItem.hash)
                        commitType = COMMIT_TYPE_UNKOWN

                if commitType != COMMIT_TYPE_UNKOWN:
                    changeInfo = gr.getChange(changeId)
                    if not changeInfo:
                        logger.warning('could not acquire change info from gerrit, for commit %r' % logItem.hash)
                        commitType = COMMIT_TYPE_UNKOWN

                if commitType != COMMIT_TYPE_UNKOWN:
                    changeNumber = int(changeInfo['number'])

                    changePatchset = -1

                    for i in patchsets:
                        if i['revision'] == logItem.hash:
                            # We found the remote patchset with the exact same hash as this one (so it's either pulled or merged)
                            changePatchset = int(i['number'])

                            # Check if is merged
                            if changeInfo['status'] == 'MERGED':
                                commitType = COMMIT_TYPE_MERGED
                            else:
                                commitType = COMMIT_TYPE_PULL

                    if commitType == COMMIT_TYPE_INVALID:
                        # Try to find a patchset number from the manifest
                        for manifestPs in self._manifest.getCherrypicks(proj):
                            if manifestPs.number == changeNumber:
                                commitType = COMMIT_TYPE_CP

                                if manifestPs.ps != None:
                                    changePatchset = manifestPs.ps
                                else:
                                    # Assume it's the latest one
                                    changePatchset = int(gr.getPatchset(changeId)['number'])
                else:
                    changeNumber = -1
                    changePatchset = 0

                logger.debug('\tadding change: %s %s' % (str(changeNumber), str(changePatchset)))

                writer.addChange(changeNumber, changePatchset, logItem.title, commitType)

                if commitType == COMMIT_TYPE_MERGED:
                    historyLength -= 1

                if historyLength == 0:
                    break

            writer.endProject()

        writer.end()

        with open(outputFile, 'w') as fileObj:
            fileObj.write(writer.notes)

            logger.debug('notes written to %r' % outputFile)
