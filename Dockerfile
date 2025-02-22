FROM python:3.12-alpine

WORKDIR /usr/src/app

RUN apk update
RUN apk add libusb build-base

COPY ./ ./

RUN python -m pip install -e .

ENTRYPOINT [ "python", "telemetry_rx/__main__.py", "-vvv", "--influx-bucket", "nires_2025_v2", "listen", "--adapter", "USB", "--address", "/dev/ttyUSB0" ]
