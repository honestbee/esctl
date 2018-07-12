"""Bridge between CLI and cluster level actions"""

from lib.es.cluster import new_cluster
from lib.cli.args import ACTION
import json

def cluster_action(action, opts):
    
    cluster = new_cluster(opts)

    if action == ACTION["CLUSTER_STATUS"]:
        _do_cluster_status(cluster, opts)
    elif action == ACTION["CLUSTER_SETTINGS"]:
        _do_cluster_settings(cluster, opts)
    elif action == ACTION["CLUSTER_REBALANCING"]:
        _do_cluster_toggle_rebalancing(cluster, opts)
    else:
        raise Exception("Invalid action '{}'".format(action))


def _do_cluster_status(cluster, opts):
    status = cluster.status()
    print("Cluster name:       {}".format(status["cluster_name"]))
    print("Cluster status:     {}".format(status["status"]))
    print("Num. nodes:         {}".format(status["number_of_nodes"]))
    print("Num. data nodes:    {}".format(status["number_of_data_nodes"]))
    print("Unassigned shards:  {}".format(status["unassigned_shards"]))
    print("Pending tasks:      {}".format(status["number_of_pending_tasks"]))


def _do_cluster_toggle_rebalancing(cluster, opts):
    if "value" in opts:
        value = opts["value"]
    data = cluster.toggle_rebalancing(value)
    _print_cluster_response(data)


def _do_cluster_settings(cluster, opts):
    value = None
    key = None

    if "value" in opts:
        value = opts["value"]
    if "key" in opts:
        key = opts["key"]
    
    data = cluster.settings(key, value)
    _print_cluster_response(data)


def _print_cluster_response(data):
    print("Response from cluster:")
    print(json.dumps(data, sort_keys=True, indent=2))