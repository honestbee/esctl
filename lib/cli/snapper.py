"""Bridge between CLI and snapshot level actions"""

from lib.es.snapper import new_snapper
from lib.cli.args import ACTION


def snapshot_action(action, opts):

    snapper = new_snapper(opts)

    if action == ACTION["SNAPSHOT_CREATE"]:
        _do_snapshot(snapper, opts)
    elif action == ACTION["SNAPSHOT_RESTORE"]:
        _do_restore(snapper, opts)
    elif action == ACTION["SNAPSHOT_LIST"]:
        _do_list(snapper)
    elif action == ACTION["SNAPSHOT_CLEANUP"]:
        _do_cleanup(snapper, opts)
    else:
        raise Exception("Invalid action '{}'".format(action))


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
