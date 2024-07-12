import sys
import serial
from gps_utils import IsValidGpsinfo, uart_port

def main():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        latitude, longitude = IsValidGpsinfo(gps)
        if latitude is not None and longitude is not None:
            print("\nExtracted Coordinates:")
            print("{:.6f}, {:.6f}".format(latitude, longitude))
            break

if __name__ == "__main__":
    sys.exit(main())
