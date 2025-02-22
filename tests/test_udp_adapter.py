import socket


def udp_client(host="127.0.0.1", port=8333):
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Get user input for the message
        binary_data = bytes([0x66, 0xCB, 0x65, 0x6F, 0x04, 0x01, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07])

        # Send the binary data
        s.sendto(binary_data, (host, port))
        print(f"Sent binary data: {binary_data.hex()}")


if __name__ == "__main__":
    udp_client()
