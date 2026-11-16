"""Send and verify one 32-by-32 grayscale test image on the Basys 3."""

import argparse
from time import sleep

import serial

FRAME_WIDTH = 32
FRAME_HEIGHT = 32
HEADER = b"\xA5"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", help="the board's serial port, such as COM5")
    args = parser.parse_args()
    image = bytes(
        ((index * 37) ^ (index >> 3)) & 0xFF
        for index in range(FRAME_WIDTH * FRAME_HEIGHT)
    )

    try:
        with serial.Serial(args.port, 115200, timeout=2, write_timeout=2) as connection:
            # Allow a partial request from an earlier attempt to time out.
            sleep(0.15)
            connection.reset_input_buffer()
            connection.write(HEADER + image)
            reply = connection.read(len(image))
    except serial.SerialException as error:
        parser.exit(1, f"Could not use {args.port}: {error}\n")

    if len(reply) != len(image):
        parser.exit(
            1,
            f"Expected 1,024 bytes, received {len(reply):,}. Check that frame_echo.bit is loaded.\n",
        )

    if reply != image:
        index = next(i for i, (sent, received) in enumerate(zip(image, reply)) if sent != received)
        row, column = divmod(index, FRAME_WIDTH)
        parser.exit(
            1,
            f"Pixel at row {row}, column {column} differed: sent {image[index]}, got {reply[index]}.\n",
        )

    print(f"PASS: all 1,024 pixels matched on {args.port}.")


if __name__ == "__main__":
    main()
