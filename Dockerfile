FROM python:3.12-alpine

WORKDIR /usr/src/app

RUN apk update
RUN apk add libusb build-base

COPY ./ ./

RUN python -m pip install -e .

ENV ADAPTER=${INFLUX_BUCKET}
ENV ADDRESS=${INFLUX_BUCKET}
ENV BUCKET=${INFLUX_BUCKET}
ENV ORG=${INFLUX_ORG}

ENTRYPOINT [ "python", "telemetry_rx/__main__.py", "--influx-bucket", ${BUCKET}, "--influx-org", ${ORG}, "listen", "--adapter", ${ADAPTER}, "--address", ${ADDRESS} ]
