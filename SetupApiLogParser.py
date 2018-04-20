import json
import logging
import argparse
import SaLogHandler as Slh

VALID_DEBUG_LEVELS = ["ERROR", "WARN", "INFO", "DEBUG"]


def get_arguments():
    usage = '''Parse Setup API log files to JSONL.'''

    arguments = argparse.ArgumentParser(
        description=(usage)
    )
    arguments.add_argument(
        "-s", "--source",
        dest="source",
        action="store",
        required=True,
        help="Source file."
    )
    arguments.add_argument(
        "--debug",
        dest="debug",
        action="store",
        default="ERROR",
        choices=VALID_DEBUG_LEVELS,
        help="Debug level [default=ERROR]"
    )

    return arguments


def set_debug_level(debug_level):
    if debug_level in VALID_DEBUG_LEVELS:
        logging.basicConfig(
            level=getattr(logging, debug_level)
        )
    else:
        raise(Exception("{} is not a valid debug level.".format(debug_level)))


def main():
    arguments = get_arguments()
    options = arguments.parse_args()

    set_debug_level(options.debug)

    with open(options.source, "rb") as file_io:
        log_reader = Slh.SetupApiLogHandler(
            file_io, options.source
        )
        for sh in log_reader.iter_sections():
            record = sh.as_dict()
            print(json.dumps(record))


if __name__ == "__main__":
    main()
