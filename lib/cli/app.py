"""Commandline interface"""

from lib.cli import args
from lib.cli.snapper import snapshot_action
from lib.cli.cluster import cluster_action

def run():

    parser = args.arg_parser()
    cli_args = parser.parse_args()
    opts = args.extra_opts(cli_args)

    if not cli_args.action or not cli_args.group:
        parser.print_help()
        return

    if cli_args.group == args.GROUP["SNAPSHOT"]:
        snapshot_action(cli_args.action, opts)
    elif cli_args.group == args.GROUP["CLUSTER"]:
        cluster_action(cli_args.action, opts)
    else:
        raise Exception("Invalid action group '{}'".format(cli_args.group))
