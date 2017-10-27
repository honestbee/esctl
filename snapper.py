#!/usr/bin/env python3

"""Snapshot and restore utility for Elasticsearch"""

import sys
import time
import json
from uuid import uuid4
import argparse
import requests


ACTION_SNAPSHOT = "snapshot"
ACTION_RESTORE = "restore"
ACTION_CLEANUP = "cleanup"


def main():
    """Entry point"""
    parser = make_arg_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
    elif args.command == "snapshot":
        action_snapshot(args)
    elif args.command == "restore":
        action_restore(args)
    else:
        raise Exception("Invalid command: '"+args.command+"'")


def make_arg_parser():
    """Set up command line args and returns the resulting ArgumentParser"""

    parser = argparse.ArgumentParser(description="Elasticsearch snapshot utility")
    subparsers = parser.add_subparsers(help='command to execute', dest='command')

    parser_snapshot = subparsers.add_parser("snapshot")
    add_repo_args(parser_snapshot)

    parser_restore = subparsers.add_parser("restore")
    add_repo_args(parser_restore)

    parser_restore.add_argument("--snapshot", "--name", default="latest")
    parser_restore.add_argument("--wait-for", default="green", choices=("red", "yellow", "green"))

    return parser


def add_repo_args(parser):
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
                        type=bool,
                        default=False)


def make_opts(args):
    """Takes CLI args passed to the script, converts them to options dict"""
    options = dict(
        bucket_name=args.bucket_name,
        region=args.region,
        repo_name=args.repo_name,
        url=args.url
    )
    return options


def make_headers():
    """Generate the default headers for making requests to the ES API"""
    return {'Content-type': 'application/json'}


def action_snapshot(args):
    """Evaluate arguments and invoke snapshot operation"""

    if args.wait_for_cluster:
        wait_for_cluster(args.url)

    options = make_opts(args)
    name = str(uuid4())

    do_snapshot(name, options)


def action_restore(args):
    """Evaluate arguments and invoke restore operation"""

    if args.wait_for_cluster:
        wait_for_cluster(args.url)

    options = make_opts(args)
    name = args.snapshot
    wait_for = args.wait_for

    do_restore(options=options, name=name, wait_for=wait_for)


def check_response(res, expected=(200, 201), message="Unexpected response status"):
    """Check if response status code is within expected values, of not raises an Exception"""
    if res.status_code not in expected:
        print(res.text, file=sys.stderr)
        raise Exception(message)


def ensure_repo(repo_url, bucket_name, region):
    """Ensure the elasticsearch snapshot repo at the given url actually exists, if it doesn't,
    create it"""

    res = requests.get(repo_url)

    if res.status_code == 404:

        print("Creating snapshot repository")

        headers = make_headers()
        payload = {
            "type": "s3",
            "settings": {
                "bucket": bucket_name,
                "region": region
            }
        }

        res = requests.put(repo_url, data=json.dumps(payload), headers=headers)
        check_response(res)


def get_repo_url(cluster_url, repo_name):
    """Generates the repo url for a snapshot repo based on the given options"""
    return cluster_url+"/_snapshot/"+repo_name


def get_index_url(cluster_url, index_name):
    """Generates the url to the given index using the url from options"""
    return cluster_url+"/"+index_name


def get_healthcheck_url(cluster_url):
    """Generates the health check endpoint url"""
    return cluster_url+"/_cat/health"


def get_snapshot_url(cluster_url, repo_name, snapshot_name):
    """Generates the url for given snapshot"""
    repo_url = get_repo_url(cluster_url, repo_name)
    return repo_url+"/"+snapshot_name


def do_snapshot(name, options):
    """Do a snapshot"""

    url = get_repo_url(options["url"], options["repo_name"])
    snapshot_url = url+"/"+name

    ensure_repo(url, bucket_name=options["bucket_name"], region=options["region"])

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


def find_latest_snapshot(repo_url):
    """Find the latest snapshot in the repo at the given url. Returns None if there are no
    snapshots."""

    res = requests.get(repo_url+'/_all', headers=make_headers())
    check_response(res)
    data = res.json()

    if not data["snapshots"]:
        return None

    sorted_snaps = sorted(data["snapshots"], key=lambda snap: snap["start_time"], reverse=True)
    return sorted_snaps[0]


def get_snapshot(repo_url, name):
    """Find the snapshot with the given name. Raises an error if the snapshot was not found"""

    url = repo_url+'/'+name
    res = requests.get(url, headers=make_headers())

    if res.status_code == 404:
        raise Exception("No snapshot with name "+name)
    else:
        check_response(res)
        data = res.json()
        return data["snapshots"][0]


def wait_for_status(cluster_url, expected_state="green"):
    """Poll cluster health state and only terminate when given state is reached"""

    health_url = get_healthcheck_url(cluster_url)

    while True:
        res = requests.get(health_url, headers=make_headers())
        check_response(res)

        data = res.json()

        if data[0]["status"] != expected_state:
            time.sleep(5)
        else:
            break


def wait_for_cluster(cluster_url):
    """Probe cluster health endpoint, return only when status is 200"""

    health_url = get_healthcheck_url(cluster_url)

    print("Waiting for cluster to become available")

    while True:
        res = requests.get(health_url, headers=make_headers())
        status_code = res.status_code
        if status_code != 200:
            print("Cluster response is "+str(status_code)+", waiting")
            time.sleep(5)
        else:
            break


def close_indices(cluster_url, indices):
    """Close list of indices on cluster at given url. If an index does not exist it is ignored"""

    for index_name in indices:
        print("Closing index "+index_name)

        index_url = get_index_url(cluster_url, index_name)
        res = requests.post(index_url+"/_close")

        if res.status_code == 404:
            print("No such index, ignoring")
        else:
            check_response(res)


def do_restore(options, name='latest', wait_for='green'):
    """Do a restore"""

    # check if snapshot repo already exists, if not, create it
    # (an existing bucket might hold snapshots already we can use to restore)
    cluster_url = options["url"]
    repo_name = options["repo_name"]

    repo_url = get_repo_url(cluster_url, repo_name)
    ensure_repo(repo_url, options["bucket_name"], options["region"])

    # find requested version or use the latest one if version == 'latest'
    if name == 'latest':
        snapshot = find_latest_snapshot(repo_url)
        if not snapshot:
            raise Exception("No snapshots found")
    else:
        snapshot = get_snapshot(repo_url, name)

    snapshot_name = snapshot["snapshot"]
    indices = snapshot["indices"]
    start_time = snapshot["start_time"]

    print("Restoring snapshot "+snapshot_name+" taken "+start_time)
    close_indices(cluster_url, indices)

    # restore snapshot
    restore_url = get_snapshot_url(cluster_url, repo_name, snapshot_name)+"/_restore"
    res = requests.post(restore_url)
    check_response(res)

    if wait_for == 'red' or not wait_for:
        return # no need to wait

    print("Waiting for cluster to become "+wait_for)
    wait_for_status(cluster_url, wait_for)

    print("Done restoring from snapshot "+snapshot_name)


if __name__ == '__main__':
    main()
