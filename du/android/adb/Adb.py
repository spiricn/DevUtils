from du.utils.ShellCommand import CommandFailedException, ShellCommand

import time
import logging

logger = logging.getLogger(__name__.split(".")[-1])


class Adb:
    """
    ADB daemon wrapper
    """

    # SE linux status strings
    SE_LINUX_PERMISSIVE = "Permissive"
    SE_LINUX_ENFORCING = "Enforcing"

    DEFAULT_ADB_PORT = ":5555"

    # Time we should wait before ADB commands that are prone to failure (due to bugs)
    QUIET_TIME_SEC = 1

    # Number of retries to do in case first connect ping fails
    NUM_CONNECT_PING_RETRIES = 3

    def __init__(self, adb="adb"):
        """
        Constructor

        @param adb Path to ADB binary
        """

        self.__adb = adb

        # Set the first device as active, by default
        devices = self.getAttachedDevices()
        if devices:
            self.__activeDevice = devices[0]
        else:
            self.__activeDevice = None

    def getAttachedDevices(self):
        """
        Get a list of attached devices
        """

        return [
            i.split()[0]
            for i in ShellCommand.execute([self.__adb, "devices"])
            .stdoutStr.strip()
            .splitlines()[1:]
        ]

    def connect(self, address):
        """
        Connect to a device and set it as active

        @param address Device address
        """

        # Append port if not specified (otherwise -s might not work)
        if not address.endswith(self.DEFAULT_ADB_PORT):
            address += self.DEFAULT_ADB_PORT

        logger.debug("connect {}".format(address))

        oldDevice = self.__activeDevice

        self.__activeDevice = None

        self.execute(["connect", address])

        # Wait a bit and test the connection
        time.sleep(self.QUIET_TIME_SEC)

        logger.debug("check connection ..")

        self.__activeDevice = address
        connected = False
        for i in range(self.NUM_CONNECT_PING_RETRIES):
            try:
                self.ping()
                connected = True
                break
            except CommandFailedException as e:
                logger.debug("ping failed: {}".format(e))

                if i != self.NUM_CONNECT_PING_RETRIES - 1:
                    logger.debug("re-trying ..")
                    time.sleep(self.QUIET_TIME_SEC)

        if not connected:
            self.__activeDevice = oldDevice

            raise RuntimeError("could not ping device")

    def ping(self):
        """
        Check if the device is responsive, by executing a command
        """

        self.__checkDeviceActive()

        testStr = "42"

        # Echo via shell command, and verify output
        if self.shell(["echo", testStr]).stdoutStr.strip() != testStr:
            raise RuntimeError("Not alive")

    def remount(self):
        """
        Remount as RW
        """

        self.root()

        self.execute("remount")

    def setDevice(self, address):
        """
        Set active device address
        """

        self.__activeDevice = address

    def disconnect(self):
        """
        Disconnect from all devices
        """

        self.__checkDeviceActive()

        self.execute("disconnect")

        self.__activeDevice = None

    def execute(self, command):
        """
        Execute an ADB command
        """
        if not isinstance(command, list):
            command = [command]

        return ShellCommand.execute(self.__getCommand(command))

    def root(self):
        """
        Restart ADB daemon as root
        """

        self.__checkDeviceActive()

        self.execute("root")

        time.sleep(self.QUIET_TIME_SEC)

        self.reconnect()

        self.shell(["su", "--help"])

    def reconnect(self):
        """
        Disconnect and connect to the device
        """

        self.__checkDeviceActive()

        address = self.__activeDevice

        self.disconnect()

        self.connect(address)

    def shell(self, command):
        """
        Execute a shell command

        @return ShellCommand object
        """

        self.__checkDeviceActive()

        return self.execute(["shell"] + command)

    def setSeLinuxEnabled(self, enabled):
        """
        Enable or disable SE linux
        """

        self.__checkDeviceActive()

        # Need to be rooted
        self.root()

        self.shell(["setenforce", "1" if enabled else "0"])

        # Check if OK
        assert enabled == self.isSeLinuxEnabled()

    def isSeLinuxEnabled(self):
        """
        Check if SE linux is enabled

        @return True if enabled
        """

        self.__checkDeviceActive()

        currentStatus = self.shell(["getenforce"]).stdoutStr.strip()

        assert currentStatus in [self.SE_LINUX_PERMISSIVE, self.SE_LINUX_ENFORCING]

        return currentStatus == self.SE_LINUX_ENFORCING

    def __checkDeviceActive(self):
        """
        Check if a device is set, and throw if not
        """

        if not self.__activeDevice:
            raise RuntimeError("no active devices")

    def __getCommand(self, command):
        """
        Construct a full ADB shell command
        """

        # ADB binary
        base = [self.__adb]

        # Add device selection if device is set
        if self.__activeDevice:
            base += "-s", self.__activeDevice

        return base + command
