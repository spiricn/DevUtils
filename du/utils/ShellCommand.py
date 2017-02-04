import os
import subprocess
import sys
import threading

class ShellFactory:
    def __init__(self, commandOutput, raiseOnError):
        self._commandOutput = commandOutput
        self._raiseOnError = raiseOnError

    def spawn(self, command, cwd=None):
        cmd = ShellCommand(command, cwd, self._commandOutput, self._raiseOnError)
        cmd.start()
        return cmd

class ShellCommand:
    RETURN_CODE_OK = 0
    OUTPUT_ENCODING = 'ascii'

    def __init__(self, command, cwd=None, commandOutput=True, raiseOnError=False):
        if isinstance(command, str):
            self._command = command.split(' ')
        else:
            self._command = command

        self._cwd = cwd
        self._commandOutput = commandOutput
        self._raiseOnError = raiseOnError

        self._stdout = b''
        self._stderr = b''

    @staticmethod
    def run(command, cwd=None):
        cmd = ShellCommand(command, cwd, commandOutput=True, raiseOnError=True)
        cmd.start()
        return cmd

    def start(self):
        return self._run()

    def _run(self):
        if self._commandOutput:
            sys.stdout.write(' '.join(self._command) + '\n')

        if self._cwd != None and not os.path.isdir(self._cwd):
            raise RuntimeError('Invalid cwd: %r' % self._cwd)

        self._pipe = subprocess.Popen(self._command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self._cwd)

        if self._commandOutput:
            stderrThread = threading.Thread(target=self._pipeRead, args=(self._pipe.stderr, sys.stderr))
            stderrThread.start()

            stdoutThread = threading.Thread(target=self._pipeRead, args=(self._pipe.stdout, sys.stdout))
            stdoutThread.start()

        self._pipe.wait()

        if self._commandOutput:
            stderrThread.join()
            stdoutThread.join()
        else:
            self.stderr = self._pipe.stderr.read()
            self.stdout = self._pipe.stdout.read()

        if self.rc != self.RETURN_CODE_OK and self._raiseOnError:
            message = ''

            message += 'Command failed\n'
            message += '\tcommand: %r\n' % ' '.join(self._command)
            message += '\tcode: %d\n' % self.rc
            message += self.stderrStr

            raise RuntimeError(message)

    def _pipeRead(self, stream, output):
        for i in iter(stream):
            output.write(i)
            output.flush()

            if output == sys.stderr:
                self._stderr += i
            else:
                self._stdout += i

    @property
    def rc(self):
        return self._pipe.returncode

    @property
    def stderr(self):
        return self._stderr

    @property
    def stdout(self):
        return self._stdout

    @property
    def stdoutStr(self):
        return self.stdout.encode(self.OUTPUT_ENCODING)

    @property
    def stderrStr(self):
        return self.stderr.encode(self.OUTPUT_ENCODING)
