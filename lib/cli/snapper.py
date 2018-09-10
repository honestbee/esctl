"""Bridge between CLI and snapshot level actions"""

from lib.es.snapper import new_snapper

def create(keep, cleanup, **args):
    """Do snapshot"""
    snapper = _from_args(**args)
    snapper.snapshot()
    if cleanup: 
        snapper.cleanup(keep)


def ls(**args):
    """Do list"""
    snapper = _from_args(**args)
    snapshots = snapper.list_snapshots()
    for snap in snapshots:
        print("- snapshot: {}".format(snap["snapshot"]))
        print("  start_time: {}".format(snap["start_time"]))
        print("  end_time: {}".format(snap["end_time"]))
        print("  version: {}".format(snap["version"]))
        print("  indices: {}".format(len(snap["indices"])))
        print("  state: {}".format(snap["state"]))


def restore(snapshot="latest", ignore_missing=True, wait_for="green", **args):
    """Do restore"""
    snapper = _from_args(**args)
    snapper.restore(snapshot, ignore_missing, wait_for)


def cleanup(keep, **args):
    """Cleanup old snapshots"""
    snapper = _from_args(**args)
    snapper.cleanup(keep)


def _from_args(**args):
    return new_snapper(
        url=args["url"], 
        user=args["user"],
        repo=args["repo"],
        bucket=args["bucket"],
        region=args["region"],
        password=args["password"])
