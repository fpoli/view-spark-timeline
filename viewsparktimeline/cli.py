import sys
import argparse
import random
from viewsparktimeline import __version__, __prog_name__
from viewsparktimeline.generator import generate
from viewsparktimeline.exceptions import CliException


def create_parser():
    parser = argparse.ArgumentParser(
        prog=__prog_name__,
        description="Visualize the timeline of a Spark execution from its log file. (v{})".format(
            __version__
        )
    )
    parser.add_argument(
        "-i", "--input-log",
        required=True,
        help="path to the spark's application log"
    )
    parser.add_argument(
        "-o", "--output-image",
        required=True,
        help="path of the output image"
    )
    parser.add_argument(
        "-u", "--time-uncertainty",
        default=0,
        type=int,
        help=(
            "maximum allowed time uncertainty (in ms) of the timestamps in the log file. "
            "An high uncertainty determines a slower, but more robust, execution. (Default: 0)"
        )
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="print version and exit"
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.version:
        print("{} version {}".format(__prog_name__, __version__))
        return
    try:
        random.seed(42)
        generate(
            args.input_log,
            args.output_image,
            args.time_uncertainty
        )
    except CliException as e:
        print(e)
        sys.exit(1)
