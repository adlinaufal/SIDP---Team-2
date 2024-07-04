import serial

from gps_utils_testing import GetGPSData

if __name__ == "__main__":
    uart_port = "/dev/ttyS0"

    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    
    latitude, longitude = GetGPSData(gps)
    if latitude is not None and longitude is not None:
        print("Latitude:", latitude)
        print("Longitude:", longitude)
    else:
        print("Failed to retrieve GPS coordinates.")
