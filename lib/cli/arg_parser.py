"""Factory for command line argument parser"""

import argparse
import lib.cli.snapper as snapper
import lib.cli.cluster as cluster
from os import environ as env

DEFAULT_KEEP = "5"

def arg_parser():
    """Set up command line args and returns the resulting ArgumentParser"""

    # Top-level parser
    main_parser = argparse.ArgumentParser(description="Elasticsearch utility")
    main_sp = main_parser.add_subparsers(help="Commands")

    # Default options for all commands
    defaults = argparse.ArgumentParser(add_help=False)
    defaults.add_argument("--url",
                        required=False,
                        default=env.get("CLUSTER_URL", None),
                        help="Cluster to work on (default: CLUSTER_URL from env)")
    defaults.add_argument("--debug", "-d",
                        required=False,
                        action="store_true",
                        help="Toggle debug output")
    defaults.add_argument("--user",
                        default=env.get("HTTP_USER"),
                        required=False,
                        dest="user",
                        help="HTTP Basic user if server requires auth")
    defaults.add_argument("--password",
                        default=env.get("HTTP_PASSWORD"),
                        required=False,
                        dest="password",
                        help="HTTP Basic password if server requires auth")

    # Default args for snapshots
    snapshot_defaults = argparse.ArgumentParser(add_help=False, parents=[defaults])
    snapshot_defaults.add_argument("--bucket",
                                    required=False,
                                    help="S3 Bucket name (must exist)")
    snapshot_defaults.add_argument("--region",
                                    required=False,
                                    help="AWS region to use")
    snapshot_defaults.add_argument("--repo",
                                    default="snapper-snapshots",
                                    required=False,
                                    help="Name of the repo to use (default: snapper-snapshots)")

    # Snapshot sub-commands
    snapshot_parser = main_sp.add_parser("snapshot", help="Snapshot sub-commands")
    snapshot_sp = snapshot_parser.add_subparsers(title="Snapshot commands")

    # Snapshot - Create
    snapshot_create = snapshot_sp.add_parser(
                            "create", 
                            help="create snapshot",
                            parents=[snapshot_defaults])
    snapshot_create.add_argument("--cleanup",
                            required=False,
                            dest="cleanup",
                            action="store_true")
    snapshot_create.add_argument("--keep",
                            default=DEFAULT_KEEP,
                            required=False,
                            type=int)
    snapshot_create.set_defaults(func=snapper.create)

    # Snapshot - Restore
    snapshot_restore = snapshot_sp.add_parser(
                            "restore", 
                            help="restore from snapshot",
                            parents=[snapshot_defaults])
    snapshot_restore.add_argument("--snapshot", "--name",
                            default="latest")
    snapshot_restore.add_argument("--wait-for",
                            default="green",
                            choices=("red", "yellow", "green"))
    snapshot_restore.add_argument("--ignore-missing",
                            required=False,
                            dest='ignore_missing',
                            action='store_true')
    snapshot_restore.set_defaults(func=snapper.restore)

    # Snapshot - List
    snapshot_ls = snapshot_sp.add_parser(
                            "ls", 
                            help="list snapshots",
                            parents=[snapshot_defaults])
    snapshot_ls.set_defaults(func=snapper.ls)

    # Snapshot - Cleanup
    snapshot_cleanup = snapshot_sp.add_parser(
                            "cleanup", 
                            help="clean up old snapshots", 
                            parents=[snapshot_defaults])
    snapshot_cleanup.add_argument("--keep",
                            default=DEFAULT_KEEP,
                            required=False,
                            type=int)
    snapshot_cleanup.set_defaults(func=snapper.cleanup)

    # Cluster commands
    cluster_parser = main_sp.add_parser("cluster", help="Cluster sub-commands")
    cluster_sp = cluster_parser.add_subparsers(title="Cluster sub-commands")

    # Cluster set settings
    cluster_set = cluster_sp.add_parser(
                            "set", 
                            help="Set cluster wide settings",
                            parents=[defaults])
    cluster_set.add_argument("--key",
                            required=True,
                            type=str)
    cluster_set.add_argument("--value",
                            required=True,
                            type=str)
    cluster_set.add_argument("--transient",
                            required=False,
                            action="store_true")
    cluster_set.set_defaults(func=cluster.settings_set)

    # Cluster get settings
    cluster_settings = cluster_sp.add_parser(
                            "settings", 
                            help="Get cluster wide settings",
                            parents=[defaults])
    cluster_settings.set_defaults(func=cluster.settings)
    
    # Cluster status
    cluster_status = cluster_sp.add_parser(
                            "status", 
                            help="Get cluster status",
                            parents=[defaults])
    cluster_status.set_defaults(func=cluster.status)

    # Cluster rebalance settings
    cluster_rebalance = cluster_sp.add_parser(
                            "rebalance", 
                            help="Set cluster rebalancing",
                            parents=[defaults])
    cluster_rebalance.add_argument("--value",
                            choices=["all", "primaries", "new_primaries", "none"],
                            required=True,
                            type=str)
    cluster_rebalance.set_defaults(func=cluster.set_rebalancing)

    return main_parser
