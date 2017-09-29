#!/bin/sh

set -e

RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[1;32m'
NC='\033[0m'

function usage() {
    echo "The following env vars must be set: BUCKET_NAME, REGION, REPO_NAME, ES_URL, ES_REPLICA" 2>&1
    exit 1
}

# BUCKET_NAME='elasticsearch-snapshots-517285003183'
# REGION='ap-southeast-1'
# REPO_NAME='replication'

# ES_URL=http://es-staging-in.honestbee.com
# ES_REPLICA=http://es-staging-datateam.honestbee.com

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
            curl -s -XPUT -H 'Content-Type: application/json' -d "$payload" "$url/_snapshot/$repo"
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

exit 99

# create snapshot
echo "--"
echo "Taking snapshot of $ES_URL"
curl --fail -s $ES_URL/_snapshot/$REPO_NAME/$TSTAMP -XPUT > /dev/null

echo "Waiting for snapshot to complete"
while true; do
    STATE=`curl --fail -s $ES_URL/_snapshot/$REPO_NAME/_all | jq -r ".snapshots[] | {id: .snapshot, state: .state}  | select(.id == \"$TSTAMP\").state"`

    case $STATE in
        SUCCESS)
            printf "\rSnapshot $TSTAMP complete\n"
            break
            ;;
        IN_PROGRESS)
            printf "\rState=$STATE, waiting..."
            sleep 2
            ;;
        *)
            echo "Unexpected snapshot state: '$STATE' - exiting" 1>&2
            exit 1
            ;;
    esac
done

INDICES=`curl --fail -s -H "Content-type: application/json" $ES_REPLICA/_cat/indices | jq -r '.[].index'`

echo "--"
echo "Closing indices on $ES_REPLICA"
for IDX in $INDICES; do
    echo "Closing index $IDX"
    curl --fail -s -XPOST $ES_REPLICA/$IDX/_close > /dev/null
done

echo "--"
echo "Restoring snapshot $TSTAMP to $ES_REPLICA"
curl -s --fail $ES_REPLICA/_snapshot/$REPO_NAME/$TSTAMP/_restore -H "content-type: application/json" -XPOST -d '{"include_global_state": false}' > /dev/null

echo "Restoration started"
while true; do
    CLUSTER_STATE=`curl --fail -s $ES_REPLICA/_cat/health -H "content-type: application/json" | jq -r '.[].status' | tail -n 1`

    case $CLUSTER_STATE in
        'green')
            printf "\rCluster state is ${GREEN}$CLUSTER_STATE${NC}           \n"
            break
            ;;
        'yellow')
            printf "\rCluster state is ${YELLOW}$CLUSTER_STATE${NC}, waiting..."
            sleep 2
            ;;
        'red')
            printf "\rCluster state is ${RED}$CLUSTER_STATE${NC}, waiting...   "
            sleep 2
            ;;
        *)
            echo "Unexpected cluster state: '$CLUSTER_STATE' - exiting" 1>&2
            exit 1
            ;;
    esac
done

echo "Replication complete!"
