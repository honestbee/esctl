COMMAND := "snapshot"

snapshot:
	COMMAND=snapshot TSTAMP=`date +%s` envsubst < example/job.yml | kubectl create -f -

restore:
	COMMAND=restore TSTAMP=`date +%s` envsubst < example/job.yml | kubectl create -f -

cleanup:
	kubectl delete job -l job=es-snapshot-snapshot
	kubectl delete job -l job=es-snapshot-restore
