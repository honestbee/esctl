"""Commandline interface"""

from lib.cli import args
from lib.cli.snapper import snapshot_action
from lib.cli.cluster import cluster_action


BLACKLIST = ["http_password"]


def run():

    parser = args.arg_parser()
    opts = vars(parser.parse_args())

    print_args(opts)

    if "action" not in opts or "group" not in opts:
        parser.print_help()
        return

    group = opts["group"]
    action = opts["action"]

    if group == args.GROUP["SNAPSHOT"]:
        snapshot_action(action, opts)
    elif group == args.GROUP["CLUSTER"]:
        cluster_action(action, opts)
    else:
        raise Exception("Invalid action group '{}'".format(opts.group))


def print_args(args):
    """Print options for debugging"""
    print("Options:")
    for key, value in args.items():
        if value is None:
            continue
        if key in BLACKLIST:
            print("  {}: ******".format(key))
        else:
            print("  {}: {}".format(key, value))
    print() # empty line
