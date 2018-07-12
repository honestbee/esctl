"""Factory for command line argument parser"""

import argparse
from os import environ as env


GROUP = dict(
    SNAPSHOT="snapshot",
    CLUSTER="cluster"
)


ACTION = dict(
    SNAPSHOT_CREATE="create",
    SNAPSHOT_RESTORE="restore",
    SNAPSHOT_CLEANUP="cleanup",
    SNAPSHOT_LIST="ls",
    CLUSTER_REBALANCE="rebalancing",
    CLUSTER_STATUS="status",
)


DEFAULT_KEEP = "5"


def arg_parser():
    """Set up command line args and returns the resulting ArgumentParser"""

    default_args = _default_parser()
    snapshot_args = _snapshot_parser()

    parser = argparse.ArgumentParser(description="Elasticsearch snapshot utility")

    sp_main = parser.add_subparsers(help="Command group to execute", dest="group")

    p_snapshots = sp_main.add_parser(GROUP["SNAPSHOT"])
    p_cluster = sp_main.add_parser(GROUP["CLUSTER"])

    # Snapshot subcommands
    sp_snapshots = p_snapshots.add_subparsers(help="Snapshot commands", dest="action")
    sp_cluster = p_cluster.add_subparsers(help="Cluster level settings", dest="action")

    # Snapshot - create command
    p_snapshot = sp_snapshots.add_parser(ACTION["SNAPSHOT_CREATE"], parents=[default_args, snapshot_args])

    p_snapshot.add_argument("--cleanup",
                            required=False,
                            dest="cleanup",
                            action="store_true")
    p_snapshot.add_argument("--keep",
                            default=DEFAULT_KEEP,
                            required=False,
                            type=int)

    # Snapshot - Restore command
    p_restore = sp_snapshots.add_parser(ACTION["SNAPSHOT_RESTORE"], parents=[default_args, snapshot_args])

    p_restore.add_argument("--snapshot", "--name",
                            default="latest")
    p_restore.add_argument("--wait-for",
                            default="green",
                            choices=("red", "yellow", "green"))
    p_restore.add_argument("--ignore-missing",
                            required=False,
                            dest='ignore_missing',
                            action='store_true')

    # Snapshot - List command
    sp_snapshots.add_parser(ACTION["SNAPSHOT_LIST"], parents=[default_args, snapshot_args])

    # Snapshot - Cleanup command
    p_cleanup = sp_snapshots.add_parser(ACTION["SNAPSHOT_CLEANUP"], parents=[default_args, snapshot_args])
    p_cleanup.add_argument("--keep",
                            default=DEFAULT_KEEP,
                            required=False,
                            type=int)

    # Cluster - rebalancing
    p_rebalance = sp_cluster.add_parser(ACTION["CLUSTER_REBALANCE"], parents=[default_args])
    p_rebalance.add_argument("--value",
                            required=True,
                            choices=["on", "off"],
                            type=str)

    sp_cluster.add_parser(ACTION["CLUSTER_STATUS"], parents=[default_args])

    return parser


def _snapshot_parser():
    """Args required for ES snapshots"""

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("--bucket",
                        required=True,
                        help="S3 Bucket name (must exist)")
    parser.add_argument("--region",
                        required=True,
                        help="AWS region to use")
    parser.add_argument("--repo",
                        default="snapper-snapshots",
                        required=False,
                        help="Name of the repo to use")

    return parser


def _default_parser():
    """Common args used by all sub parsers"""

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("--url",
                        required=True,
                        help="URL of ES cluster to work on")

    parser.add_argument("--http-user",
                        default=env.get("HTTP_USER"),
                        required=False,
                        dest="http_user",
                        help="HTTP Basic user if server requires auth")
    parser.add_argument("--http-password",
                        default=env.get("HTTP_PASSWORD"),
                        required=False,
                        dest="http_password",
                        help="HTTP Basic password if server requires auth")

    return parser
