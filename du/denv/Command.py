import logging
import subprocess
import os
import platform
import sys

from cmd2 import utils

logger = logging.getLogger(__name__.split(".")[-1])


class Command:
    """
    Provides a way to run bash commands on local or remote side
    Remote execution of commands is done over SSH protocol for given username and host
    """

    # Host platform string for Windows
    PLATFORM_OS_WIN32 = "win32"

    # Host platform string for Linux
    PLATFORM_OS_LINUX = "linux"

    # Host platform string for MAC OS
    PLATFORM_OS_MACOS = "darwin"

    # Path to System folder on Windows platform
    WIN32_SYSTEM_PATH = (
        os.path.join(
            os.environ["SystemRoot"],
            "SysNative" if platform.architecture()[0] == "32bit" else "System32",
        )
        if sys.platform == PLATFORM_OS_WIN32
        else ""
    )

    # Encoding used to decode stdout with
    OUTPUT_ENCODING = "ISO-8859-1"

    # ssh connection param template for linux platform
    LINUX_SSH_CONN_PARAM_TEMPLATE = " {} {}@{} '{}'"

    # ssh connection param template for win32 platform
    WIN32_SSH_CONN_PARAM_TEMPLATE = " {} {}@{} {}"

    # Relative path to the ssh executable on Windows platform
    WIN32_SSH_RELATIVE_EXE_PATH = "OpenSSH\\ssh.exe"

    # Path that is used to check if we have administrative rights
    ADMIN_CHECK_PATH = os.sep.join(
        [os.environ.get("SystemRoot", "C:\\windows"), "temp"]
    )

    # Localhost string
    HOST_LOCALHOST = "localhost"

    def __init__(self, username):
        """
        Constructor

        @param username Default username
        """

        self.__username = username
        self.__host = None
        self.__port = None
        # Host platform
        self.__platform = sys.platform
        # Path to ssh binary on host
        self.__sshPath = None
        # Subprocess check_output shell param
        self.__coShell = None

        # Set subprocess params on init
        self.__setSshHostCommandParams()

    def setUsername(self, username):
        """
        Change username

        @param username New username
        """

        self.__username = username

    def setHost(self, host, port):
        """
        Change host

        @param host New host
        @param port New port
        """
        self.__host = host
        self.__port = port

    def getUsername(self):
        """
        Get current username

        @return Current username
        """

        return self.__username

    def getHost(self):
        """
        Get current host

        @return Current host
        """
        return self.__host if self.__host else self.HOST_LOCALHOST

    def getPort(self):
        """
        Get current port

        @return Current port
        """
        return self.__port

    def runCommand(self, command, local=False):
        """
        Run a command locally or via ssh

        @param command Command to run
        @param local Set to True to run command on local host explicitly (default = False)
        @return stdout
        """

        # If host is set -> run via SSH
        if self.__host and not local:
            if self.__sshPath:
                command = self.__sshPath.format(
                    "-T {}".format("-p " + self.__port if self.__port else ""),
                    self.__username,
                    self.__host,
                    command,
                )
            else:
                # TODO: Proper Error handling, throw exception here (no ssh binary = no remote command execution)
                logger.error("No SSH binary found on host!")
                return None

        logger.debug(command)
        stdout = (
            subprocess.check_output(command, shell=self.__coShell)
            .decode(self.OUTPUT_ENCODING)
            .strip()
        )

        logger.debug(stdout)

        return stdout

    def spawnSshShell(self, host, command):
        """
        Spawns an interactive ssh shell on the host

        @param host Remote host to connect to, if none jump-host will be used
        @param command Command to execute on remote shell
        @return Return code of the spawned ssh shell process
        """

        proc = subprocess.Popen(
            self.__sshPath.format(
                "{}".format("-p " + self.__port if self.__port else ""),
                self.__username,
                self.__host if not host else host,
                "{}".format(command if command else ""),
            ),
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True,
        )

        # Start the process reader threads (for stdout and stderr)
        proc_reader = utils.ProcReader(proc, sys.stdout, sys.stderr)
        # Block here until we exit from the process
        proc_reader.wait()

        return proc.returncode

    def sshCommandStringConvert(self, command):
        """
        Convert command that is sent over ssh acording to the host environment

        @param command Command string that needs to be converted
        @return converted command string
        """
        # For now we need to convert the string which contains " chars to '
        # only when host is Win32 platform
        # Some of the docker commands may fail if they are sent from Win32
        # host over ssh if this conversion is not done
        if self.__platform == self.PLATFORM_OS_WIN32:
            command = command.replace('"', "'")
        return command

    def getHostPlatform(self):
        """
        Return the host platform on which this tool is running

        @return current host platform
        """
        if self.__platform is self.PLATFORM_OS_WIN32:
            return self.PLATFORM_OS_WIN32
        elif self.__platform is self.PLATFORM_OS_MACOS:
            return self.PLATFORM_OS_MACOS
        # Assume for everything else that we are on Linux like OS
        else:
            return self.PLATFORM_OS_LINUX

    def checkAdmin(self):
        """
        Checks if the environment in which this tool is run has administrative privileges

        @return Tuple with two values: username, hasAdmin (True or False)
        """
        if self.__platform == self.PLATFORM_OS_WIN32:
            try:
                # only windows users with admin privileges can read the C:\windows\temp
                temp = os.listdir(self.ADMIN_CHECK_PATH)
            except:
                return (os.environ["USERNAME"], False)
            else:
                return (os.environ["USERNAME"], True)
        elif self.__platform == self.PLATFORM_OS_LINUX:
            if "SUDO_USER" in os.environ and os.geteuid() == 0:
                return (os.environ["SUDO_USER"], True)
            else:
                return (os.environ["USERNAME"], False)
        elif self.__platform == self.PLATFORM_OS_MACOS:
            logger.info("There is no need for SUDO check on MAC_OS for now")

    def __setSshHostCommandParams(self):
        """
        Checks host platform and sets correct ssh binary path and params
        for subprocess command call
        """
        logger.debug("Host platform: " + self.__platform)
        # Check the host platform in order to get the path to ssh binary
        if self.__platform == self.PLATFORM_OS_WIN32:
            self.__sshPath = (
                os.path.join(self.WIN32_SYSTEM_PATH, self.WIN32_SSH_RELATIVE_EXE_PATH)
                + self.WIN32_SSH_CONN_PARAM_TEMPLATE
            )
            self.__coShell = False
        elif self.__platform == self.PLATFORM_OS_LINUX or self.PLATFORM_OS_MACOS:
            self.__sshPath = "ssh" + self.LINUX_SSH_CONN_PARAM_TEMPLATE
            self.__coShell = True

        if self.__sshPath is not None:
            logger.debug("SSH binary path: " + self.__sshPath)
        else:
            logger.error(
                "No SSH binary found on host, only local cmd execution will work!"
            )
        return
