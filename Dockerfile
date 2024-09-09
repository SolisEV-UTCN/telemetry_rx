FROM python:3.12-alpine

WORKDIR /usr/src/app

RUN apk update
RUN apk add libusb

COPY ./ ./

RUN python -m pip install .

ENTRYPOINT [ "python", "telemetry_rx/__main__.py", "listen", "--adapter", "USB", "--address", "/dev/ttyUSB0" ]
