import logging

from du.smartpush.SmartPushAppBase import SmartPushAppBase
from du.smartpush.ssh.SshArtifactInstaller import SshArtifactInstaller


logger = logging.getLogger(__name__.split('.')[-1])

class SshSmartPushApp(SmartPushAppBase):
    def __init__(self):
        SmartPushAppBase.__init__(self)

    def createArgParser(self, parser):
        parser.add_argument('-remote_server')
        parser.add_argument('-remote_user')

    def execute(self, args, artifacts, timestampFile, force):
        if not args.remote_server:
            raise RuntimeError('server argument missing')

        if not args.remote_user:
            raise RuntimeError('user argument missing')

        ai = SshArtifactInstaller(artifacts, timestampFile, args.remote_server, args.remote_user)

        return ai.install(force)

    @staticmethod
    def getProtocolName():
        return 'ssh'
