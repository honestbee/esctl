FROM alpine:3.6

RUN apk --no-cache add curl bash
COPY replicator.sh /

CMD ["/replicator.sh"]
