import sys
import serial
from gps_utils import GetGPSData, uart_port, CoordinatestoLocation

def read_gps_data_from_file(filename='gps_data.txt'):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            latitude_line = lines[0].strip()
            longitude_line = lines[1].strip()
            latitude = float(latitude_line.split(': ')[1])
            longitude = float(longitude_line.split(': ')[1])
            return latitude, longitude
    except (FileNotFoundError, IndexError, ValueError) as e:
        print(f"Error reading GPS data from file: {e}")
        return None, None

def main():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)

    latitude, longitude = GetGPSData(gps)
        
    if latitude is None or longitude is None:
        latitude, longitude = read_gps_data_from_file()

    location = CoordinatestoLocation(latitude, longitude)
    print("\nLocation: ", location)
    print("Coordinates: {:.6f}, {:.6f}".format(latitude, longitude))


if __name__ == "__main__":
    sys.exit(main())
