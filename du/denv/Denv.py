import argparse
import logging
import sys
import os
import traceback
import time
import subprocess
import getpass
import datetime
import re

from du.denv.SshConfigManager import SshConfigManager
from du.denv.Command import Command
from enum import Enum
from subprocess import CalledProcessError

logger = logging.getLogger(__name__.split(".")[-1])


class ErrCodes(Enum):
    # Error Codes
    ERROR_NO_ERROR = "0"
    ERROR_NOT_IN_DOCKER = "1"
    ERROR_OVERLAYFS_IMAGE_NOT_FOUND = "2"
    ERROR_MOUNT_NOT_POSSIBLE = "3"
    ERROR_UNABLE_TO_CREATE_WORKSPACE_FOLDER = "4"
    ERROR_FOLDER_DOES_NOT_EXIST = "5"
    EROROR_GENERAL_ERROR = "6"


class Denv:
    # Docker repo template
    DOCKER_REPO_TEMPLATE = "mcs65:5000/{}:latest"

    # Default docker image template
    DEFAULT_DOCKER_IMAGE_NAME = "master/aosp-generic-dev"

    # Default remote Overlay Images path
    DEFAULT_REMOTE_OVERLAYFS_IMG_PATH = (
        "/home/workareas/iwj-master/aosp_base_device_workspace_images"
    )

    # Temp overlay FS mount point root
    OVERLAYFS_TEMP_MOUNT_ROOT = "/tmp/overlay/"

    # Persisntent path root
    OVERLAYFS_PERSIST_ROOT = "/persist"

    # Persisntent overlay FS mount point root
    OVERLAYFS_PERSIST_MOUNT_ROOT = OVERLAYFS_PERSIST_ROOT + "/overlay/"

    # Final workspace OverlayFS mount point
    OVERLAYFS_WORKSPACE_MOUNT = "/workspace"

    # OverlayFS image file extension
    OVERLAYFS_IMAGE_FILE_EXT = ".img"

    # ls command "serious problem" exit code
    # https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html
    LS_SERIOUS_TROUBLE_EXIT_STATUS = 2

    def __init__(
        self,
        username,
        host=None,
        port=None,
        overlayImagesPath=DEFAULT_REMOTE_OVERLAYFS_IMG_PATH,
    ):
        """
        Constructor

        @param username Default username
        @param host Default host name
        @overlayImagesPath Default OverlayFS images path
        """

        self.__username = username
        self.__host = host
        self.__port = port
        self.__overlayImagesPath = overlayImagesPath
        self.__overlayImages = None
        self.__command = Command(username)
        self.__sshCfgManager = SshConfigManager(self.__command)

    def setUsername(self, username):
        """
        Change username

        @param username New username
        """

        self.__username = username
        self.__command.setUsername(username)

    def setHost(self, host, port):
        """
        Change host

        @param host New host
        @param port New port
        """
        self.__host = host
        self.__port = port
        self.__command.setHost(host, port)

        # Optionally create local user identity file and copy it to authorized_keys on remote side
        # If remote side is local skip this step
        if self.getHost() is not None:
            self.__sshCfgManager.copyLocalSshPubKeyToRemote()

    def setOverlayImagesPath(self, overlayImagesPath, noCheck=False):
        """
        Change OverlayFS images path

        @param overlayImagesPath New OverlayFS image path
        @param noCheck Do not check if the folder exists, set the path explicitly
        @return errorCode - Error code, ERROR_NO_ERROR if folder exists and it is set
        """
        # Obtain error code and list of overlay images in one go
        # Surround with try to catch exceptions if image files are not found in the folder
        try:
            retValue = self.__command.runCommand(
                "if [ -d '{}' ]; then {}; ls {}/*{} 2>/dev/null; else {}; fi".format(
                    overlayImagesPath,
                    "echo {}".format(ErrCodes.ERROR_NO_ERROR.value),
                    "{}".format(overlayImagesPath),
                    self.OVERLAYFS_IMAGE_FILE_EXT,
                    "echo {}".format(ErrCodes.ERROR_FOLDER_DOES_NOT_EXIST.value),
                )
            ).splitlines()
        except CalledProcessError as ex:
            if ex.returncode == self.LS_SERIOUS_TROUBLE_EXIT_STATUS:
                # Do not throw error since the folder actually exists
                # but there are no image files there
                retValue = ErrCodes.ERROR_NO_ERROR.value
            else:
                # Unexpected error happened, return general error
                retValue = ErrCodes.EROROR_GENERAL_ERROR.value

        # Get error code from first returned line
        errCode = ErrCodes(retValue[0])

        # If everything is OK
        if errCode is ErrCodes.ERROR_NO_ERROR or noCheck:
            # Set the new overlay fs image path
            self.__overlayImagesPath = overlayImagesPath
            # Populate image list form the second line if exists
            # Also, while we are at it, trim the list items to get only the base image file names
            # using the magic of complex "Python List Comprehension"
            self.__overlayImages = (
                ([os.path.basename(imagePath) for imagePath in retValue[1:]])
                if retValue and len(retValue[1:])
                else None
            )

        logger.debug("List of overlay images: {}".format(self.__overlayImages))
        logger.debug("setOverlayImagesPath return error code: {}".format(errCode))

        return errCode if not noCheck else ErrCodes.ERROR_NO_ERROR

    def listOverlayImages(self):
        """
        List available OverlayFS images
        """
        return self.__overlayImages

    def getUsername(self):
        """
        Get current username

        @param return Current username
        """

        return self.__username

    def getHost(self):
        """
        Get current host

        @return Current host
        """
        return self.__host

    def getOverlayImagesPath(self):
        """
        Get current OverlayFS images path

        @return Current OverlayFS images path
        """
        return self.__overlayImagesPath

    def listContainers(self):
        """
        List available containers

        @return list of containers
        """
        # Sanitize and update global ssh config file for both Linux and Windows
        self.__sshCfgManager.sanitizeUserSshConfig(self.__generateContainerUserFilter())

        containers = self.__command.runCommand(
            """
            containers=$(docker ps --format "{{.Names}}" --filter "name=%(name)s")
            for container in $containers; do
                image=$(docker exec $container /bin/sh -c \
                "mount | grep "ro_lower"%(osString)s)
                echo $container,$image
            done
            """
            % {
                "name": self.__generateContainerUserFilter(),
                "osString": "%(imgFilterStr)s"
                % {
                    "imgFilterStr": '" | awk "{print \$1}"'
                    if self.__command.getHostPlatform()
                    is self.__command.PLATFORM_OS_LINUX
                    or self.__command.PLATFORM_OS_MACOS
                    else "| awk '{print $1}'\"",
                },
            }
        ).splitlines()

        # Make tuple list for containers, each tuple contains container name and mounted overlay image if any
        containerTupleList = [
            tuple(map(str, container.split(","))) for container in containers
        ]

        return containerTupleList

    def stopContainer(self, name):
        """
        Stop container by name

        @param name Container name
        """

        self.__command.runCommand("docker stop {}".format(name))

    def stopAllContainers(self):
        """
        Stop all containers owned by current user
        """

        return self.__command.runCommand(
            'docker stop $(docker ps --format="{{{{.ID}}}}" --filter "name={}")'.format(
                self.__generateContainerUserFilter()
            )
        )

    def __generateContainerName(self, path="tempfs"):
        """
        Generate a unique container name

        @param path Optional workspace name
        @return container name
        """

        # Generate docker name filter based on user name
        name = self.__generateContainerUserFilter()

        # Append workspace name
        name += "-" + os.path.basename(path)

        # Append timestamp
        name += "-" + datetime.datetime.now().strftime("%j%H%M%S")

        return name

    def startContainer(
        self, localUser=False, containerName=None, imageName=None, workspacePath=None
    ):
        """
        Spawn a new container

        @param localUser Set to True to start container with local user context, otherwsie
        it will be started with root user context (default behaviour)
        @param containerName Name of the container, default name if not set
        @param imageName Name of the docker image that will be used, deufult if not set
        @param workspacePath Path to the persistent workspace inside container, tempfs if not set
        @return name, id, address
        """

        # Assign default container name value if none passed
        containerName = (
            self.__generateContainerName()
            if not containerName
            else self.__generateContainerName(containerName)
        )

        # Assign default container name value if none passed
        imageName = (
            self.DOCKER_REPO_TEMPLATE.format(self.DEFAULT_DOCKER_IMAGE_NAME)
            if not imageName
            else self.DOCKER_REPO_TEMPLATE.format(imageName)
        )

        # Assign default workspace path if none passed
        workspacePath = None if not workspacePath else workspacePath

        logger.debug(
            "Spawning {} with docker image {} and workspace path {}".format(
                containerName, imageName, workspacePath
            )
        )

        cmd = """
{}
docker pull {} >> /dev/null
retVal=$?
if [ $retVal -ne 0 ]; then {}; exit; fi
docker run \
    -d \
    --rm \
    --name {} \
    --privileged \
    {} \
    -it \
    -v /etc/passwd:/etc/passwd \
    -v /etc/group:/etc/group \
    -v /home/:/home/ \
    -v {}:/images \
    {} \
    -v /mnt:{} \
    {}
{}
""".format(
            "mkdir -p {}".format(workspacePath) if workspacePath else "",
            imageName,
            "echo {}".format(ErrCodes.ERROR_UNABLE_TO_CREATE_WORKSPACE_FOLDER.value),
            containerName,
            "" if not localUser else "--user $(id -u):$(id -g)",
            self.__overlayImagesPath,
            "-v {}:{}".format(workspacePath, self.OVERLAYFS_PERSIST_ROOT)
            if workspacePath
            else "",
            self.OVERLAYFS_WORKSPACE_MOUNT,
            imageName,
            self.__command.sshCommandStringConvert(
                """
                docker exec {} /bin/sh -c "
                if [ -d '{}' ]; then
                    {} mount --bind {} {}
                fi"
                """
            ).format(
                containerName,
                self.OVERLAYFS_PERSIST_ROOT,
                "" if not localUser else "sudo",
                self.OVERLAYFS_PERSIST_ROOT,
                self.OVERLAYFS_WORKSPACE_MOUNT,
            ),
        )

        # Spawn container
        containerId = self.__command.runCommand(cmd)

        # Get container IP address
        containerAddress = self.__command.runCommand(
            self.__command.sshCommandStringConvert(
                'docker inspect -f "{{{{ .NetworkSettings.IPAddress }}}}" {}'.format(
                    containerName
                )
            )
        )

        # Crate docker container ssh config file for spawned docker container
        self.__sshCfgManager.createDockerContainerSshConfig(
            containerAddress, containerName
        )

        # Sanitize and update global ssh config file for both Linux and Windows
        self.__sshCfgManager.sanitizeUserSshConfig(self.__generateContainerUserFilter())

        return (containerName, containerId, containerAddress)

    def mountOverlayFS(self, overlayImageFile, containerName):
        """
        Mount OverlayFS image inside the docker container

        @param overlayImageFile Image file that can be mounted as lower read-only OverlayFS partition
        @param containerName Name of the docker container in which the image file will be mounted
        @return errorCode - Zero errorCode means that the mounting has been successful
        """

        dockerMountCmd = """
        docker exec %(containerName)s /bin/sh -c "
            if [ -f '/images/%(overlayImageFile)s' ]; then
                if [ -d '%(persistRoot)s' ]; then
                    mkdir -p %(persistOverlayRoot)s
                    cd %(persistRoot)s
                else
                    mkdir -p %(tmpOverlayRoot)s
                    cd /tmp/
                    sudo mount -t tmpfs tmpfs %(tmpOverlayRoot)s
                fi
                # Unmount workspace before everything
                sudo umount /workspace
                # Prepare Overlay FS required mount points
                mkdir -p overlay/{ro_lower,lower,upper,work}
                # Mount the overlay image file as read only to the /lower_ro partition
                sudo mount -o ro,loop /images/%(overlayImageFile)s overlay/ro_lower
                # Use bindfs to allow current running user to have permissions over the files from the image
                sudo bindfs -u $(id -u) -g $(id -g) overlay/ro_lower overlay/lower
                # Finally  mount the resulting OverlayFS to final workspace mount point
                sudo mount -t overlay overlay -o lowerdir=overlay/lower,upperdir=overlay/upper,workdir=overlay/work %(workspace)s
                %(noErrorErrCode)s
            else
                %(noImageFoundErrCode)s
            fi"
        """ % {
            "containerName": containerName,
            "overlayImageFile": overlayImageFile,
            "persistRoot": self.OVERLAYFS_PERSIST_ROOT,
            "persistOverlayRoot": self.OVERLAYFS_PERSIST_MOUNT_ROOT,
            "tmpOverlayRoot": self.OVERLAYFS_TEMP_MOUNT_ROOT,
            "workspace": self.OVERLAYFS_WORKSPACE_MOUNT,
            "noErrorErrCode": "echo {}".format(ErrCodes.ERROR_NO_ERROR.value),
            "noImageFoundErrCode": "echo {}".format(
                ErrCodes.ERROR_OVERLAYFS_IMAGE_NOT_FOUND.value
            ),
        }

        dockerCheckMountCmd = """
        docker exec %(containerName)s /bin/sh -c "
            sudo mount | grep "ro_lower"" >> /dev/null
        """ % {
            "containerName": containerName,
            "workspace": self.OVERLAYFS_WORKSPACE_MOUNT.strip("/"),
        }

        cmd = """
        docker exec %(containerName)s cat /proc/1/cgroup | grep docker >> /dev/null
        retVal=$?

        if [ $retVal -ne 0 ]; then
           %(notInsideContainerErrCode)s
        else
            %(dockerCheckMountCmd)s
            retVal=$?
            if [ $retVal -ne 1 ]; then
                %(mountNotPossibleErrCode)s
            else
                %(dockerMountCmd)s
            fi
        fi
        """ % {
            "containerName": containerName,
            "dockerCheckMountCmd": self.__command.sshCommandStringConvert(
                dockerCheckMountCmd
            ),
            "dockerMountCmd": self.__command.sshCommandStringConvert(dockerMountCmd),
            "notInsideContainerErrCode": "echo {}".format(
                ErrCodes.ERROR_NOT_IN_DOCKER.value
            ),
            "mountNotPossibleErrCode": "echo {}".format(
                ErrCodes.ERROR_MOUNT_NOT_POSSIBLE.value
            ),
        }

        return ErrCodes(self.__command.runCommand(cmd))

    def unmountOverlayFS(self, containerName):
        """
        Un-mount OverlayFS image inside the docker container

        @param containerName Name of the docker container in which the image file will be un-mounted
        @return errorCode - Zero errorCode means that the un-mounting has been successful
        """

        dockerUnmountCmd = """
        docker exec %(containerName)s /bin/sh -c "
            sudo umount %(workspace)s
            if [ -d '%(persistRoot)s' ]; then
                sudo umount %(persistOverlayRoot)slower
                sudo umount %(persistOverlayRoot)sro_lower
                # Mount back persist to workspace
                sudo mount --bind %(persistRoot)s %(workspace)s
            else
                sudo umount %(tmpOverlayRoot)slower
                sudo umount %(tmpOverlayRoot)sro_lower
                sudo umount %(tmpOverlayRoot)s
            fi
            %(noErrorErrCode)s"
        """ % {
            "workspace": self.OVERLAYFS_WORKSPACE_MOUNT,
            "containerName": containerName,
            "tmpOverlayRoot": self.OVERLAYFS_TEMP_MOUNT_ROOT,
            "persistRoot": self.OVERLAYFS_PERSIST_ROOT,
            "persistOverlayRoot": self.OVERLAYFS_PERSIST_MOUNT_ROOT,
            "noErrorErrCode": "echo {}".format(ErrCodes.ERROR_NO_ERROR.value),
        }

        dockerCheckMountCmd = """
        docker exec %(containerName)s /bin/sh -c "
            sudo mount | grep "ro_lower"" >> /dev/null
        """ % {
            "containerName": containerName,
            "workspace": self.OVERLAYFS_WORKSPACE_MOUNT.strip("/"),
        }

        cmd = """
        docker exec %(containerName)s cat /proc/1/cgroup | grep docker >> /dev/null
        retVal=$?

        if [ $retVal -ne 0 ]; then
            %(notInsideContainerErrCode)s
        else
            %(dockerCheckMountCmd)s
            retVal=$?
            if [ $retVal -ne 0 ]; then
                %(mountNotPossibleErrCode)s
            else
                %(dockerUnmountCmd)s
            fi
        fi
        """ % {
            "containerName": containerName,
            "dockerCheckMountCmd": self.__command.sshCommandStringConvert(
                dockerCheckMountCmd
            ),
            "dockerUnmountCmd": self.__command.sshCommandStringConvert(
                dockerUnmountCmd
            ),
            "notInsideContainerErrCode": "echo {}".format(
                ErrCodes.ERROR_NOT_IN_DOCKER.value
            ),
            "mountNotPossibleErrCode": "echo {}".format(
                ErrCodes.ERROR_MOUNT_NOT_POSSIBLE.value
            ),
        }

        return ErrCodes(self.__command.runCommand(cmd))

    def spawnSshShellSession(self, containerName=None, command=None):
        """
        Start an interactive shell on the container or jump-host

        @param containerName If set to None the ssh session will be created on host
        @param command Optional command to execute on remote shell
        @retrun Retrun code of the spawned shell process
        """
        return self.__command.spawnSshShell(containerName, command)

    def __generateContainerUserFilter(self):
        """
        Generate container filter string based on username and container template string

        @return filter string
        """
        return self.__sshCfgManager.CONTAINER_NAME_TEMPLATE.format(self.__username)
