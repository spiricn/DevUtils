import logging
import re
import os
import sys
from subprocess import CalledProcessError

from du.denv.Command import Command

logger = logging.getLogger(__name__.split(".")[-1])


class SshConfigManager:

    """
    Manages ssh configuration files on host and client side for given user
    """

    # Path to the scp executable for both Linux and Win32 host platfrom
    SCP_BINARY = (
        "scp"
        if sys.platform == Command.PLATFORM_OS_LINUX
        else os.path.join(Command.WIN32_SYSTEM_PATH, "OpenSSH\\scp.exe")
    )

    # Path to the ssh-keygen executable for both Linux and Win32 host platfrom
    SSH_KEYGEN_BINARY = (
        "ssh-keygen -N '' -f {}"
        if sys.platform == Command.PLATFORM_OS_LINUX
        else os.path.join(
            Command.WIN32_SYSTEM_PATH, 'OpenSSH\\ssh-keygen.exe -P "" -f {}'
        )
    )

    # Path to ssh program data folder on Windows platform
    WIN32_SSH_PROGRAM_DATA_PATH = (
        os.path.join(
            os.environ["AllUsersProfile"],
            "ssh",
        )
        if sys.platform == Command.PLATFORM_OS_WIN32
        else ""
    )

    # System ssh config file on Win32 OS
    WIN32_SYSTEM_SSH_CONFIG_FILE = os.path.join(
        WIN32_SSH_PROGRAM_DATA_PATH + os.sep, "ssh_config"
    )

    # Local user SSH root folder
    LOCAL_USER_SSH_ROOT_FOLDER = os.path.join(os.path.expanduser("~") + os.sep, ".ssh")

    # Local user SSH config file location on Linux OS
    LOCAL_LINUX_USER_SSH_CONFIG_FILE = os.path.join(
        LOCAL_USER_SSH_ROOT_FOLDER + os.sep, "config"
    )

    # Local user SSH config file location on Win32 OS
    LOCAL_WIN32_USER_SSH_CONFIG_FILE = os.path.join(
        LOCAL_USER_SSH_ROOT_FOLDER + os.sep, "config_overlay"
    )

    # Local user public and private key files
    LOCAL_USER_SSH_IDENTITY_FILE_PUBLIC = os.path.join(
        LOCAL_USER_SSH_ROOT_FOLDER + os.sep, "id_rsa.pub"
    )
    LOCAL_USER_SSH_IDENTITY_FILE_PRIVATE = os.path.join(
        LOCAL_USER_SSH_ROOT_FOLDER + os.sep, "id_rsa"
    )

    # Remote side authorized_keys file location (Linux OS only for now)
    REMOTE_LINUX_AUTH_KEYS_FILE = "/home/{}/.ssh/authorized_keys"

    # Remote user SSH config file location (Linux OS only for now)
    REMOTE_LINUX_USER_SSH_CONFIG_FILE = "/home/{}/.ssh/config"

    # Docker container SSH config file location
    DOCKER_CONTAINER_SSH_CONFIG_FILE = "/home/{}/.ssh/{}"

    # OpenSSH default binary location on Windows 10
    OPENSSH_WIN10_FILE_LOCATION = re.escape(
        r"C:\\Windows\\System32\\{}".format(
            re.escape(Command.WIN32_SSH_RELATIVE_EXE_PATH)
        )
    )

    # Command string that is passed to remote shell in order to get the list of active_containers
    SSH_DOCKER_CONTAINER_LIST_CMDLINE = 'active_containers=$(docker ps --format "{{ .Names }}" --filter "name=%(filter)s")'

    # Line which is prepended to the user's ssh config file on Windows platform
    SSH_CONFIG_OVERLAY_INCLUDE_STRING = "Include config_overlay"

    # Default container template name
    CONTAINER_NAME_TEMPLATE = "{}-denv"

    # Windows host system ssh_config file template
    WIN32_SSH_CONFIG_FILE_TEMPLATE = """Host *{}*
    StrictHostKeyChecking no
    UserKnownHostsFile NUL


""".format(
        CONTAINER_NAME_TEMPLATE.format("")
    )

    def __init__(self, command):
        """
        Constructor

        @param command Command instance to be used
        """

        self.__command = command

        # Check if the system ssh_config is patched on Windows host platform
        self.__sshWinConfigPatcher()

    def sanitizeUserSshConfig(self, filter):
        """
        Syncrhronize user's ssh config file with active docker containers hosts
        and generate global ssh configs for both Linux and Windows platforms

        @param filter Filter string used to filter current user's docker containers
        @return stdout of bash executed script
        """
        # Set ssh config files for given user
        configFileLinux = self.REMOTE_LINUX_USER_SSH_CONFIG_FILE.format(
            self.__command.getUsername()
        )
        configFileWin = configFileLinux + "{}".format("_windows")

        logger.debug(
            "Sanitizing container ssh configs:\n\thost:\t{}\n\tuser:\t{}".format(
                self.__command.getHost(), self.__command.getUsername()
            )
        )

        cmdRet = None

        # Prepare bash shell command which will update user ssh config
        # files based on currently active docker containers
        cmd = """
rm -rf %(configLinux)s
rm -rf %(configWin)s
%(dockerListContCommand)s
delete=1
for file in /home/%(username)s/.ssh/%(filter)s*
do
    for container in $active_containers; do
    if [ \"${file##*/\"$container\"}\" ]; then
        delete=1
    else
        delete=0
        break
    fi
    done
    if [ "$delete" = "1" ]; then
        rm -rf $file
    else
        cat $file >> /home/%(username)s/.ssh/config
    fi
done
    if [ -f "%(configLinux)s" ]; then
    sed -e 's/localhost/jump-box/g' -e 's#/dev/null#NUL#g' \
-e %(winSshBinPath)s %(configLinux)s > %(configWin)s
    fi
""" % {
            "configLinux": configFileLinux,
            "configWin": configFileWin,
            "dockerListContCommand": self.__command.sshCommandStringConvert(
                self.SSH_DOCKER_CONTAINER_LIST_CMDLINE % {"filter": filter}
            ),
            "filter": filter,
            "username": self.__command.getUsername(),
            "winSshBinPath": "s/ssh/" + self.OPENSSH_WIN10_FILE_LOCATION + "/g",
        }

        # If host is local and Win32, skip this step
        if not (
            self.__command.getHostPlatform() is Command.PLATFORM_OS_WIN32
            and self.__command.getHost() is None
        ):
            cmdRet = self.__command.runCommand(cmd)
            if not cmdRet:
                # Copy final ssh config file back to host
                self.__copyDockerSshConfigToHost()
        return cmdRet

    def createDockerContainerSshConfig(self, containerAddress, containerName):
        """
        Creates a ssh config for given docker container name and IP address
        This config is created with host acting as a jump-box for the spawned docker container's ssh connection
        Generated config also disables Host Key Cheking for those ssh connections

        @param containerAddress IP address of the docker container
        @param containerName Name of the docker container
        @return stdout of bash executed script
        """
        # Set ssh docker container config file
        dockerSshConfig = self.DOCKER_CONTAINER_SSH_CONFIG_FILE.format(
            self.__command.getUsername(), containerName
        )

        logger.debug(
            "Creating ssh config for:\n\tuser:\t{}\n\tcontainer:\t{}".format(
                self.__command.getUsername(), containerName
            )
        )

        # Prepare bash shell command which will create ssh config for given user and docker container
        cmd = """
if [ ! -d "/home/%(username)s/.ssh" ]; then
    mkdir "/home/%(username)s/.ssh"
fi
echo "Host localhost" | tee -a %(dockerConfig)s > /dev/null
echo "    HostName %(host)s" | tee -a %(dockerConfig)s > /dev/null
echo "    User %(username)s" | tee -a %(dockerConfig)s > /dev/null
echo "    Port 22" | tee -a %(dockerConfig)s > /dev/null
echo | tee -a %(dockerConfig)s > /dev/null
echo "Host %(dockerName)s" | tee -a %(dockerConfig)s > /dev/null
echo "    HostName %(dockerIp)s" | tee -a %(dockerConfig)s > /dev/null
echo "    User %(username)s" | tee -a %(dockerConfig)s > /dev/null
echo "    StrictHostKeyChecking no" | tee -a %(dockerConfig)s > /dev/null
echo "    UserKnownHostsFile /dev/null" | tee -a %(dockerConfig)s > /dev/null
echo "    ProxyCommand ssh -q -W %%h:%%p localhost" | tee -a %(dockerConfig)s > /dev/null
echo | tee -a %(dockerConfig)s > /dev/null
        """ % {
            "username": self.__command.getUsername(),
            "dockerConfig": dockerSshConfig,
            "dockerIp": containerAddress,
            "dockerName": containerName,
            "host": self.__command.getHost()
            if self.__command.getHost()
            else "localhost",
        }

        return self.__command.runCommand(cmd)

    def copyLocalSshPubKeyToRemote(self):
        """
        Copies local user's identity file (eg. ~/.ssh/id_rsa.pub) to the
        remote host authorized_keys file
        If local identity file is not presnet new one will be generated

        @return stdout of the executed remote command
        """

        # 1. Check if local user has a generated local identity
        #    Usually it is id_rsa.pub file located in ~/.ssh folder
        #    If not present try to generate one
        if not os.path.exists(self.LOCAL_USER_SSH_IDENTITY_FILE_PUBLIC):
            logger.info(
                "There is no local user's identity on this machine, we will create one"
            )

            # If we are on Windows host check if .ssh folder exists in local user's
            # home directory and create it since the ssh keygeneration will fail otherwise
            if (
                self.__command.getHostPlatform() is Command.PLATFORM_OS_WIN32
                and not os.path.exists(self.LOCAL_USER_SSH_ROOT_FOLDER)
            ):
                logger.info(
                    "There is no .ssh folder in user's home direcotry on Windows host, we will creat one."
                )
                os.makedirs(self.LOCAL_USER_SSH_ROOT_FOLDER)

            crateLocalUserPublicKeyCommand = self.SSH_KEYGEN_BINARY.format(
                self.LOCAL_USER_SSH_IDENTITY_FILE_PRIVATE
            )
            self.__command.runCommand(crateLocalUserPublicKeyCommand, True)

        # Also on Windows platform we need to create config file if it does not exist
        # This file which will include config_overlay file which consists of container
        # ssh jump-host configs
        if self.__command.getHostPlatform() is Command.PLATFORM_OS_WIN32:
            if not os.path.exists(self.LOCAL_LINUX_USER_SSH_CONFIG_FILE):
                logger.info(
                    "There is no ssh config file, we will create one and patch it"
                )
                self.__fileLinePrepender(
                    self.LOCAL_LINUX_USER_SSH_CONFIG_FILE,
                    self.SSH_CONFIG_OVERLAY_INCLUDE_STRING,
                    True,
                )
            # If it exists we need to check if the config_overlay is already included
            # If not, add that line at the begining of the file
            else:
                if not self.__fileLineSearch(
                    self.LOCAL_LINUX_USER_SSH_CONFIG_FILE,
                    self.SSH_CONFIG_OVERLAY_INCLUDE_STRING,
                ):
                    logger.info("ssh config file found but it will be patched")
                    self.__fileLinePrepender(
                        self.LOCAL_LINUX_USER_SSH_CONFIG_FILE,
                        self.SSH_CONFIG_OVERLAY_INCLUDE_STRING,
                    )

        # Get the public key from the id_rsa.pub file
        with open(self.LOCAL_USER_SSH_IDENTITY_FILE_PUBLIC, "r") as file:
            publicKey = file.read().replace("\n", "")

        logger.debug("User's public key: " + publicKey)

        # 2. Check if authorized_keys file exists on remote side
        #    and create it if missing, check if user's public key
        #    is already there and append it if necessery
        logger.debug("Transfering local user's public key to remote side if needed")

        # Prepare bash shell command which will do the job
        cmd = """
if [ ! -d "/home/%(username)s/.ssh" ]; then
    mkdir "/home/%(username)s/.ssh"
fi
if [ -f "%(remoteAuthKeysFile)s" ]; then
    echo "File authorized_keys exists, checking if user public key is already there"
    if grep -Fxq "%(localUserPublicKey)s" "%(remoteAuthKeysFile)s"; then
        echo "User public key found, do nothing"
    else
        echo "User public key not found, append it"
        echo "%(localUserPublicKey)s" | tee -a "%(remoteAuthKeysFile)s" > /dev/null
    fi
else
    echo "File authorized_keys does not exist, create one and append user public key"
    echo "%(localUserPublicKey)s" | tee -a "%(remoteAuthKeysFile)s" > /dev/null
fi

chmod 600  "%(remoteAuthKeysFile)s"
        """ % {
            "username": self.__command.getUsername(),
            "remoteAuthKeysFile": self.REMOTE_LINUX_AUTH_KEYS_FILE.format(
                self.__command.getUsername()
            ),
            "localUserPublicKey": publicKey
            if self.__command.getHostPlatform() is Command.PLATFORM_OS_LINUX
            or Command.PLATFORM_OS_MACOS
            else re.escape(publicKey),
        }

        return self.__command.runCommand(cmd)

    def __copyDockerSshConfigToHost(self):
        """
        Copies remote ssh config files to the local host
        After this step the local host has the ssh config with jump-host
        configuration to the remote docker containers

        @return stdout of the executed commands
        """
        # Set ssh config files for given user
        remoteConfigFileLinux = self.REMOTE_LINUX_USER_SSH_CONFIG_FILE.format(
            self.__command.getUsername()
        )
        localConfigFileLinux = self.LOCAL_LINUX_USER_SSH_CONFIG_FILE
        remoteConfigFileWin = remoteConfigFileLinux + "{}".format("_windows")

        # Determine local host and prepare copy commands accordingly
        if (
            self.__command.getHostPlatform() == Command.PLATFORM_OS_LINUX
            or self.__command.getHostPlatform() == Command.PLATFORM_OS_MACOS
        ):
            logger.debug("Prepare SSH config sync from remote to Linux host")
            scpSshConfigCopyCommand = self.SCP_BINARY + " %(username)s@%(remoteHost)s:%(remoteConfigLinux)s %(localConfigLinux)s > \/dev\/null 2>&1" % {
                "username": self.__command.getUsername(),
                "userLocalWindowsSshConfig": self.LOCAL_WIN32_USER_SSH_CONFIG_FILE,
                "remoteHost": self.__command.getHost(),
                "remoteConfigLinux": remoteConfigFileLinux,
                "localConfigLinux": localConfigFileLinux,
            }
            localSshConfigPath = localConfigFileLinux
        elif self.__command.getHostPlatform() == Command.PLATFORM_OS_WIN32:
            logger.debug("Prepare SSH config sync from remote to Win32 host")
            scpSshConfigCopyCommand = self.SCP_BINARY + " %(remotePort)s %(username)s@%(remoteHost)s:%(configWin)s %(userLocalWindowsSshConfig)s" % {
                "username": self.__command.getUsername(),
                "userLocalWindowsSshConfig": self.LOCAL_WIN32_USER_SSH_CONFIG_FILE,
                "remoteHost": self.__command.getHost(),
                "remotePort": "-p {}".format(self.__command.getPort())
                if self.__command.getPort()
                else "",
                "configWin": remoteConfigFileWin,
            }
            localSshConfigPath = self.LOCAL_WIN32_USER_SSH_CONFIG_FILE

        # Copy the remote ssh config files to local host
        scpSshCopyCmdParams = {"command": scpSshConfigCopyCommand, "local": True}
        localSshConfigPathParams = {"path": localSshConfigPath}

        command_list = [
            (self.__command.runCommand, scpSshCopyCmdParams, CalledProcessError),
            (os.remove, localSshConfigPathParams, FileNotFoundError),
        ]

        result = None

        for action, params, ex in command_list:
            try:
                result = action(**params)
                break
            except CalledProcessError as ex:
                logger.debug(
                    "Remote SSH config file missing or some other error - do local cleanup. Return code is {}".format(
                        ex.returncode
                    )
                )
                continue
            except FileNotFoundError as ex:
                logger.debug(
                    "Local SSH config file missing or some other error. Strerror: {}, error number: {}".format(
                        ex.strerror, ex.errno
                    )
                )

            return result

    def __sshWinConfigPatcher(self):
        """
        Patches the ssh_config file on Win32 platform to disable StrictHostChecking option
        for containers started by this tool
        Call to this function needs to be done from within administrative context
        This patching is not needed on Linux platform
        """

        # Check if system ssh_config file exists
        if self.__command.getHostPlatform() is Command.PLATFORM_OS_WIN32:
            if not os.path.exists(self.WIN32_SYSTEM_SSH_CONFIG_FILE):
                logger.info("There is no system ssh_config on this Windows host")
                # Chek for admin rights
                if not self.__command.checkAdmin()[1]:
                    # Inform user that in order to patch the system ssh_config file
                    # the tool needs to be restarted from shell with admin privileges
                    logger.info(
                        "Please restart this tool from shell with admin privileges, so we can create and patch it"
                    )
                    sys.exit()
                else:
                    # Create the file and apply the patch to the begining of the file
                    self.__fileLinePrepender(
                        self.WIN32_SYSTEM_SSH_CONFIG_FILE,
                        self.WIN32_SSH_CONFIG_FILE_TEMPLATE,
                        True,
                    )
                    logger.info(
                        "We have admin rights... file is crated and patched successfully"
                    )
            else:
                if not self.__fileLineSearch(
                    self.WIN32_SYSTEM_SSH_CONFIG_FILE,
                    # Do search on the first line only, it is good enough
                    self.WIN32_SSH_CONFIG_FILE_TEMPLATE.partition("\n")[0],
                ):
                    logger.info(
                        "System ssh_config file found but it needs to be patched"
                    )
                    # Chek for admin rights
                    if not self.__command.checkAdmin()[1]:
                        # Inform user that in order to patch the system ssh_config file
                        # the tool needs to be restarted from shell with admin privileges
                        logger.info(
                            "Please restart this tool from shell with admin privileges, so we can patch it"
                        )
                        sys.exit()
                    else:
                        # Append the patch to the begining of the file
                        self.__fileLinePrepender(
                            self.WIN32_SYSTEM_SSH_CONFIG_FILE,
                            self.WIN32_SSH_CONFIG_FILE_TEMPLATE,
                        )
                        logger.info(
                            "We have admin rights... patching is finished successfully"
                        )
        return

    def __fileLinePrepender(self, filename, line, newFile=False):
        """
        Adds string line to the begining of the file

        @param filename File which will be modified (line prepended)
        @param line String line
        @param newFile If True it will create/overwrite the file. If False it will patch existing file
        """
        with open(filename, "w+" if newFile else "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(line.rstrip("\r\n") + "\n\n" + content)

    def __fileLineSearch(self, filename, searchLine):
        """
        Searches a string line in the file

        @param filename File which will be used for serach
        @param searchLine String line that is beeing searched
        @return True if line is found, False otherwise
        """
        with open(filename, "r") as f:
            for line in f:
                line = line.rstrip()  # remove '\n' at end of line
                if searchLine == line:
                    return True
            return False
