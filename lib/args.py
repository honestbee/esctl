"""Command line arg parser and definitions for snapper"""

import argparse

ACTION = dict(
    SNAPSHOT="snapshot",
    RESTORE="restore",
    CLEANUP="cleanup",
    LIST="ls"
)

DEFAULT_KEEP = 5


def arg_parser():
    """Set up command line args and returns the resulting ArgumentParser"""

    parser = argparse.ArgumentParser(description="Elasticsearch snapshot utility")
    subparsers = parser.add_subparsers(help='command to execute', dest='command')

    # Create each sub parser and add default arguments
    parser_snapshot = subparsers.add_parser(ACTION["SNAPSHOT"])
    _default_args(parser_snapshot)

    parser_restore = subparsers.add_parser(ACTION["RESTORE"])
    _default_args(parser_restore)

    parser_list = subparsers.add_parser(ACTION["LIST"])
    _default_args(parser_list)

    parser_cleanup = subparsers.add_parser(ACTION["CLEANUP"])
    _default_args(parser_cleanup)

    # Additional args for 'snapshot' command
    parser_snapshot.add_argument("--cleanup",
                                 required=False,
                                 dest="cleanup",
                                 action="store_true")
    parser_snapshot.add_argument("--keep",
                                 required=False,
                                 type=int,
                                 default=DEFAULT_KEEP)

    # Additional args for 'restore' command
    parser_restore.add_argument("--snapshot", "--name",
                                default="latest")
    parser_restore.add_argument("--wait-for",
                                default="green",
                                choices=("red", "yellow", "green"))
    parser_restore.add_argument("--ignore-missing",
                                required=False,
                                dest='ignore_missing',
                                action='store_true')

    # Additional args for 'cleanup' command
    parser_cleanup.add_argument("--keep",
                                required=False,
                                type=int,
                                default=DEFAULT_KEEP)

    return parser


def _default_args(parser):
    """Add common args used by all sub parsers"""

    parser.add_argument("--bucket-name",
                        required=True,
                        help="S3 Bucket name (must exist)")
    parser.add_argument("--region",
                        required=True,
                        help="AWS region to use")
    parser.add_argument("--repo-name",
                        default="snapper-snapshots",
                        help="Name of the repo to use")
    parser.add_argument("--url",
                        required=True,
                        help="URL of ES cluster to work on")
    parser.add_argument("--wait-for-cluster",
                        required=False,
                        dest='wait_for_cluster',
                        action='store_true')
    parser.add_argument("--http-user",
                        required=False,
                        dest="http_user",
                        help="HTTP Basic user if server requires auth")
    parser.add_argument("--http-password",
                        required=False,
                        dest="http_password",
                        help="HTTP Basic password if server requires auth")
