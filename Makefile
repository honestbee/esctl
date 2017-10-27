COMMAND := "snapshot"
REPO = $(shell git config --get remote.origin.url | awk -F":" '{print $$2}' | cut -d"." -f1)

snapshot: build
	docker run --rm $(REPO) snapshot \
		--url $(API_URL) \
		--bucket-name $(BUCKET_NAME) \
		--region $(REGION) \
		--wait-for-cluster=True

restore: build
	docker run --rm $(REPO) restore \
		--url $(API_URL) \
		--bucket-name $(BUCKET_NAME) \
		--region $(REGION) \
		--wait-for-cluster=True

build:
	docker build -t $(REPO) .
