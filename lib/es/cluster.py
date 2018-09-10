from lib.es.client import Client
import json

def new_cluster(url, user=None, password=None):
    client = Client(url, user, password)
    cluster = Cluster(client)
    return cluster
    

class Cluster:

    def __init__(self, es_client):
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


    def settings_set(self, key, value, transient=False):
        """Modify cluster settings"""
        payload = {}
        payload["persistent" if not transient else "transient"] = {key: value}
        data, _ = self._client.do_put("/_cluster/settings", payload)
        return data


    def settings_get(self):
        """Get cluster wide value"""
        data, _ = self._client.do_get("/_cluster/settings")
        return data


    def toggle_rebalancing(self, value):
        """Set cluster wide shard rebalancing to on or off"""
        return self.settings("cluster.routing.allocation.enable", value)
