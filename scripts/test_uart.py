"""Verify that the Basys 3 echoes a byte over its USB serial port."""

import argparse

import serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", help="the board's serial port, such as COM5")
    args = parser.parse_args()

    try:
        with serial.Serial(args.port, 115200, timeout=2, write_timeout=2) as connection:
            connection.reset_input_buffer()
            connection.write(b"A")
            reply = connection.read(1)
    except serial.SerialException as error:
        parser.exit(1, f"Could not use {args.port}: {error}\n")

    if not reply:
        parser.exit(1, f"Sent A on {args.port}, but received no reply. Check that uart_echo.bit is loaded.\n")
    if reply != b"A":
        parser.exit(1, f"Sent A (0x41) on {args.port}, but received 0x{reply[0]:02X}.\n")

    print(f"PASS: sent A and received A on {args.port}.")


if __name__ == "__main__":
    main()
