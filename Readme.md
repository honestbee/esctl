# esctl -  Elasticsearch Toolkit

## Building

Setup venv and install dependencies:

```sh
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
./main.py
```

Or build and run Docker image:

```sh
make build
docker run honestbee/esctl:latest
```

## Usage

Run without params or `./main.py -h` for help on all available commands/command groups. Common parameters:

| Flag              | Env Var         | Meaning                                         |
|-------------------|-----------------|-------------------------------------------------|
| `--url`           |                 | Base URL of ES cluster                          |
| `--http-user`     | `HTTP_USER`     | HTTP user for basic auth if required by cluster |
| `--http-password` | `HTTP_PASSWORD` | Password for basic auth, if required            |

### Cluster

Cluster info:

```sh
./main.py cluster info --url $URL
```

Change cluster settings (e.g. shard rebalancing):

```sh
./main.py cluster settings --url $URL --key=cluster.routing.allocation.enable --value=all
```

### Snapshots

For S3 snapshots, an existing buckets name must be passed to the CLU, but AWS IAM credentials need 
to be provided to the cluster, _not_ to `esctl`.

List snapshots:

```sh
./main.py snapshot ls --url=$URL --bucket=$BUCKET --region=$REGION
```

Take new snapshot:

```sh
./main.py snapshot create --url=$URL --bucket=$BUCKET --region=$REGION
```

Restore from (latest) snapshot:

Take new snapshot:

```sh
./main.py snapshot restore --url=$URL --bucket=$BUCKET --region=$REGION
```

For each subcommand, use the `-h` for additional snapshots.
