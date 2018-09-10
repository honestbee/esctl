"""Commandline interface"""

from lib.cli.arg_parser import arg_parser
import json


SENSITIVE = ["http_password"]


def run():
    parser = arg_parser()
    args = parser.parse_args()
    if "debug" in args and args.debug:
        print_args(args)
    args.func(**vars(args))


def print_args(args):
    """Print options for debugging"""
    hsh = {}
    for key, value in vars(args).items():
        if value is None or key == "func":
            continue
        if key in SENSITIVE:
            hsh[key] = "*****"
        else:
            hsh[key] = value
    print(json.dumps(dict(options=hsh)))
