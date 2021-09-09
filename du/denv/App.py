import argparse
import logging
import sys
import os
import traceback
import time
import subprocess
import getpass
import datetime

from inspect import getfullargspec
from argparse import RawTextHelpFormatter
from du.denv.Denv import Denv
from du.denv.Denv import ErrCodes

# Host platform string for Windows
PLATFORM_OS_WIN32 = "win32"

# Host platform string for Linux
PLATFORM_OS_LINUX = "linux"

# Host platform string for MAC OS
PLATFORM_OS_MACOS = "darwin"

try:
    import cmd2
except ModuleNotFoundError:
    if sys.platform == PLATFORM_OS_WIN32:
        # Install automatically via PIP if missing on Windows (we can do this from script)
        print("Installing cmd2 ..")

        # Make sure we have pip installed (this will fail on Linux, since it has to be done via apt)
        subprocess.check_call([sys.executable, "-m", "ensurepip"])

        # Install cmd2 dependency
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cmd2"])

        import cmd2
    elif sys.platform == PLATFORM_OS_LINUX:
        # On linux the user has to do it manually
        print("#" * 80 + "\n")

        print("Dependencies missing, run the following commands to install them: ")

        # Command to install PIP
        print("\n\tsudo apt-get install -y python3-pip")

        # Command to install dependencies via PIP
        print("\n\tsudo python3 -m pip install cmd2")
        print("\n\tsudo python3 -m pip install gnureadline")

        print("\n" + "#" * 80 + "\n")

        sys.exit(-1)
    elif sys.platform == PLATFORM_OS_MACOS:
        # On MAC OS the user has to do it manually
        print("#" * 80 + "\n")

        print("Dependencies missing, run the following commands to install them: ")

        # Command to install dependencies via PIP
        print("\n\tpython3 -m pip install cmd2 --user")
        print("\n\tpython3 -m pip install gnureadline --user")

        print("\n" + "#" * 80 + "\n")

        sys.exit(-1)
    else:
        print("Unhandled platform {}".format(sys.platform))
        sys.exit(-1)

from cmd2 import with_argparser

logger = logging.getLogger(__name__.split(".")[-1])

try:
    import cmd2
except ModuleNotFoundError:
    # Install automatically via PIP if missing
    logger.info("Installing cmd2 ..")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cmd2"])

    import cmd2

from cmd2 import with_argparser


class App(cmd2.Cmd):
    # Default local host name
    DEFAULT_LOCAL_HOST_NAME = "local"

    # Clear screen cmd on Windows
    CLEAR_CMD_WIN32 = "cls"

    # Clear screen cmd on Unix type OS
    CLEAR_CMD_UNIX = "clear"

    def __init__(self):
        super().__init__()
        self.__denv = Denv(getpass.getuser())
        # Set initial cmd prompt
        self.__updatePrompt()

    def do_set_username(self, username):
        """
        Set new username
        """
        # Change to new username and update cmd prompt
        self.__denv.setUsername(username)
        logger.info("Username changed to: {}".format(username))
        self.__updatePrompt()

    setHostArgParser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog="This command needs to be called with valid positional argument(s), there are no default values",
    )
    setHostArgParser.add_argument(
        "host",
        metavar="HOST:PORT",
        type=str,
        help="Host name with optional port number (ex. host:port)",
    )

    @with_argparser(setHostArgParser)
    def do_set_host(self, args):
        """
        Set new host

        If remote host is running ssh daemon on non default port 22
        the port can be set to host in following way:

        do_set_host host:port [eg. mcsxx:8022]

        If the host is local machine then set host argument to "local"
        """
        # Parse port number out of host string if any
        if args.host:
            parsedHost = args.host.rsplit(":", 1)
            hostName = parsedHost[0] if len(parsedHost) > 0 else None
            port = parsedHost[1] if len(parsedHost) > 1 else None
        else:
            hostName = None
            port = None

        # Change to new host and update cmd prompt
        # Setting hostName to "local" will make commands run on local host
        self.__denv.setHost(
            None
            if hostName == self.DEFAULT_LOCAL_HOST_NAME or hostName == ""
            else hostName,
            port,
        )
        logger.info("Host changed to: {}".format(args.host))
        self.__updatePrompt()

        # Update and show containers
        self.do_list(None)

        # Try to set Overlay FS images path on the new host
        # If it does not exist, fall back to default one
        setOverlayPathRes = self.__denv.setOverlayImagesPath(
            overlayImagesPath=self.__denv.getOverlayImagesPath()
        )
        if setOverlayPathRes is not ErrCodes.ERROR_NO_ERROR:
            logger.error(
                "Current OverlayFS image path is not present on {} host!\nFalling back to default:\n\tcurrent:\t{}\n\tdefault:\t{}".format(
                    self.__denv.getHost(),
                    self.__denv.getOverlayImagesPath(),
                    self.__denv.DEFAULT_REMOTE_OVERLAYFS_IMG_PATH,
                )
            )
            # Set the default path value explicitly
            self.__denv.setOverlayImagesPath(
                self.__denv.DEFAULT_REMOTE_OVERLAYFS_IMG_PATH, True
            )

        # Update overlay images choices
        self.__updateActiveOverlayImageChoices(self.overlayImagesArgChoices)

    overlayImgPathArgParser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog="This command needs to be called with valid positional argument(s), there are no default values",
    )
    overlayImgPathArgParser.add_argument(
        "overlay_fs_image_path",
        metavar="OVERLAY_FS_IMAGE_PATH",
        type=str,
        help="Complete path where the OverlayFS images are located on host",
    )

    @with_argparser(overlayImgPathArgParser)
    def do_set_overlay_img_path(self, args):
        """
        Set new OverlayFS images path on host
        """
        setOverlayPathRes = self.__denv.setOverlayImagesPath(
            overlayImagesPath=args.overlay_fs_image_path
        )

        if setOverlayPathRes == ErrCodes.ERROR_FOLDER_DOES_NOT_EXIST:
            logger.error(
                "Given path does not exist on {} host: {}".format(
                    self.__denv.getHost()
                    if self.__denv.getHost()
                    else self.DEFAULT_LOCAL_HOST_NAME,
                    args.overlay_fs_image_path,
                )
            )
        elif setOverlayPathRes == ErrCodes.ERROR_NO_ERROR:
            logger.info(
                "OverlayFS image path set sucessfully to: {}".format(
                    args.overlay_fs_image_path
                )
            )
        else:
            logger.error(
                "There was an issue with setting OverlayFS image path: {} (errCode = {})".format(
                    args.overlay_fs_image_path, setOverlayPathRes
                )
            )

        # Update overlay images choices
        self.__updateActiveOverlayImageChoices(self.overlayImagesArgChoices)

    def do_list_overlay_images(self, line):
        """
        List available OverlayFS images on host
        """
        overlayImages = self.__updateActiveOverlayImageChoices(
            self.overlayImagesArgChoices
        )

        logger.info(
            "OverlayFS images available on {} host: {}".format(
                self.__denv.getHost()
                if self.__denv.getHost()
                else self.DEFAULT_LOCAL_HOST_NAME,
                len(overlayImages) if overlayImages else 0,
            )
        )

        if overlayImages:
            for index, image in enumerate(overlayImages):
                logger.info("\t{}. {}".format(index + 1, image))

    def do_list(self, line):
        """
        List available containers on host
        """
        containers = self.__updateActiveContainerChoices(self.containerNamesArgChoices)

        logger.info(
            "Containers available on {} host: {}".format(
                self.__denv.getHost()
                if self.__denv.getHost()
                else self.DEFAULT_LOCAL_HOST_NAME,
                len(containers),
            )
        )

        for index, container in enumerate(containers):
            logger.info(
                "\t{}. {} {}".format(
                    index + 1,
                    container[0],
                    "[{}]".format(os.path.basename(container[1]))
                    if container[1] != ""
                    else "",
                )
            )

    stopArgParser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog="This command needs to be called with valid positional argument(s), there are no default values",
    )
    stopContainerNameArg = stopArgParser.add_argument(
        "container_name",
        metavar="CONTAINER_NAME",
        type=str,
        help="Complete name of container to stop",
    )

    @with_argparser(stopArgParser)
    def do_stop(self, args):
        """
        Stop container
        """

        logger.info("Stopping {} ..".format(args.container_name))

        self.__denv.stopContainer(args.container_name)
        self.do_list(None)

    def do_stop_all(self, line):
        """
        Stop all containers
        """
        self.__denv.stopAllContainers()
        self.do_list(None)

    startArgParser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog="Calling this comamnd without params is equal to calling it with all default argument values passed",
    )
    startArgParser.add_argument(
        "-lu",
        "--localuser",
        action="store_true",
        help="Run docker with local user context (if not set it will be root user)",
    )
    startArgParser.add_argument(
        "-n",
        "--name",
        metavar="CONTAINER_NAME",
        type=str,
        help="String identifier that will be part of the container name",
    )
    startArgParser.add_argument(
        "-i",
        "--image",
        metavar="DOCKER_IMAGE",
        type=str,
        help="Docker image to use (relative path to the docker repo)",
    )
    startArgParser.add_argument(
        "-w",
        "--workspace",
        metavar="WORKSPACE_PATH",
        type=str,
        help="Apsolute path on the remote host for the persisntent workspace",
    )

    @with_argparser(startArgParser)
    def do_start(self, args):
        """
        Spawn a new container

        If Any of the params are not set a default value will be used
        Default values are:
            not set -lu -> root user context will be used (needed for SSH ready docker containers)
            not set -n [container_name] = tempfs
            not set -i [docker_image_name] = master/aosp-generic-dev
            not set -w [remote_workspace_path] -> workspace will be mounted on tempFS

        Some examples:
            Start container with local user context and custom "MyContainer" name using "master/ndk" docker image and tempFS mounted workspace
            command: start -lu -n MyContainer -i master/ndk

            Start container with root user context and default values for name using default docker image and custom persistent workspace path
            command: start -w /home/workareas/myuser/work
        """
        containerName, containerId, containerAddress = self.__denv.startContainer(
            localUser=args.localuser,
            containerName=args.name,
            imageName=args.image,
            workspacePath=args.workspace,
        )

        logger.info(
            "Spawned container:\n\tname:\t{}\n\tid:\t{}\n\taddress:\t{}\n\tworkspace mount type:\t{} on path {}".format(
                containerName,
                containerId,
                containerAddress,
                "tmpfs" if args.workspace is None else "persistent",
                self.__denv.OVERLAYFS_WORKSPACE_MOUNT,
            )
        )

        # Update containers choices
        self.__updateActiveContainerChoices(self.containerNamesArgChoices)

    mountArgParser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog="This command needs to be called with valid required arguments, there are no default values",
    )
    mountArgParserReqiredArgsGroup = mountArgParser.add_argument_group(
        "required arguments"
    )
    mountContainerNameArg = mountArgParserReqiredArgsGroup.add_argument(
        "container_name",
        metavar="CONTAINER_NAME",
        type=str,
        help="Complete name of started container",
    )
    mountOverlayImageFileArg = mountArgParserReqiredArgsGroup.add_argument(
        "overlay_image_file",
        metavar="OVERLAY_IMAGE_FILE",
        type=str,
        help="Overlay image file to use (relative to the overlay image store path)",
    )

    @with_argparser(mountArgParser)
    def do_mount_overlay(self, args):
        """
        Mount an OvelrayFS image to the running container
        """

        mountRes = self.__denv.mountOverlayFS(
            overlayImageFile=args.overlay_image_file,
            containerName=args.container_name,
        )

        if mountRes == ErrCodes.ERROR_OVERLAYFS_IMAGE_NOT_FOUND:
            logger.error(
                "OverlayFS image file {} does not exist".format(args.overlay_image_file)
            )
        elif mountRes == ErrCodes.ERROR_MOUNT_NOT_POSSIBLE:
            logger.error(
                "OverlayFS already mounted in {} container".format(args.container_name)
            )
        elif mountRes == ErrCodes.ERROR_NO_ERROR:
            logger.info(
                "OverlayFS image mounted sucessfully:\n\timage:\t{}\n\tcontainer:\t{}\n\tmount point:\t{}".format(
                    args.overlay_image_file,
                    args.container_name,
                    self.__denv.OVERLAYFS_WORKSPACE_MOUNT,
                )
            )
        else:
            logger.error(
                "There was an issue with mounting of OverlayFS image {} inside the container {} (errCode = {})".format(
                    args.overlay_image_file, args.container_name, mountRes
                )
            )

    unmountArgParser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog="This command needs to be called with valid required arguments, there are no default values",
    )
    unmountArgParserReqiredArgsGroup = unmountArgParser.add_argument_group(
        "required arguments"
    )
    unmountContainerNameArg = unmountArgParserReqiredArgsGroup.add_argument(
        "container_name",
        metavar="CONTAINER_NAME",
        type=str,
        help="Complete name of started container",
    )

    @with_argparser(unmountArgParser)
    def do_unmount_overlay(self, args):
        """
        Un-mount currently mounted OvelrayFS image on the running container
        """
        unmountRes = self.__denv.unmountOverlayFS(containerName=args.container_name)

        if unmountRes == ErrCodes.ERROR_MOUNT_NOT_POSSIBLE:
            logger.error(
                "OverlayFS already unmounted in {} container".format(
                    args.container_name
                )
            )
        elif unmountRes == ErrCodes.ERROR_NO_ERROR:
            logger.info(
                "OverlayFS image un-mounted sucessfully:\n\tcontainer:\t{}\n\tmount point:\t{}".format(
                    args.container_name, self.__denv.OVERLAYFS_WORKSPACE_MOUNT
                )
            )
        else:
            logger.error(
                "There was an issue with un-mounting of OverlayFS image inside the container {} (errCode = {})".format(
                    args.container_name, unmountRes
                )
            )

    remoteShellArgParser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        epilog="Calling this comamnd without params is equal to calling it with current host passed as argument",
    )
    remoteShellContainerNameArg = remoteShellArgParser.add_argument(
        "container_name",
        nargs="?",
        default=None,
        metavar="CONTAINER_NAME/HOST",
        type=str,
        help="Complete name of started container or host",
    )

    remoteShellArgParser.add_argument(
        "-c",
        "--command",
        metavar="COMMAND",
        type=str,
        help="Optional command to run on remote shell",
    )

    @with_argparser(remoteShellArgParser)
    def do_spawn_remote_shell(self, args):
        """
        Spawn a remote shell session

        If no parameter is passed, session will be created with current host machine
        """
        if args.container_name is None and self.__denv.getHost() is None:
            logger.info(
                "There is no point in spawning shell session with local host! Aborting."
            )
        else:
            if args.command:
                logger.info(
                    "Running command on {}".format(
                        self.__denv.getHost()
                        if args.container_name is None
                        else args.container_name
                    )
                )
            else:
                logger.info(
                    'Spawning shell on {}, to exit back from shell type "exit"'.format(
                        self.__denv.getHost()
                        if args.container_name is None
                        else args.container_name
                    )
                )
            self.__denv.spawnSshShellSession(args.container_name, args.command)

    def do_clear(self, line):
        """
        Clear the console screen
        """
        self.do_shell(
            "{}".format(
                self.CLEAR_CMD_UNIX
                if sys.platform == PLATFORM_OS_LINUX
                or sys.platform == PLATFORM_OS_MACOS
                else self.CLEAR_CMD_WIN32
            )
        )

    # List of arguments that need update for container choices
    containerNamesArgChoices = [
        mountContainerNameArg,
        unmountContainerNameArg,
        stopContainerNameArg,
        remoteShellContainerNameArg,
    ]

    # List of arguments that need update for OverlayFS image choices
    overlayImagesArgChoices = [mountOverlayImageFileArg]

    # Definition of private and public methods that are not part of the cmdLoop starts from this line

    def __updatePrompt(self):
        """
        Updates the comand prompt with current username and hostname
        """
        cmd2.Cmd.prompt = "({}@{}) ".format(
            self.__denv.getUsername(),
            self.__denv.getHost()
            if self.__denv.getHost()
            else self.DEFAULT_LOCAL_HOST_NAME,
        )

    def __updateActiveContainerChoices(self, argParamsList=None):
        """
        Updates the contaner list choices for passed argParams list

        @param argParamsList - List of argparams to update choices for
        @return - list of active containers

        """
        containers = self.__denv.listContainers()

        # Get only container names for argParams choices
        containerNames = [container[0] for container in containers]

        if argParamsList:
            for arg in argParamsList:
                arg.choices = containerNames if len(containerNames) > 0 else None

        return containers

    def __updateActiveOverlayImageChoices(self, argParamsList=None):
        """
        Updates the OverlayFS image list choices for passed argParams list

        @param argParamsList - List of argparams to update images for
        @return - list of active OverlayFS images

        """
        overlayImages = self.__denv.listOverlayImages()

        if argParamsList:
            for arg in argParamsList:
                arg.choices = (
                    overlayImages if overlayImages and len(overlayImages) > 0 else None
                )

        if not overlayImages or len(overlayImages) == 0:
            logger.info(
                "Warning: There are no Overlay FS image files found on current image path!"
            )

        return overlayImages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[denv] %(levelname)s/%(name)s: %(message)s",
    )

    App().cmdloop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
