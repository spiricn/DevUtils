import logging
import os
import subprocess
import sys
import threading
import select
import time
import random

logger = logging.getLogger(__name__.split(".")[-1])


class CommandFailedException(Exception):
    """
    Exception thrown when a command failed with a non zero command
    """

    def __init__(self, command, message):
        """
        Constructor

        @param command Parent command
        @param message Detailed failure message
        """

        self._command = command
        self._message = message

    @property
    def command(self):
        return self._command

    def __str__(self):
        return self._message


class ShellCommand:
    # Return code indicating success
    RETURN_CODE_OK = 0

    # Output encoding when converting to string
    OUTPUT_ENCODING = "ISO-8859-1"

    # Type of output stream
    OUTPUT_STREAM_STDERR, OUTPUT_STREAM_STDOUT = range(2)

    # Default retry fixed time value
    DEFAULT_FIXED_RETRY_TIME_SEC = 0.1

    # Default retry range time value
    DEFAULT_RETRY_TIME_RANGE_SEC = (0.5, 3)

    # Number of fetch retries
    DEFAULT_NUM_RETRIES = 3

    def __init__(
        self,
        command,
        workingDirectory=None,
        raiseOnError=True,
        numRetries=1,
        randomRetry=False,
        retryRange=None,
        output=logger.debug,
    ):
        """
        Constructor

        @param command Command to execute
        @param workingDirectory Working directory in which the command shall get executed
        @param raiseOnError Indication if an exception should be thrown on command failure
        @param numRetries Number of attempts at executing a command if it fails
        @param randomRetry If set to True the attempts will be executed in random period defined by retryRange param
        @param retryRange If randomRetry == True: Tuple value with range values of minimum and maximum time (seconds)
        in which random retries will be performed,  If randomRetry == False: retryRange is treated as single integer
        value used for fixed retry interval
        @param output Log output function
        """

        self.__output = output

        # Input command
        if isinstance(command, str):
            self._command = command.split(" ")
        else:
            self._command = command

        # Working directory
        self._workingDirectory = workingDirectory

        # Indication if we should throw on error
        self._raiseOnError = raiseOnError

        # Nax number of retries
        self._numRetries = numRetries

        # Command code
        self._returnCode = None

        # Random command execution
        self._randomRetry = randomRetry

        # Retry time range value
        self._retryRange = retryRange

    @staticmethod
    def execute(*args, **kwargs):
        """
        Execute a command

        @return command instance
        """

        cmd = ShellCommand(*args, **kwargs)
        cmd.run()
        return cmd

    def run(self):
        """
        Run the command
        """

        # Convert all arguments to string
        self._command = [str(i) for i in self._command]

        logger.debug(
            "executing%s:\n\t%s"
            % (
                ""
                if not self._workingDirectory
                else " in '" + self._workingDirectory + "'",
                " ".join(self._command),
            )
        )

        # Working directory ok ?
        if self._workingDirectory != None and not os.path.isdir(self._workingDirectory):
            raise RuntimeError("Invalid working directory: %r" % self._workingDirectory)

        success = True
        errorMessage = ""

        # Check other params only if there is more than one command execution retry
        if self._numRetries > 1:
            # Sanity check and setting of default value for retryRange param
            if not self._randomRetry and not self._retryRange:
                self._retryRange = self.DEFAULT_FIXED_RETRY_TIME_SEC
            elif not self._retryRange:
                self._retryRange = self.DEFAULT_RETRY_TIME_RANGE_SEC
                # Check for tuple size - it's should contain at least 2 elements
                if len(self._retryRange) < 2:
                    raise RuntimeError(
                        self,
                        "retryRange tuple must contain at least 2 elements (min and max time intervals in seconds)",
                    )

        # Main command execution loop
        for i in range(self._numRetries):
            # Reset output buffers
            self._outputBuffers = {
                self.OUTPUT_STREAM_STDERR: b"",
                self.OUTPUT_STREAM_STDOUT: b"",
            }

            pipe = subprocess.Popen(
                self._command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self._workingDirectory,
            )

            # Streams we're reading from
            outputStreams = {
                pipe.stdout.fileno(): pipe.stdout,
                pipe.stderr.fileno(): pipe.stderr,
            }

            # Indication that EOS was reached
            streamsEosReached = {i: False for i in outputStreams.keys()}

            # Maping of file number to type of stream
            streamTypeMap = {
                pipe.stdout.fileno(): self.OUTPUT_STREAM_STDOUT,
                pipe.stderr.fileno(): self.OUTPUT_STREAM_STDERR,
            }

            # Read output
            while True:
                # Read from stdout/stderr
                reads = outputStreams.keys()

                # Select
                ret = select.select(reads, [], [])

                # Check if execution has finished
                terminated = pipe.poll() != None

                # Break only when execution has terminated, and we read everything from all the streams
                if terminated and all(streamsEosReached.values()):
                    break

                for fd in ret[0]:
                    buffer = outputStreams[fd].read()

                    # Mark the stream as EOS, if nothing was read and pipe has finished executing
                    if not buffer:
                        if terminated:
                            streamsEosReached[fd] = True
                        continue

                    string = buffer.decode(self.OUTPUT_ENCODING).rstrip().lstrip()
                    if string:
                        # Log output string
                        self.__output(string)

                    # Save output
                    self._outputBuffers[streamTypeMap[fd]] += buffer

            pipe.wait()

            self._returnCode = pipe.returncode

            if self._returnCode != self.RETURN_CODE_OK and self._raiseOnError:
                errorMessage = ""

                errorMessage += "Command failed\n"
                errorMessage += "\tcommand: %r\n" % " ".join(self._command)
                errorMessage += "\tcode: %d\n" % self.returnCode

                if self._workingDirectory:
                    errorMessage += "\twork directory: %r\n" % self._workingDirectory

                # Include stdout in error message as well
                if self.stdoutStr:
                    errorMessage += self.stdoutStr + "\n"

                errorMessage += self.stderrStr

                success = False

                if self._numRetries > 1:
                    sleepTime = self._retryRange

                    if self._randomRetry:
                        # Randomize sleep time
                        sleepTime = random.uniform(
                            self._retryRange[1], self._retryRange[0]
                        )

                    logger.error(errorMessage)
                    logger.error(
                        "command execution failed retrying in {:.2f} sec ..".format(
                            sleepTime
                        )
                    )
                    time.sleep(sleepTime)

            else:
                success = True

                break

        if not success:
            raise CommandFailedException(self, errorMessage)

    @property
    def returnCode(self):
        """
        Command return code
        """
        return self._returnCode

    @property
    def stderr(self):
        """
        Command stderr byte buffer
        """
        return self._outputBuffers[self.OUTPUT_STREAM_STDERR]

    @property
    def stdout(self):
        """
        Command stdout byte buffer
        """
        return self._outputBuffers[self.OUTPUT_STREAM_STDOUT]

    @property
    def stdoutStr(self):
        """
        Command stdout string
        """
        return self.stdout.decode(self.OUTPUT_ENCODING)

    @property
    def stderrStr(self):
        """
        Command stderr string
        """
        return self.stderr.decode(self.OUTPUT_ENCODING)
