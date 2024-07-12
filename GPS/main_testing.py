import sys
import time
import serial
from gps_utils_testing import GetGPSData

uart_port = "/dev/ttyS0"

def main():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        latitude, longitude = GetGPSData(gps)
        if latitude and longitude:
            print("\nExtracted Coordinates:")
            print("Latitude: {} degrees {} minutes {}".format(latitude[0], latitude[1], latitude[2]))
            print("Longitude: {} degrees {} minutes {}".format(longitude[0], longitude[1], longitude[2]))
            break  # Stop execution once the values are retrieved and printed
        time.sleep(1)
    
    gps.close()

if __name__ == "__main__":
    sys.exit(main())
