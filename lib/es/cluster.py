from lib.es.client import Client
import json

def new_cluster(opts):
    client = Client(opts)
    cluster = Cluster(client, opts)
    return cluster

class Cluster:

    def __init__(self, es_client, opts):
        self._client = es_client

    
    def status(self):
        data, _ = self._client.do_get("_cluster/health")
        return dict(
            cluster_name=data["cluster_name"],
            status=data["status"],
            number_of_nodes=data["number_of_nodes"],
            number_of_data_nodes=data["number_of_data_nodes"],
            unassigned_shards=data["unassigned_shards"],
            delayed_unassigned_shards=data["delayed_unassigned_shards"],
            number_of_pending_tasks=data["number_of_pending_tasks"],
        )


    def toggle_rebalancing(self, enable):
        """Set cluster wide shard rebalancing to on or off"""

        val = "all" if enable else "none"
        payload = {"transient": {"cluster.routing.allocation.enable": val}}

        data, _ = self._client.do_put("/_cluster/settings", payload)
        return data
