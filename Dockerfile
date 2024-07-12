FROM python:3.12-alpine

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y libusb-1.0.0 pipx

COPY --chmod=755 src/ ./
RUN pipx install hatch

RUN hatch build

RUN pipx install --force .

CMD pipx run --spec . start_telemetry
