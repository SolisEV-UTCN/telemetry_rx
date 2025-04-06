# Telemetry RX

A Python-based telemetry data collection and storage system designed specifically for solar vehicle data acquisition. This project is part of the Solis EV telemetry subsystem, focused on receiving, processing, and storing CAN (Controller Area Network) data in InfluxDB for real-time monitoring and analysis.

## Features

- Real-time CAN data collection via USB or UDP
- Support for multiple transmission protocols (RF, LTE)
- Offline data parsing from SD card recordings
- InfluxDB integration for time-series data storage
- DBC file support for CAN message decoding
- Modular design for easy protocol switching

## Variants

Telemetry subsystems are designed to be modular in order, so it is easier to switch between variants. Each variant was developed to overcome specific race conditions and track environments.

### RF (BWSC 2023)

Transmission over RF using *xBee* was developed for BWSC 2023. It was designed to transmit data between the solar car and an escort vehicle. Transmission is done via 802.15.4 standard, which is specifically created for low power power applications.

#### Components:
- [Nucleo STM32F103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html) - Main microcontroller
- [Digi xBee 3 802.15.4](https://www.digi.com/resources/documentation/digidocs/PDFs/90002273.pdf) - RF transceiver

#### Specifications:
- Bandwidth: 230400bps (configurable up to 1Mbps)
- Power consumption: 0.1Wh
- Data format: USART bytestream
- Range: Up to 1km line of sight
- Latency: <100ms

### LTE (iLumen 2024)

For iLumen European Solar Challange 2024, we developed transmission over LTE. Circuit Zolder has sufficient GSM coverage to efficiently use LTE. Binary data is transmitted from an antena located on the solar car to a server via UDP socket.

#### Components:
- [Nucleo STM32F103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html) - Main microcontroller
- [itbrainpower u-GSM](https://itbrainpower.net/u-GSM/features.php) - GSM modem
- [Digi xBee 3 Low-Power LTE](https://www.digi.com/resources/documentation/digidocs/PDFs/90002420.pdf) - LTE transceiver

#### Specifications:
- Bandwidth: 230400bps
- Power consumption: 0.66Wh
- Data format: UDP packets
- Network: 4G LTE
- Requirements: Functional SIM card with data roaming

### HTTP (Discontinued)

This variant was developed in an *Plug'n Play* style but has been discontinued due to high power consumption.

#### Components:
- [Kvaser Ethercan HS](https://www.kvaser.com/product/kvaser-ethercan-hs/#/!) - CAN interface
- [Loco5AC](https://dl.ui.com/qsg/Loco5AC/Loco5AC_EN.html) - Network device

#### Specifications:
- Bandwidth: Up to 4Gbps (dynamic)
- Power consumption: 7Wh
- Data format: HTTP frames
- Status: Discontinued

## Getting Started

### Prerequisites

1. Python Environment:
   - [Python 3.12](https://www.python.org/downloads/) or higher
   - pip package manager

2. Optional Development Environment:
   - [Windows Subsystem Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) for Windows users
   - [Docker](https://docs.docker.com/compose/install/) for containerized deployment
   - [usbipd](https://github.com/dorssel/usbipd-win/releases) for USB device sharing on Windows
   - usbip for WSL:
     ```bash
     sudo apt upgrade
     sudo apt install -y linux-tools-virtual hwdata usbip
     ```

3. Database:
   - InfluxDB server (v2.x recommended)
   - Write permissions for the specified bucket

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SolisEV-UTCN/telemetry_rx
   cd telemetry_rx
   ```

2. Set up Python virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
   - Windows CMD: `.\.venv\Scripts\activate.bat`
   - Linux/macOS: `source ./.venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install .
   ```

5. Verify installation:
   ```bash
   python telemetry_rx/__main__.py --help
   ```

### Configuration

The application requires two main configuration elements:

1. CAN Database (DBC) file:
   - Located in `telemetry_rx/config/`
   - Contains CAN message definitions
   - Specify path using `--dbc` flag

2. InfluxDB Connection:
   Required parameters (can be provided via command line or environment variables):
   ```
   --influx-url <STR>    # InfluxDB server URL
   --influx-org <STR>    # Organization name
   --influx-token <STR>  # API token with write permissions
   --influx-bucket <STR> # Target bucket name
   ```

   Environment variables:
   - INFLUX_URL
   - INFLUX_ORG
   - INFLUX_TOKEN
   - INFLUX_BUCKET

   Note: API token can also be provided via file using `--influx-token-file <PATH>`

### Usage

#### Live Data Collection

The application supports two modes of live data collection:

1. USB Connection:
   ```bash
   python telemetry_rx/__main__.py \
     --dbc telemetry_rx/config/Solis-EV4.dbc \
     listen \
     --adapter USB \
     --address COM1
   ```

2. UDP Connection:
   ```bash
   python telemetry_rx/__main__.py \
     --dbc telemetry_rx/config/Solis-EV4.dbc \
     listen \
     --adapter UDP \
     --address 0.0.0.0
   ```

#### Offline Data Processing

Process data recorded to SD card:
```bash
python telemetry_rx/__main__.py \
  --dbc <PATH_TO_DBC> \
  parse \
  --path <PATH_TO_DIR>
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
