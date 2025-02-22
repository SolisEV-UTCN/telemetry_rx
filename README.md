# Telemetry

This project is part of telemetry subsystem. It's goal is to store CAN data inside a database. Project is intended to be used from CLI. Database of choice for storage is InfluxDB.

## Variants

Telemetry subsystems are designed to be modular in order, so it is easier to switch between variants. Each variant was developed to overcome specific race conditions and track environments.

### RF

Transmission over RF using *xBee* was developed for BWSC 2023. It was designed to transmit data between the solar car and an escort vehicle. Transmission is done via 802.15.4 standard, which is specifically created for low power power applications. List of components:

- [Nucleo STM32F103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html)
- [Digi xBee 3 802.15.4](https://www.digi.com/resources/documentation/digidocs/PDFs/90002273.pdf)

___Note 1:___ Current bandwidth is set to 230400bps. It is possible to increase it to 1Mbps, but at the cost of a higher power efficiency and an increase of error rate in transmission.

___Note 2:___ Current power consumption is 0.1Wh.

___Note 3:___ Data is received as an USART bytestream.

### LTE

For iLumen European Solar Challange 2024, we developed transmission over LTE. Circuit Zolder has sufficient GSM coverage to efficiently use LTE. Binary data is transmitted from an antena located on the solar car to a server via UDP socket. List of components:

- [Nucleo STM32F103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html)
- [itbrainpower u-GSM](https://itbrainpower.net/u-GSM/features.php)
- [Digi xBee 3 Low-Power LTE](https://www.digi.com/resources/documentation/digidocs/PDFs/90002420.pdf)

___Note 1:___ Current bandwidth is set to 230400bps.

___Note 2:___ Current power consumption is 0.66Wh.

___Note 3:___ Data is received as bytes in UDP packets.

___Note 4:___ A functional SIM card with data roaming is required.

### HTTP (discontinued)

This variant was developed in an *Plug'n Play* style. List of components:

- [Kvaser Ethercan HS](https://www.kvaser.com/product/kvaser-ethercan-hs/#/!)
- [Loco5AC](https://dl.ui.com/qsg/Loco5AC/Loco5AC_EN.html)

___EDIT:___ This variant has a very large power consumption. **Further development is not planned.**

___Note 1:___ Bandwidth is dynamically set by *Loco5AC*. Maximum throughput is 4Gbps.

___Note 2:___ Current power consumption is 7Wh.

___Note 3:___ Data is received in HTTP frames.

## Getting started

### Prerequisites:

1. Install [Python 3.12](https://www.python.org/downloads/)
2. (Optional) Install [Winows Subsytem Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) on your host machine.
3. (Optional) Install [docker](https://docs.docker.com/compose/install/).
4. (Optional) Install [usbipd](https://github.com/dorssel/usbipd-win/releases) on your host machine.
5. (Optional) Install **usbip** on the WSL:
    ```
    sudo apt upgrade
    sudo apt install -y linux-tools-virtual hwdata usbip
    ```

### Installation (Pip)

1. Clone this repository:
    ```
    git clone https://github.com/VorobiovM/telemetry_rx
    cd telemetry_rx
    ```
2. Create a Python virtual environment:
    ```
    python -m venv .venv
    ```
3. Activate Python virtual environment:
    - PowerShell: `.\.venv\Scripts\Activate.ps1`
    - CMD: `.\.venv\Scripts\activate.bat`
    - Bash: `source ./.venv/bin/activate`
4. Download project dependencies:
    ```
    pip install .
    ```
5. Run main script:
    ```
    python telemetry_rx/__main__.py --help
    ```

### Usage

This applcation is designed to run from a command line. It expects to have a working connection to an InfluxDB server and a CAN database file (DBC). CAN database file is located in the `telemetry_rx/config` folder. To pass the file path use `--dbc` flag. To establish a connection to the Influx server, you must provide following options:
```
--influx-url <STR>
--influx-org <STR>
--influx-token <STR>
--influx-bucket <STR>
```

___Note 1:___ InfluxDB parameters can be passed as environment variables (INFLUX_URL, INFLUX_ORG, INFLUX_TOKEN, INFLUX_BUCKET).

___Note 2:___ InfluxDB API token must contain write permissions. It is also possible to pass token in a file using `--influx-token-file <PATH>`.


#### Listen to live traffic:

Telemetry application can collect CAN traffic coming from the solar car over **USB** or **UDP** connection. This is done via `listen` command. Specific connection adapter can be chosen by passing `--adapter` flag.
- To listen to **USB** traffic specify COM port via `--address` flag.
- To bind to a **UDP** server specify its address via `--address` flag.

Example to start USB server on COM1:
```
python telemetry_rx/__main__.py --dbc telemetry_rx/config/Solis-EV4.dbc listen --adapter USB --address COM1
```

Example to start UDP server on all interfaces:
```
python telemetry_rx/__main__.py --dbc telemetry_rx/config/Solis-EV4.dbc listen --adapter UDP --address 0.0.0.0
```

#### Parse offline data:

Telemetry application can also load offline data recorded to an SD card. This is done via `parse` command. Path to directory with offline measurements must be passed in `--path` flag.

Example:
```
python telemetry_rx/__main__.py --dbc <PATH_TO_DBC> parse --path <PATH_TO_DIR>
```
