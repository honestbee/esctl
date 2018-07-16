# fixme - from repo url
# REPO ?= honestbee/search
REPO = $(shell git config --get remote.origin.url | awk -F":" '{print $$2}' | cut -d"." -f1)
IMAGE = $(REPO)
VERSION ?= latest
REGION ?= ap-southeast-1

build:
	docker build -t $(IMAGE):$(VERSION) .

run: build
	docker run $(IMAGE):$(VERSION)