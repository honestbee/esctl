"""Bridge between CLI and cluster level actions"""

from lib.es.cluster import new_cluster
import json


def status(**args):
    cluster = _from_args(**args)
    status = cluster.status()
    print("Cluster name:       {}".format(status["cluster_name"]))
    print("Cluster status:     {}".format(status["status"]))
    print("Num. nodes:         {}".format(status["number_of_nodes"]))
    print("Num. data nodes:    {}".format(status["number_of_data_nodes"]))
    print("Unassigned shards:  {}".format(status["unassigned_shards"]))
    print("Pending tasks:      {}".format(status["number_of_pending_tasks"]))


def set_rebalancing(value, **args):
    cluster = _from_args(**args)
    data = cluster.toggle_rebalancing(value)
    _print_response(data)


def settings_set(key, value, transient, **args):
    cluster = _from_args(**args)
    print(key, value, transient)
    data = cluster.settings_set(key, value, transient)
    _print_response(data)


def settings(**args):
    cluster = _from_args(**args)
    data = cluster.settings_get()
    _print_response(data)


def _from_args(**args):
    return new_cluster(
        args["url"], 
        args["user"], 
        args["password"])


def _print_response(data):
    print(json.dumps(data, sort_keys=True, indent=2))
