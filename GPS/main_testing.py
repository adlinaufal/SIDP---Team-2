import sys
from testing import uart_port, is_valid_gpsinfo
import serial

def main():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    latitude, longitude = is_valid_gpsinfo(gps)
    if latitude and longitude:
        print(f"Latitude: {latitude}, Longitude: {longitude}")
    else:
        print("No valid GPS data available.")
    gps.close()

if __name__ == "__main__":
    sys.exit(main())
