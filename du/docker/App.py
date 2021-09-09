import argparse
import logging
import sys
import traceback
import os
from du.docker.Preprocessor import Preprocessor


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("dockerfile", help="Path to input dockerfile")

    args = parser.parse_args()

    try:
        # Process input file
        result = Preprocessor.preprocess(args.dockerfile)

        # Output to stdout
        outPath = os.path.splitext(args.dockerfile)[0]
        print("Writing output: %r" % outPath)

        with open(outPath, "w") as fileObj:
            fileObj.write(result)

    except Exception as e:
        sys.stderr.write("Preprocess failed: %s\n" % str(e))
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
