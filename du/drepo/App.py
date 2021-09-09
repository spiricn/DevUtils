import argparse
import logging
import sys
import os
import traceback
import time
import datetime

import du
from du.utils.ShellCommand import CommandFailedException
from du.drepo.DRepo import DRepo, Credentials
from du.drepo.Commands import DownloadType
from du.drepo.manifest.Parser import Parser as ManifestParser
from du.drepo.report.HtmlGenerator import HtmlGenerator
from du.drepo.report.VersionGenerator import VersionGenerator
from du.gerrit.Utils import Utils as GerritUtils


def parseHttpCredentials(credentialsList):
    """
    Parse a list of "server,username,password" raw strings

    @param credentialsList List of credentail strings
    @return credentials dictionary
    """
    httpCredentials = {}

    if not credentialsList:
        return {}

    for cred in credentialsList:
        tokens = cred.split(",")

        # Expecting server,username,password tripplets
        if len(tokens) != 3:
            raise RuntimeError(
                "Unexpected HTTP credential format, expecting <server>,<username>,<password>: got %r"
                % cred
            )

        server, username, password = (token.strip() for token in tokens)

        # Check for duplicates
        if server in httpCredentials:
            raise RuntimeError("Duplicate HTTP credential for server %r" % server)

        httpCredentials[server] = Credentials(username, password)

    return httpCredentials


def parseReportGenerators(reportArgs):
    """
    Given a a list of report arguments, create a list of (path, generator) pairs

    @param reportArgs List of report arguments
    @return list of paths & generators
    """
    # Report type name -> generator function map
    reportGeneratorTypeMap = {
        "html": HtmlGenerator.generate,
        "version": VersionGenerator.generate,
    }

    reports = []

    for arg in reportArgs:
        # Look for arguments which explicitly specify the type fo the report
        if ":" not in arg:
            # Default to HTML
            reports.append((arg, HtmlGenerator.generate))
            continue

        tokens = arg.split(":")
        if len(tokens) != 2:
            raise RuntimeError(
                "Invalid report format. Expected <type>:<path>, got %r" % arg
            )

        reportTypeName, reportPath = tokens

        if reportTypeName not in reportGeneratorTypeMap:
            # Not supported
            raise RuntimeError("Unrecognized report type %r" % reportTypeName)

        reportGenerator = reportGeneratorTypeMap[reportTypeName]

        reports.append((reportPath, reportGenerator))

    return reports


def main():
    startTime = time.time()

    parser = argparse.ArgumentParser()

    parser.add_argument("-manifest_file", help="path to manifest file")
    parser.add_argument("-manifest_source", help="manifest source string")
    parser.add_argument(
        "-match_tag",
        nargs="?",
        default=None,
        help="tag name string to match; if set, it will match only those tags in release notes generation;"
        + "if not set, it will match first tag found and only on HEAD change of the repo",
    )
    parser.add_argument(
        "-notes",
        nargs="+",
        help="Report path; if set report will be generated and stored here",
    )
    parser.add_argument(
        "-sync",
        action="store_true",
        help="if provided, drepo will syncrhonize source code",
    )
    parser.add_argument("-build")
    parser.add_argument(
        "-verbose",
        action="store_true",
        help="If set, verbose logs & command output are enabled. Used for debugging purposes.",
    )
    parser.add_argument(
        "-ci_change",
        help="""Continous integration gerrit change ID. If specified, current manifest build final
touches will be overriden with latest patchset of changes which shared this ID. Alternatively an environment variable may be specified from which
the changeID shall be retreived""",
    )
    parser.add_argument(
        "-ci_type",
        type=DownloadType,
        metavar="{"
        + str(DownloadType.valueList())
        .replace("[", "")
        .replace("]", "")
        .replace("'", "")
        + "}",
        choices=list(DownloadType),
        help="""Defines a way to download the CI commit
        merge(DEFAULT) - Pulls the change and its predecessors on top of the base (may fail in case there's a conflict)
        checkout - Checks out the change, overwriting any base (never fails)
        cherrypick - Cherry-picks the change on top of whichever base was set (may fail in case there's a conflict with the base)
        """,
    )
    parser.add_argument(
        "-http_credentials",
        nargs="+",
        help="A list of HTTP credentials to be used for cloning/REST calls.\nEach entry is formated as such: server,username,password",
    )
    parser.add_argument(
        "-fetch_depth",
        type=int,
        help="If specified only specific number of commits will be fetched, as opposed to the entire git history",
    )
    parser.add_argument("-j", type=int, default=1, help="Number of threads")

    parser.add_argument(
        "-root",
        help="Build root override. If specified this path will be used instead of the root defined in the build manifest",
    )

    parser.add_argument(
        "-ci_only",
        action="store_true",
        help="If specified, clones only the projects with CI changes",
    )

    parser.add_argument(
        "-tag",
        help="Tag to be checked out for all projects. Useful for releases",
    )

    parser.add_argument(
        "-report_depth",
        type=int,
        default=3,
        help="Number indicating how many merged commits will be displayed in the reports",
    )

    forallArg = "-forall"
    # The argument entry here is just a placeholder for the help doc, we're doing the parsing manually
    parser.add_argument(forallArg, help="Command to execute in all project directories")

    forallCommand = None
    if forallArg in sys.argv:
        # Find the the forall argument start
        forallStartIndex = sys.argv.index(forallArg)

        # Command is everything that comes after it
        forallCommand = sys.argv[forallStartIndex + 1 :]

        # Remove the forall from arguments so that it doesn't affect the parser
        sys.argv = sys.argv[:forallStartIndex]

        # TODO This is not the most ideal way of doing this, but other solutions
        # such as argparse.REMAINDER have ugly corner cases which break the parsing (e.g. ambigious option error etc.)

    args = parser.parse_args()
    httpCredentials = {}

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[drepo] %(levelname)s/%(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__.split(".")[-1])

    logger.info("du version %s", du.__version_name__)

    if args.manifest_file and args.manifest_source:
        logger.error(
            "arguments -manifest_file and -manifest_source are mutually exclusive"
        )
        return -1
    elif args.manifest_file:
        with open(args.manifest_file, "rb") as fileObj:
            manifestSource = fileObj.read()

    elif args.manifest_source:
        manifestSource = args.manifest_source

    else:
        logger.error("manifest not provided")
        return -1

    logger.debug("parsing manifest ..")

    try:
        manifest = ManifestParser.parseString(manifestSource)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("*" * 80)
        logger.error("\t\terror parsing manifest: %r" % str(e))
        logger.error("*" * 80)
        return -1

    drepo = None

    # Create DRepo
    try:
        # Parse HTTP credentials
        httpCredentials = parseHttpCredentials(args.http_credentials)

        ciChange = args.ci_change

        # Check if provided CI change is a gerrit change ID, or an environment variable
        if args.ci_change and not GerritUtils.isValidChangeId(args.ci_change):

            # It's an environment variable, so try to get it
            logger.debug("Getting CI change ID from env variable %r" % args.ci_change)
            ciChange = os.getenv(args.ci_change)

        drepo = DRepo(
            manifest,
            ciChange=ciChange,
            ciType=(args.ci_type if args.ci_type else DownloadType.MERGE),
            httpCredentials=httpCredentials,
            fetchDepth=args.fetch_depth,
            ciOnly=args.ci_only,
            tag=args.tag,
        )

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("*" * 80)
        logger.error("\t\terror creating drepo: %r" % str(e))
        logger.error("*" * 80)
        return -1

    # Sync
    if args.sync:
        logger.info("syncing ..")
        try:
            drepo.sync(numThreads=args.j, buildRoot=args.root)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("*" * 80)
            logger.error("\t\tsync error: %r" % str(e))
            logger.error("*" * 80)
            return -1

    if forallCommand:
        try:
            drepo.execute(forallCommand)
        except CommandFailedException as e:
            logger.error(traceback.format_exc())
            logger.error("*" * 80)
            logger.error("\t\tforall error: %r" % str(e))
            logger.error("*" * 80)
            return e.command.returnCode

    # Generate reports (of possibly various types)
    if args.notes:
        logger.info("generating reports ..")

        reports = parseReportGenerators(args.notes)

        # Generate all reports
        for reportPath, reportGenerator in reports:
            logger.info(
                "generating report %s to %r .." % (str(reportGenerator), reportPath)
            )
            try:
                drepo.generateReport(
                    reportPath,
                    reportGenerator,
                    args.report_depth,
                    args.match_tag,
                    numThreads=args.j,
                )
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error("*" * 80)
                logger.error("\t\terror generating release notes: %r" % str(e))
                logger.error("*" * 80)
                return -1

    endTime = time.time()

    logger.info("-------------------------------")
    logger.info(
        "execution time {}".format(datetime.timedelta(seconds=endTime - startTime))
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
