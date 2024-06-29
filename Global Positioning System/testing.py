import serial
import sys
from gps_utils import GetGPSData

# Define your UART device path
serial_port_path = '/dev/ttyS0'  # Example, adjust based on your board's configuration

if __name__ == "__main__":
    try:
        with serial.Serial(serial_port_path, baudrate=9600, timeout=1) as serial_port:
            utc_time, latitude, longitude = GetGPSData(serial_port)
            print("UTC Time:", utc_time)
            print("Latitude:", latitude)
            print("Longitude:", longitude)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        sys.exit(1)
