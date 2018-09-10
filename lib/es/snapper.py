"""Module implements a class to make snapshot requests against the Elasticsearch API"""

import sys
import time
import json
from uuid import uuid4
import requests
from retrying import retry
from lib.es.client import Client


def new_snapper(url, repo, bucket, region, user, password):
    client = Client(url, user, password)
    snapper = Snapper(client, repo, bucket, region)
    return snapper


class Snapper:
    """Tool to manage snapshots on an ES cluster"""


    def __init__(self, es_client, repo="snapper-snapshots", bucket=None, region=None):
        self._client = es_client
        self._repo_name = repo
        self._bucket_name = bucket
        self._region = region


    def snapshot(self):
        """Do a snapshot"""

        name = str(uuid4())
        snapshot_url = "_snapshot/{}/{}".format(self._repo_name, name)

        self._ensure_repo()

        # PUT snapshot url creates the snapshot
        print("Snapshot url: "+snapshot_url)
        self._client.do_put(snapshot_url)

        # Poll snapshot state and wait until it changes to 'SUCCESS'
        print("Waiting for snapshot to complete ...")
        while True:
            data, _ = self._client.do_get(snapshot_url)
            state = data["snapshots"][0]["state"]

            if state == "SUCCESS":
                print("Snapshot complete: "+snapshot_url)
                break
            elif state == "IN_PROGRESS":
                time.sleep(2)
                continue
            else:
                raise Exception("Unexpected snapshot state: "+state)


    def restore(self, name="latest", ignore_missing=False, wait_for="green"):
        """Do a restore"""

        # An existing S3 bucket might already hold snapshots we can use to restore
        # Check if snapshot repo already exists, if not, create it
        self._ensure_repo()

        repo_url = "_snapshot/{}".format(self._repo_name)
        snapshot_info = None

        # Find requested version or use the latest one if version == 'latest'
        if name == 'latest':
            snapshot_info = self._find_latest_snapshot()
        else:
            snapshot_info = self._get_snapshot(repo_url, name)

        if not snapshot_info:
            if not ignore_missing:
                raise Exception("No snapshots found")
            else:
                print("No snapshot to restore, ignoring")
                return

        snapshot_name = snapshot_info["snapshot"]
        indices = snapshot_info["indices"]
        start_time = snapshot_info["start_time"]

        print("Restoring snapshot "+snapshot_name+" taken "+start_time)
        self._close_indices(indices)

        # restore snapshot
        restore_url = "_snapshot/{}/{}/_restore".format(self._repo_name, snapshot_name)
        self._client.do_post(restore_url)

        if wait_for == "red" or not wait_for:
            return # no need to wait

        print("Waiting for cluster to become "+wait_for)
        self._wait_for_status(wait_for)

        print("Done restoring from snapshot "+snapshot_name)


    def list_snapshots(self, sort_reverse=False):
        """List all snapshots"""

        self._ensure_repo()

        data, _ = self._client.do_get("_snapshot/{}/_all".format(self._repo_name))

        sorted_snaps = sorted(
            data["snapshots"],
            key=lambda s: s["start_time"],
            reverse=sort_reverse
        )

        return sorted_snaps


    def cleanup(self, keep=5):
        """Cleanup old snapshots"""
        snaps = self.list_snapshots(sort_reverse=True)
        delete = snaps[keep:]

        print("Cleaning up, will keep {} latest snapshot(s)".format(keep))
        for snap in delete:
            self._delete_snapshot(snap["snapshot"])
            print("Snapshot {} from {} deleted".format(snap["snapshot"], snap["start_time"]))


    def _ensure_repo(self):
        """Ensure the elasticsearch snapshot repo at the given url actually exists, if it doesn't,
        create it"""

        repo_url = "_snapshot/{}".format(self._repo_name)
        _, res = self._client.do_get(repo_url, expected=(200, 404))

        if res.status_code == 404:
            print("Snapshot repo '{}' does not exist, trying to create it".format(self._repo_name))
            self._create_repo(repo_url)
        else:
            print("Snapshot repo '{}' already exists".format(self._repo_name))


    def _create_repo(self, repo_url):
            if self._bucket_name is None:   
                raise Exception("Value for `bucket` is not provided")
            if self._region is None:
                raise Exception("Value for `region` is not provided")

            settings = {
                "type": "s3",
                "settings": {
                    "bucket": self._bucket_name,
                    "region": self._region
                }
            }
            self._client.do_put(repo_url, payload=settings)
            print("Repo created")


    def _find_latest_snapshot(self):
        """Find the latest snapshot in the repo at the given url. Returns None if there are no
        snapshots."""
        snapshots = self.list_snapshots(sort_reverse=True)
        if not snapshots:
            return None
        else:
            return snapshots[0]


    def _get_snapshot(self, repo_url, name):
        """Find the snapshot with the given name. Raises an error if the snapshot was not found"""

        url = repo_url+'/'+name
        data, res = self._client.do_get(url, expected=(200, 404))

        if res.status_code == 404:
            return None
        else:
            return data["snapshots"][0]


    def _wait_for_status(self, expected_state="green"):
        """Poll cluster health state and only terminate when given state is reached"""
        while True:
            data, _ = self._client.do_get("_cat/health")
            if data[0]["status"] != expected_state:
                time.sleep(5)
            else:
                break


    def _close_indices(self, indices):
        """Close list of indices on cluster at given url. If index does not exist it is ignored"""
        for index_name in indices:
            print("Closing index "+index_name)
            self._client.do_post(index_name+"/_close", expected=(200, 404))


    def _delete_snapshot(self, name):
        """Delete snapshot given by name"""
        url = "_snapshot/{}/{}".format(self._repo_name, name)
        self._client.do_delete(url)
