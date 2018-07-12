FROM alpine:3.6

ENV PYTHONUNBUFFERED=yes

RUN apk --no-cache add curl python3 \
 && python3 -m ensurepip \
 && pip3 install --upgrade pip

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

COPY main.py /src/esctl
COPY lib/ /src/lib

RUN adduser -DH esctl
USER esctl

ENTRYPOINT ["/src/esctl"]
CMD ["-h"]
