from collections import namedtuple


InstallStatistics = namedtuple('InstallStatistics', 'numUpToDate, numInstalled, numErrors')

class SmartPushAppBase:
    def __init__(self):
        pass

    def createArgParser(self, parser):
        raise NotImplementedError('Not implemented')

    def execute(self, args, artifacts, timestampFile, force):
        raise NotImplementedError('Not implemented')
