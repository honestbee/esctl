#!/usr/bin/env python3

"""Snapshot and restore utility for Elasticsearch"""

from lib.snapper import Snapper
from lib.args import arg_parser, ACTION


def main():
    """Entry point"""
    parser = arg_parser()
    args = parser.parse_args()
    opts = vars(args)

    _print_opts(opts)

    snapper = Snapper(opts)

    if not args.command:
        parser.print_help()
    elif args.command == ACTION["SNAPSHOT"]:
        _do_snapshot(snapper, opts)
    elif args.command == ACTION["RESTORE"]:
        _do_restore(snapper, opts)
    elif args.command == ACTION["LIST"]:
        _do_list(snapper)
    elif args.command == ACTION["CLEANUP"]:
        _do_cleanup(snapper, opts)
    else:
        raise Exception("Invalid command: '"+args.command+"'")


def _print_opts(opts):
    """Print options for debugging"""
    print("Options:")
    for key, value in opts.items():
        print("  {}: {}".format(key, value))


def _do_snapshot(snapper, opts):
    """Do snapshot"""
    snapper.snapshot()
    if opts["cleanup"]:
        snapper.cleanup(keep=opts["keep"])


def _do_list(snapper):
    """Do list"""
    snapshots = snapper.list_snapshots()
    for snap in snapshots:
        print("- snapshot: {}".format(snap["snapshot"]))
        print("  start_time: {}".format(snap["start_time"]))
        print("  end_time: {}".format(snap["end_time"]))
        print("  version: {}".format(snap["version"]))
        print("  indices: {}".format(len(snap["indices"])))
        print("  state: {}".format(snap["state"]))


def _do_restore(snapper, opts):
    """Do restore"""
    name = opts["snapshot"] if "snapshot" in opts else "latest"
    ignore_missing = opts["ignore_missing"]
    wait_for = opts["wait_for"]
    snapper.restore(name, ignore_missing=ignore_missing, wait_for=wait_for)


def _do_cleanup(snapper, opts):
    keep = opts["keep"]
    snapper.cleanup(keep=keep)


if __name__ == '__main__':
    main()
