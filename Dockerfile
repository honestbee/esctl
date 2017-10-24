FROM alpine:3.6

ENV PYTHONUNBUFFERED=yes

RUN apk --no-cache add curl python3 \
 && python3 -m ensurepip \
 && pip3 install --upgrade pip

COPY snapper.py /usr/bin/snapper
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

RUN adduser -DH snapper
USER snapper

ENTRYPOINT ["/usr/bin/snapper"]
CMD ["-h"]
