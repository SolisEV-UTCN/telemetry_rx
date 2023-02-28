# Telemetry system

**Telemetry system** is divided into two variants: _Plug&Play_ and _xBee_.

### Plug&Play

**Plug&Play** is designed using third-party components. Its main goal is to
quickly develop entire telemetry system. List of third-party components:

- [Kvaser Ethercan HS](https://www.kvaser.com/product/kvaser-ethercan-hs/#/!)
- [Loco5AC](https://dl.ui.com/qsg/Loco5AC/Loco5AC_EN.html)

Substantial drawback of this system is big power consumption (~7W). Once _xBee_
variant is complete this _Plug&Play_ could be used as a redundancy system.

### xBee

**xBee** is a student made telemetry variant. It is designed to use the least
possible amount of power, whilst satisfying regulations enforced by tournament
organizers. List of components:

- [STM32F103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html)

This variant has a limited bandwidth, but it still satisfies current telemetry
system needs.

## Quick Start

To start the app:

1. Install [docker-compose](https://docs.docker.com/compose/install/) on the docker host.
1. Clone this repo on the docker host.
1. Optionally, change default credentials or Grafana provisioning.
1. Run the following command from the root of the cloned repo:

```
docker-compose up -d
```

To stop the app:

1. Run the following command from the root of the cloned repo:

```
docker-compose down
```

## Ports

The services in the app run on the following ports:

| Host Port      | Service    |
| -------------- | ---------- | ------------ |
| 3000           | Grafana    |
| 8086           | InfluxDB   |
| 127.0.0.1:8888 | Chronograf | (not needed) |

Note that Chronograf does not support username/password authentication. Anyone who can connect to the service has full admin access. Consequently, the service is not publically exposed and can only be access via the loopback interface on the same machine that runs docker.

If docker is running on a remote machine that supports SSH, use the following command to setup an SSH tunnel to securely access Chronograf by forwarding port 8888 on the remote machine to port 8888 on the local machine:

```
ssh [options] <user>@<docker-host> -L 8888:localhost:8888 -N
```

## Volumes

The app creates the following named volumes (one for each service) so data is not lost when the app is stopped:

- influxdb-storage
- chronograf-storage (not needed)
- grafana-storage

## Users

The app creates two admin users - one for InfluxDB and one for Grafana. By default, the username and password of both accounts is `admin`. To override the default credentials, set the following environment variables before starting the app:

- `INFLUXDB_USERNAME`
- `INFLUXDB_PASSWORD`
- `GRAFANA_USERNAME`
- `GRAFANA_PASSWORD`

## Database

The app creates a default InfluxDB database called `solis_telemetry`.
