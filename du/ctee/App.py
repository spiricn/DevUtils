import argparse
import signal
import sys

from du.ctee.Ctee import Ctee
from du.ctee.processors.GccProcessor import GccProcessor
from du.ctee.processors.LogcatProcessor import LogcatProcessor
from du.ctee.processors.PasstroughProcessor import PasstroughProcessor
from du.ctee.processors.PolyProcessor import PolyProcessor
from du.ctee.transformers.HtmlTransformer import HtmlTransformer
from du.ctee.transformers.PasstroughTransformer import PasstroughTransformer
from du.ctee.transformers.TerminalTransformer import TerminalTransformer


PROCESSOR_MAP = {
    "logcat": LogcatProcessor,
    "gcc": GccProcessor,
    "passtrough": PasstroughProcessor,
    "poly": PolyProcessor,
}

TRANSFORMER_MAP = {
    "terminal": TerminalTransformer,
    "passtrough": PasstroughTransformer,
    "html": HtmlTransformer,
}


def interruptHandler(signal, frame, ctee):
    ctee.stop()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-stylesheet",
        help="if provided, app will output the stylesheet for given processor and exit",
    )
    parser.add_argument(
        "-input", help="input file. To use STDIN instead, set this to -"
    )
    parser.add_argument(
        "-processor",
        help="input stream processor. Available processors: %s"
        % ",".join(PROCESSOR_MAP.keys()),
    )
    parser.add_argument(
        "-outputs",
        nargs="+",
        help="iist of <output,transformer> pairs; available transformers: %s"
        % (",".join(TRANSFORMER_MAP.keys())),
    )

    args = parser.parse_args()

    if args.stylesheet:
        if args.stylesheet in PROCESSOR_MAP:
            print(PROCESSOR_MAP[args.stylesheet].getDefaultStylesheet())
            return 0

        else:
            print("invalid processor name %r" % args.processor)
            return -1

    ctee = Ctee()

    inputStream = None

    closeFd = True
    if args.input == "-":
        args.input = 0
        closeFd = False
    elif args.input:
        inputStream = open(args.input, "rb")
    else:
        print("input not provided")
        return -1

    inputStream = open(0, "r", closefd=closeFd, encoding="utf8", errors="replace")

    if args.processor in PROCESSOR_MAP:
        processor = PROCESSOR_MAP[args.processor]()
    else:
        print("invalid processor name %r" % args.processor)

    ctee.setInput(inputStream, processor)

    if not args.outputs:
        # Default to terminal output/stdout
        ctee.addOutput(sys.stdout, TerminalTransformer())
    else:
        for i in range(0, len(args.outputs), 2):
            outputStream = args.outputs[i + 0]
            outputTransformerName = args.outputs[i + 1]

            if outputStream == "-":
                outputStream = sys.stdout
            else:
                outputStream = open(outputStream, "w")

            if outputTransformerName in TRANSFORMER_MAP:
                transformer = TRANSFORMER_MAP[outputTransformerName]()
            else:
                raise RuntimeError(
                    "Invalid transformer name %r" % outputTransformerName
                )

            ctee.addOutput(outputStream, transformer)

    signal.signal(
        signal.SIGINT, lambda signal, frame: interruptHandler(signal, frame, ctee)
    )

    ctee.start()

    ctee.wait()

    return 0


if __name__ == "__main__":
    sys.exit(main())
