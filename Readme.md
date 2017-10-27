# Elasticsearch Replicator

## Preconditions

- The replication job does not need AWS creds itself
- However, the ES clusters doing the snapshotting/restoration do
- S3 bucket must exist and the ES cluster must have AWS credentials allowing r/w access to it

## Usage

- Build:

    ```sh
    make build
    ```

- Take snapshot:

    ```sh
    API_URL=<my-api-url> BUCKET_NAME=<my-bucket-name> REGION=<my-region> make snapshot
    ```

- Restore from latest snapshot:

    ```sh
    API_URL=<my-api-url> BUCKET_NAME=<my-bucket-name> REGION=<my-region> make restore
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
    COMMAND=snapshot TSTAMP=`date +%s` envsubst < example/job.yml | kubectl create -f -
    COMMAND=restore TSTAMP=`date +%s` envsubst < example/job.yml | kubectl create -f -
    ```

- To clean up old jobs:

    ```sh
    kubectl delete job -l job=es-snapshot-snapshot
    kubectl delete job -l job=es-snapshot-restore
    ```
