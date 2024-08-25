FROM python:3.12-alpine

WORKDIR /usr/src/app

RUN apk update
RUN apk add libusb pipx

COPY ./ ./
RUN python -m pip install .

CMD python telemetry_rx/__main__.py
