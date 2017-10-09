# Elasticsearch Replicator

- Fork this repo
- Build from Dockerfile
- Or use drone build
- Change image name in .drone.yml as needed to push to your own registry

## AWS Credentials

- The replication job does not need access to S3 itself
- However, the ES clusters doing the snapshotting/restoration do

## Using the Samples

- Copy and edit the manifests in `example/` as needed, then `kubectl create -f ...`
- Alternatively, via envsubst (part of gettext, `brew install gettext`)
- Note: you need to `brew link --force gettext` as in [here](https://stackoverflow.com/a/37192554/853237)

```sh
export ES_URL=http://es.example.com
export ES_REPLICA=http://es-replica.example.com
export IMAGE_NAME=http://registry.example.com/es-replicator
export BUCKET_NAME=my-es-replication-bucket
cat example/job.yml | envsubst | kubectl create -f -
```
