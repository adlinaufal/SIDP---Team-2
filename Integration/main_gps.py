import sys
import serial
from gps_utils import GetGPSData, uart_port, CoordinatestoLocation, read_gps_data_from_file

def main():
    count = 0
    while count < 10:
        gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
        latitude, longitude = GetGPSData(gps)
        if latitude is not None and longitude is not None:
            return latitude, longitude
        count += 1
    
    if latitude is None and longitude is None:
        latitude, longitude = read_gps_data_from_file()
    
    return latitude, longitude

