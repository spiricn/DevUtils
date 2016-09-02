import argparse
from collections import namedtuple
import os
import shutil
import subprocess
import sys

CommandRes = namedtuple('CommandRes', 'stdout, stderr, rc')


def shellCommand(command, cwd=None):
    if isinstance(command, str):
        command = command.split(' ')

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

    res = pipe.communicate()

    cmdRes = CommandRes(res[0], res[1], pipe.returncode)

    if cmdRes.rc != 0:
        raise RuntimeError('Command failed %r:\n%s' % (' '.join(command), cmdRes.stderr))

    print(cmdRes.stdout.encode('ascii'))
    print(cmdRes.stderr.encode('ascii'))

    return cmdRes


def updateManifest(rootDir, manifest):
    res = shellCommand(['mktemp', '-d'])
    if res.rc != 0:
        raise RuntimeError('Command failed: %r' % res.stderr)

    tmpDirPath = res.stdout.encode('ascii').strip()

    repoRemoteDir = os.path.join(rootDir, '.repo_remote')

    repoLocalDir = os.path.join(tmpDirPath, '.repo_remote')

    res = shellCommand(['git', 'clone', repoRemoteDir], tmpDirPath)
    if res.rc != 0:
        raise RuntimeError('Command failed: %r' % res.stderr)

    with open(os.path.join(tmpDirPath, '.repo_remote', 'default.xml'), 'w') as fileObj:
        fileObj.write(manifest)


    shellCommand('git add default.xml', repoLocalDir)

    res = shellCommand('git diff --cached --name-only', repoLocalDir)
    if not res.stdout.encode('ascii').strip():
        print('nothing to commit')
    else:
        shellCommand('git commit -a -m "update"', repoLocalDir)
        shellCommand('git push origin master', repoLocalDir)

    shutil.rmtree(tmpDirPath)

def generateRepo(rootDir, manifest):
    repoRemoteDir = os.path.join(rootDir, '.repo_remote')

    if not os.path.exists(repoRemoteDir):
        os.makedirs(repoRemoteDir)

        shellCommand('git init --bare', cwd=repoRemoteDir)

    updateManifest(rootDir, manifest)

    repoDir = os.path.join(rootDir, '.repo')

    if not os.path.exists(repoDir):
        shellCommand('repo init -u ' + repoRemoteDir, rootDir)

    shellCommand('repo sync -j8', rootDir)

def getLatestPatchset(remoteUrl, change):
    patchsets = []

    for i in shellCommand('git ls-remote ' + remoteUrl).stdout.encode('ascii').splitlines():
        if '/%s/' % change in i:
            patchsets.append(int(i.split('/')[-1]))

    return max(patchsets)

def applyCherryPicks(rootDir, projectName, changes, remoteUrl):
    for change in changes:
        if isinstance(change, str) and '/' in change:
            changeNumber, patchset = change.split('/')
            changeNumber = int(changeNumber)
            patchset = int(patchset)
        else:
            changeNumber = int(change)
            patchset = getLatestPatchset(remoteUrl, changeNumber)

        shellCommand('repo download -c %s %d/%d' % (projectName, changeNumber, patchset), rootDir)


def generateManifest(manifestLocals):
    manifestXml = ''

    manifestXml += '<manifest>'

    for name, fetch in manifestLocals['remotes'].iteritems():
        manifestXml += '<remote name="%s" fetch="%s"/>' % (name, fetch)

    manifestXml += '<default revision="refs/heads/master" sync-j="4" />'

    for name, desc in manifestLocals['projects'].iteritems():
        manifestXml += '<project name="%s" remote="%s" path="%s" revision="refs/heads/%s"/>' % (name, desc['remote'], desc['path'], desc['branch'])

    manifestXml += '</manifest>'

    return manifestXml

def generateNotes(manifest):
    notes = ''
    
    for name, desc in manifest['projects'].iteritems():
        notes += name + '\n'
        
        shellCommand('git log', desc['path'])
    
    
    return notes
    
def process(manifest):
    manifestLocals = {}

    exec(manifest, manifestLocals)

    manifestXml = generateManifest(manifestLocals)

    rootDir = manifestLocals['root']

    generateRepo(rootDir, manifestXml)

    for name, desc in manifestLocals['projects'].iteritems():
        remoteUrl = manifestLocals['remotes'][desc['remote']] + '/' + name

        applyCherryPicks(rootDir, name, desc['cherry-picks'], remoteUrl)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('manifest')

    args = parser.parse_args()

    process(args.manifest)

    return 0

if __name__ == '__main__':
    sys.exit(main())
