#!/usr/bin/python3

from argparse import ArgumentParser
from pathlib import Path


def get_webcam():
    """Get webcam usb."""
    cameras = []
    for product in Path("/sys/bus/usb/devices").glob("*/product"):
        if "camera" in product.read_text().lower():
            cameras.append(str(product).split("/")[-2])
    return cameras


def get_webcam_status(webcam: str):
    """Get webcam driver status."""
    return Path(f"/sys/bus/usb/devices/{webcam}/driver").exists()


def disable_webcam(webcam: str):
    with Path("/sys/bus/usb/drivers/usb/unbind").open("w") as f:
        f.write(webcam)


def enable_webcam(webcam: str):
    with Path("/sys/bus/usb/drivers/usb/bind").open("w") as f:
        f.write(webcam)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--disable", action="store_true")
    parser.add_argument("--enable", action="store_true")
    args = parser.parse_args()
    webcams = get_webcam()

    if len(webcams) > 1:
        print("Warning: Multiple cameras found...")

    if not webcams:
        print("No webcams found")

    for webcam in webcams:
        if args.disable:
            if not webcam:
                raise FileNotFoundError("Unable to find webcam")
            disable_webcam(webcam)
        elif args.enable:
            if not webcam:
                raise FileNotFoundError("Unable to find webcam")
            enable_webcam(webcam)
        else:
            if not webcam:
                print(f"Device {webcam}: Not found when querying status.")
            else:
                if get_webcam_status(webcam):
                    print(f"Device {webcam}: Recording!")
                else:
                    print(f"Device {webcam}: Offline.")
