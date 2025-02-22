FROM python:3.12-alpine

WORKDIR /usr/src/app

RUN apk update
RUN apk add libusb build-base

COPY ./ ./

RUN python -m pip install -e .

ENTRYPOINT [ "python", "src/telemetry_rx/__main__.py", "listen" ]
