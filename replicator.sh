#!/bin/sh

set -e

function usage() {
    echo "The following env vars must be set: BUCKET_NAME, REGION, REPO_NAME, ES_URL, ES_REPLICA" 2>&1
    exit 1
}

test "$BUCKET_NAME" != "" || usage
test "$REGION" != "" || usage
test "$REPO_NAME" != "" || usage
test "$ES_URL" != "" || usage
test "$ES_REPLICA" != "" || usage

# check if repo exists, create if necessary
# ensure_repo $ES_URL $REPO_NAME
function ensure_repo() {

    url=$1
    repo=$2
    region=$3
    bucket=$4

    status=`curl -s -w"%{http_code}" -o /dev/null $url/_snapshot/$repo`

    case $status in
        "200")
            echo "Repo $url/_snapshot exists"
            ;;
        "404")
            echo "Creating repo $url/_snapshot/$repo"
            payload="{\"type\": \"s3\", \"settings\": {\"bucket\": \"$bucket\", \"region\": \"$region\"}}"
            curl --fail -sS -XPUT -H 'Content-Type: application/json' -d "$payload" "$url/_snapshot/$repo" -o /dev/null
            ;;
        *)
            echo "Unexpected http status code" 2>&1
            ;;
    esac
}

# ensure repo exists on both clusters
ensure_repo $ES_URL $REPO_NAME $REGION $BUCKET_NAME
ensure_repo $ES_REPLICA $REPO_NAME $REGION $BUCKET_NAME
echo "--"


TSTAMP=`date -u +%Y%m%d%H%M%S`

echo "From: $ES_URL"
echo "To: $ES_REPLICA"
echo "Snapshot id/Timestamp: $TSTAMP"
echo "Snapshot repo: $REPO_NAME"

# create snapshot
echo "--"
echo "Taking snapshot of $ES_URL"
curl --fail -sS $ES_URL/_snapshot/$REPO_NAME/$TSTAMP -XPUT -o /dev/null

echo "Waiting for snapshot to complete"
while true; do
    STATE=`curl --fail -sS $ES_URL/_snapshot/$REPO_NAME/_all | jq -r ".snapshots[] | {id: .snapshot, state: .state}  | select(.id == \"$TSTAMP\").state"`

    case $STATE in
        SUCCESS)
            echo "Snapshot $TSTAMP complete"
            break
            ;;
        IN_PROGRESS)
            echo "."
            sleep 2
            ;;
        *)
            echo "Unexpected snapshot state: '$STATE' - exiting" 1>&2
            exit 1
            ;;
    esac
done

INDICES=`curl --fail -sS -H "Content-type: application/json" $ES_REPLICA/_cat/indices | jq -r '.[].index'`

echo "--"
echo "Closing indices on $ES_REPLICA"
for IDX in $INDICES; do
    echo "Index $IDX"
    curl --fail -sS -XPOST $ES_REPLICA/$IDX/_close -o /dev/null
done

echo "--"
echo "Restoring snapshot $TSTAMP to $ES_REPLICA"
curl --fail -sS $ES_REPLICA/_snapshot/$REPO_NAME/$TSTAMP/_restore -H "content-type: application/json" -XPOST -d '{"include_global_state": false}' -o /dev/null

echo "Restoration started. Monitoring cluster state..."
while true; do
    CLUSTER_STATE=`curl --fail -sS $ES_REPLICA/_cat/health -H "content-type: application/json" | jq -r '.[].status' | tail -n 1`

    case $CLUSTER_STATE in
        'green')
            echo "State is $CLUSTER_STATE - done"
            break
            ;;
        'red' | 'yellow')
            echo "State is $CLUSTER_STATE - waiting"
            sleep 3
            ;;
        *)
            echo "Unexpected cluster state: '$CLUSTER_STATE' - exiting" 1>&2
            exit 1
            ;;
    esac
done

echo "--"
echo "Job complete"
