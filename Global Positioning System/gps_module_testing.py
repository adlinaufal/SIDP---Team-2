import os
from gps_utils import GetGPSData

GPS_DEVICE_PATH = "/dev/ttyUSB0"  # Replace with your actual GPS device path

def read_gps_data(device_path):
    with open(device_path, 'r') as gps:
        while True:
            line = gps.readline()
            if line:
                yield line.strip()

if __name__ == "__main__":
    try:
        gps_data = read_gps_data(GPS_DEVICE_PATH)
        for data in gps_data:
            utc_time, latitude, longitude = GetGPSData([data])
            if utc_time and latitude and longitude:
                print("UTC Time:", utc_time)
                print("Latitude:", latitude)
                print("Longitude:", longitude)
                break
            else:
                print("Positioning failed or invalid data.")
                break
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print("Error:", e)
