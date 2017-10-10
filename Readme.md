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
docker run -it snapper snapshot --url $ES_URL --bucket-name $BUCKET_NAME --region $REGION
```

Restore from latest snapshot:

```sh
docker run -it snapper restore --url $ES_URL --bucket-name $BUCKET_NAME --region $REGION
```

## Kubernetes

- Copy and edit the manifests in `example/` as needed, then `kubectl create -f ...`
- Or using `envsubst` (part of `gettext`, on macOS [check this](https://stackoverflow.com/a/37192554/853237)):

```sh
export ES_URL=http://es.example.com
export ES_REPLICA=http://es-replica.example.com
export IMAGE_NAME=http://registry.example.com/es-replicator
export BUCKET_NAME=my-es-replication-bucket
cat example/job.yml | envsubst | kubectl create -f -
```
