from du.smartpush.SmartPushAppBase import SmartPushAppBase
from du.smartpush.file.FileArtifactInstaller import FileArtifactInstaller


class FileSmartPushApp(SmartPushAppBase):
    def __init__(self):
        SmartPushAppBase.__init__(self)

    def createArgParser(self, parser):
        pass

    def execute(self, args, artifacts, timestampFile, force):
        ai = FileArtifactInstaller(artifacts, timestampFile)

        return ai.install(force)
