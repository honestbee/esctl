# Elasticsearch Replicator

## Usage

- The replication job does not need AWS creds itself
- However, the ES clusters doing the snapshotting/restoration do

Build:

```sh
docker build -t snapper .
```

Take snapshot:

```sh
docker run -it snapper snapshot --url $API_URL --bucket-name $BUCKET_NAME --region $REGION
```

Restore from latest snapshot:

```sh
docker run -it snapper restore --url $API_URL --bucket-name $BUCKET_NAME --region $REGION
```

## Kubernetes

- Make sure `kubectl config current-context` matches expectations
- Set up your environment:

    ```sh
    export API_URL=http://es.example.com
    export IMAGE_NAME=http://registry.example.com/es-snapper
    export BUCKET_NAME=my-es-replication-bucket
    ```

- Take or restore snapshot:

    ```sh
    make snapshot
    make restore
    ```

- To clean up old jobs:

    ```sh
    make cleanup
    ```
