FROM alpine:3.6

RUN apk --no-cache add curl jq
COPY replicator.sh /

CMD ["/replicator.sh"]
