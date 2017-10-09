#!/usr/bin/env python

"""Snapshot and restore utility for Elasticsearch"""

import sys
import time
import json
from uuid import uuid4
import argparse
import requests


def main():
    """Entry point"""

    parser = make_arg_parser()
    args = parser.parse_args()
    args.func(args)


def make_arg_parser():
    """Set up command line args and returns the resulting ArgumentParser"""

    parser = argparse.ArgumentParser(description="Elasticsearch snapshot utility")

    subparsers = parser.add_subparsers()

    parser_snapshot = subparsers.add_parser("snapshot")
    parser_snapshot.set_defaults(func=action_snapshot)
    common_args(parser_snapshot)

    parser_restore = subparsers.add_parser("restore")
    parser_restore.set_defaults(func=action_restore)
    common_args(parser_restore)

    parser_restore.add_argument("--version", default="latest")
    parser_restore.add_argument("--wait-for", default="green", choices=("red", "yellow", "green"))

    return parser


def common_args(parser):
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


def make_opts(args):
    """Takes CLI args passed to the script, converts them to options dict"""
    options = dict(
        bucket_name=args.bucket_name,
        region=args.region,
        repo_name=args.repo_name,
        url=args.url
    )
    return options



def action_snapshot(args):
    """Evaluate arguments and invoke snapshot operation"""

    options = make_opts(args)
    name = str(uuid4())

    do_snapshot(name, options)


def action_restore(args):
    """Evaluate arguments and invoke restore operation"""

    options = make_opts(args)
    name = args.version
    wait_for = args.wait_for

    do_restore(options=options, name=name, wait_for=wait_for)


def check_response(res, expected=(200, 201), message="Unexpected response status"):
    if res.status_code not in expected:
        print(res.text, file=sys.stderr)
        raise Exception(message)


def ensure_repo(repo_url, bucket_name, region):
    """Ensure the elasticsearch snapshot repo at the given url actually exists, if it doesn't,
    create it"""

    res = requests.get(repo_url)

    if res.status_code == 404:

        print("Creating snapshot repository")

        headers = {'Content-type': 'application/json'}
        payload = {
            "type": "s3",
            "settings": {
                "bucket": bucket_name,
                "region": region
            }
        }

        res = requests.put(repo_url, data=json.dumps(payload), headers=headers)
        check_response(res)


def do_snapshot(name, options):
    """Do a snapshot"""

    repo_url = options["url"]+"/_snapshot/"+options["repo_name"]
    snapshot_url = repo_url+"/"+name

    ensure_repo(repo_url, bucket_name=options["bucket_name"], region=options["region"])

    res = requests.put(snapshot_url)
    check_response(res)

    print("Waiting for snapshot to complete ...")

    while True:
        res = requests.get(snapshot_url)
        check_response(res)

        data = res.json()
        state = data["snapshots"][0]["state"]

        if state == "SUCCESS":
            print("Snapshot complete: "+snapshot_url)
            break
        elif state == "IN_PROGRESS":
            time.sleep(2)
            continue
        else:
            raise Exception("Unexpected snapshot state: "+state)


def do_restore(options, name='latest', wait_for='green'):
    """Do a restore"""
    # check if snapshot repo already exists

    # if not create it (an existing S3 bucket might hold snapshots)

    # find requested version or use the latest one if version == 'latest'

    # close all indices that are in the snapshot _and_ the cluster

    # restore snapshot

    # monitor cluster state until desired state (green or yellow is reached)
    print("DO RESTORE")


if __name__ == '__main__':
    main()
