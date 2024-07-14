import sys
import serial

from gps_utils import GetGPSData, uart_port
from location import CoordinatestoLocation

def main():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        latitude, longitude = GetGPSData(gps)
        location = CoordinatestoLocation(latitude, longitude)
        if latitude is not None and longitude is not None:
            print("\nLocation: ", location)
            print("Coordinates: {:.6f}, {:.6f}".format(latitude, longitude))
            break

if __name__ == "__main__":
    sys.exit(main())
