import argparse
import logging
import sys
import os
import traceback
import time

from du.afact.Afact import Afact
import tempfile
import zipfile

logger = logging.getLogger(__name__.split(".")[-1])


def run(args, adbArgs):
    root = args.root
    manifestPath = args.manifest_file

    # If manifest path is a zip, unzip the contents first (assume it was created via the -create_archive option)
    if os.path.splitext(manifestPath)[1] == ".zip":
        logger.info("reading from zip archive")

        # New root is the path of our temporary directory where the archive is extracted
        root = tempfile.TemporaryDirectory().name

        with zipfile.ZipFile(args.manifest_file, "r") as zipf:
            zipf.extractall(root)

        # Manifest should be in the archive
        manifestPath = os.path.join(root, Afact.ARCHIVE_MANIFEST_FILENAME)

    afact = Afact(manifestPath, root if root else os.getcwd())

    # Create archive
    if args.create_archive:
        logger.info("creating archive at {} ..".format(args.create_archive))
        afact.createArchive(args.create_archive)

    # Install artifacts
    if args.install:
        afact.adbInstall(force=args.f, adbArgs=adbArgs)

    logger.info("done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_file", help="Path to manifest file")
    parser.add_argument(
        "-root", help="Root path all the artifacts in the manifest are relative to"
    )
    parser.add_argument("-verbose", action="store_true", help="Enable verbose logs")
    parser.add_argument(
        "-create_archive", help="Create zip archive out of the artifacts & manifest"
    )
    parser.add_argument(
        "-install", action="store_true", help="Install the artifacts on target device"
    )

    parser.add_argument("-f", action="store_true", help="Force install")

    adbArgsCommand = "-adb_args"
    # The argument entry here is just a placeholder for the help doc, we're doing the parsing manually
    parser.add_argument(
        adbArgsCommand, help="Additional arguments to provide to underlying ADB command"
    )

    adbArgs = None
    if adbArgsCommand in sys.argv:
        # Find the the forall argument start
        adbArgsStartIndex = sys.argv.index(adbArgsCommand)

        # Command is everything that comes after it
        adbArgs = sys.argv[adbArgsStartIndex + 1 :]

        # Remove the forall from arguments so that it doesn't affect the parser
        sys.argv = sys.argv[:adbArgsStartIndex]

        # TODO This is not the most ideal way of doing this, but other solutions
        # such as argparse.REMAINDER have ugly corner cases which break the parsing (e.g. ambiguous option error etc.)

    # Parse
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[afact] %(levelname)s/%(name)s: %(message)s",
    )

    try:
        run(args, adbArgs)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("*" * 80)
        logger.error("\t\t{}".format(e))
        logger.error("*" * 80)
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
