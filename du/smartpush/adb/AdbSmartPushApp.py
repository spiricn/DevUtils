import logging

from du.smartpush.SmartPushAppBase import SmartPushAppBase
from du.smartpush.adb.AdbArtifactInstaller import AdbArtifactInstaller


logger = logging.getLogger(__name__.split('.')[-1])

class AdbSmartPushApp(SmartPushAppBase):
    def __init__(self):
        SmartPushAppBase.__init__(self)

    def createArgParser(self, parser):
        parser.add_argument('-android_root')
        parser.add_argument('-product_name')

    def parseArgs(self, args):
        if not args.android_root:
            logger.error('android root not provided')
            return False

        if not args.product_name:
            logger.error('android product name not provided')
            return False

        return True

    def execute(self, args, artifacts, timestampFile, force):
        ai = AdbArtifactInstaller(artifacts, args.android_root, args.product_name, timestampFile)

        return ai.install(force)

    @staticmethod
    def getProtocolName():
        return 'adb'
