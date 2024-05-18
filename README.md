# Telemetry system

__Telemetry system__ is divided into two variants: ~_Plug&Play_~ and _xBee_.

### xBee

__xBee__ is a student made telemetry variant. It is designed to use the least
possible amount of power, whilst satisfying regulations enforced by tournament
organizers. List of components:

- [STM32F103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html)

This variant has a limited bandwidth, but it still satisfies current telemetry
system needs.

### ~Plug&Play~ (discontinued)

__Plug&Play__ is designed using third-party components. Its main goal is to
quickly develop entire telemetry system. List of third-party components:

- [Kvaser Ethercan HS](https://www.kvaser.com/product/kvaser-ethercan-hs/#/!)
- [Loco5AC](https://dl.ui.com/qsg/Loco5AC/Loco5AC_EN.html)

Substantial drawback of this system is big power consumption (~7W). Once _xBee_
variant is complete this _Plug&Play_ could be used as a redundancy system.

___EDIT:___ Plug&Play has a very large power consumption. Further development is not planned.

## xBee - Escort car antenna

On the escort vehicle, __xBee__ should be located at the height of the windshield.  
Its purpose is to read data from the __challanger antenna__ and store it in InfluxDB.

### Usage

#### Prerequisites:

1. Install [Winows Subsytem Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) on your host machine.
1. Install [docker-compose](https://docs.docker.com/compose/install/) on the WSL.
1. Install [usbipd](https://github.com/dorssel/usbipd-win/releases) on the host machine.
1. Install **usbip** on the WSL:
    ```
    sudo apt upgrade
    sudo apt install -y linux-tools-virtual hwdata usbip
    ```

#### Start process:

1. Get repo and enter directory:
    ```
    git clone https://github.com/VorobiovM/solis solis
    cd solis
    ```
1. Copy *src_rx/config/config_template.ini* to *src_rx/config/config.ini* and modify your credentials.
    ```
    cp src_rx/config/config_template.ini src_rx/config/config.ini
    nano src_rx/config/config.ini
    ```
1. Start container and attach to its shell:

    ```
    docker compose up
    ```

#### Stop process:

To stop the app, run the following commands in container's bash `exit`.  
If you started docker in detached mode `docker compose down`.

### Ports

The services in the app run on the following ports:

| Host Port    | Service      | Docker Port  |
| ------------ | ------------ | ------------ |
| 8080         | InfluxDB     | 8086         |


> If docker container is running as a detached process, you can connect to it by running following commands in bash:
> 
> ```
> docker container ls
> docker container attach <CONTAINER_ID>
> ```

### Volumes

The app creates the following named volumes so data is not lost when the app is stopped:

| Volume           | Description                          |
| ---------------- | ------------------------------------ |
| influx_db        | Data volume for storage persistancy. |
| src              | Python scripts for processing CAN.   |
| templates        | Dashboards for InfluxDB.             |

### Users

The app creates an admin users. Default values of the username and password is set inside *.env* file. To override the default credentials, set the following environment variables before starting the container:

- `INFLUX_USERNAME`
- `INFLUX_PASSWORD`

### Database

The app creates a default InfluxDB database called `solis`.
