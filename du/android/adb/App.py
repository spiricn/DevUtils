from os import system
from du.android.adb.Adb import Adb
import sys
import logging
import cmd2
import time
import argparse
from collections import namedtuple
from cmd2 import with_argparser

logger = logging.getLogger(__name__.split(".")[-1])

ProcInfo = namedtuple("ProcInfo", "cpu,memory")

SystemInfo = namedtuple("SystemInfo", "memFree")

MemInfo = namedtuple("MemInfo", "java, native, code, total")


class App(cmd2.Cmd):
    """
    Interactive & scriptable wrapper over Adb
    """

    def __init__(self):
        super().__init__()

        self.__adb = Adb()

    def do_connect(self, address):
        logger.info("connecting to {} ..".format(address))

        self.__adb.connect(address)

        logger.info("connected OK")

    def do_remount(self, args):
        self.__adb.remount()

    def do_root(self, args):
        self.__adb.root()

    def do_disableSeLinux(self, args):
        self.__adb.setSeLinuxEnabled(False)

    # waitProcessStart arguments parser
    startArgParser = argparse.ArgumentParser()
    startArgParser.add_argument(
        "package", help="Name of package we are waiting to start"
    )
    startArgParser.add_argument(
        "--sleepTime",
        default=1,
        type=float,
        help="Sleep time[s] between checks => 1 s default",
    )
    startArgParser.add_argument(
        "--numAttempts", default=10, type=int, help="How much attempts to use"
    )

    @with_argparser(startArgParser)
    def do_waitProcessStart(self, args):
        """
        Wait for process to start.

        If process doesn't start in a timely manner, terminate
        """

        logger.info(
            "waiting for process {} to start (attempts {}, sleep time {})".format(
                args.package, args.numAttempts, args.sleepTime
            )
        )

        # Try to get package PID
        for i in range(args.numAttempts):
            pid = self.__getPackagePid(args.package)
            if pid:
                logger.info("process {} alive with pid {}".format(args.package, pid))
                return

            # Try again
            time.sleep(args.sleepTime)

        logger.error("timed out waiting for process")
        sys.exit(-1)

    # waitProcessFinish arguments parser
    finishArgParser = argparse.ArgumentParser()
    finishArgParser.add_argument(
        "package", help="Name of package we are waiting to finish"
    )
    finishArgParser.add_argument(
        "--sleepTime",
        default=0.2,
        type=float,
        help="Sleep time[s] between checks => 200 ms default",
    )

    @with_argparser(finishArgParser)
    def do_waitProcessFinish(self, args):
        """
        Wait for process to finish
        """
        pid = None

        logger.info(
            "Waiting for process {} to finish (sleep time {})".format(
                args.package, args.sleepTime
            )
        )

        # Try to get package PID
        while True:
            pid = self.__getPackagePid(args.package)
            if not pid:
                logger.info("process {} finished".format(args.package))
                return

            time.sleep(args.sleepTime)

    monitorProcessArgs = argparse.ArgumentParser()
    monitorProcessArgs.add_argument(
        "package", help="Name of package we are waiting to finish"
    )
    monitorProcessArgs.add_argument("outFile", help="Output file")
    monitorProcessArgs.add_argument("--numSamples", help="Number of samples", type=int)
    monitorProcessArgs.add_argument(
        "--frequency", help="Monitor frequency in seconds", type=float, default=2
    )

    @with_argparser(monitorProcessArgs)
    def do_monitorProcess(self, args):
        targetPid = self.__getPackagePid(args.package)
        if not targetPid:
            raise RuntimeError("Could not find pid of package {}".format(args.package))

        logger.info("monitoring pid {}/{} ..".format(args.package, targetPid))

        def output(fileObj, content):
            fileObj.write(content)
            fileObj.flush()

            logger.info(content.strip())

        with open(args.outFile, "w") as fileObj:
            output(fileObj, "{:15} {:15}\n".format("CPU", "Memory(MiB)"))

            counter = 0

            while True:
                # Start measuring time
                iterationStartTime = time.time()

                counter += 1

                if args.numSamples and counter == args.numSamples:
                    break

                procInfo = self.__getProcInfo(targetPid)
                memInfo = self.__getMemInfo(args.package)

                output(
                    fileObj,
                    "{:15.2f} {:15.2f}\n".format(procInfo.cpu, memInfo.total / 1024.0),
                )

                # Sleep if needed
                iterationDuration = time.time() - iterationStartTime
                sleepTime = args.frequency - iterationDuration

                if sleepTime > 0:
                    time.sleep(sleepTime)

    def __getMemInfo(self, package):
        java = None
        native = None
        code = None
        total = None

        for i in self.__adb.shell(
            ["dumpsys", "meminfo", package]
        ).stdoutStr.splitlines():
            line = i.strip()

            tokens = line.split(":")

            if line.startswith("Java Heap:"):
                java = int(tokens[1])
            elif line.startswith("Native Heap:"):
                native = int(tokens[1])
            elif line.startswith("Code:"):
                code = int(tokens[1])
            elif line.startswith("TOTAL:"):
                total = int(tokens[1].strip().split(" ")[0])

        return MemInfo(java, native, code, total)

    def __getProcInfo(self, targetPid):
        for i in self.__adb.shell(
            ["top", "-n", 1, "-o", "PID,%CPU,%MEM"]
        ).stdoutStr.splitlines():
            tokens = i.split(" ")
            tokens = [i.strip() for i in tokens if i]

            if len(tokens) != 3:
                continue

            pid = int(tokens[0])
            cpu = float(tokens[1])
            mem = float(tokens[2])

            if pid == targetPid:
                return ProcInfo(cpu, mem)

    def __getSystemInfo(self):
        for i in self.__adb.shell(["cat", "/proc/meminfo"]).stdoutStr.splitlines():
            tokens = [i for i in i.split(" ") if i.strip()]

            if tokens[0] == "MemFree:":
                return SystemInfo(int(tokens[1]))

    def __getPackagePid(self, targetPackage):
        """
        Get PID of the package with given name
        """

        for package, pid in self.__getActiveProcesses():
            if package == targetPackage:
                return int(pid)

        return None

    def __getActiveProcesses(self):
        """
        Get a list of active processes and their PIDS
        """

        activeProcesses = []

        psLines = self.__adb.shell(["ps"]).stdoutStr.splitlines()[1:]

        for line in psLines:
            tokens = line.split(" ")

            tokens = [i for i in tokens if i.strip()]

            pid = int(tokens[1])
            package = tokens[-1]

            activeProcesses.append((package, pid))

        return activeProcesses

    def perror(self, final_msg, end, apply_style):
        """
        A cmd2 override. If any of the commands fail, abort execution right away

        TODO There's probably a better way of doing this ..
        """
        logger.error("exception ocurred:\n" + final_msg)
        sys.exit(-1)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[adb] [%(asctime)s.%(msecs)03d] %(levelname)s/%(name)s: %(message)s",
        datefmt="%I:%M:%S",
    )

    return App().cmdloop()


if __name__ == "__main__":
    sys.exit(main())
