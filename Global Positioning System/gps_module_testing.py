import os
from gps_utils import GetGPSData

GPS_DEVICE_PATH = "/dev/ttyS0"  # Replace with your actual GPS device path

def read_gps_data(device_path):
    with open(device_path, 'r') as gps:
        line = gps.readline()
        if line:
            return line.strip()
        else:
            return None

if __name__ == "__main__":
    try:
        gps_data = read_gps_data(GPS_DEVICE_PATH)
        if gps_data: 
            utc_time, latitude, longitude = GetGPSData([gps_data])
            if utc_time and latitude and longitude:
                print("UTC Time:", utc_time)
                print("Latitude:", latitude)
                print("Longitude:", longitude)
            else:
                print("Positioning failed or invalid data.")
    except KeyboardInterrupt:
        print("\nInterru[pted by user.]")
    except Exception as e:
        print("Error:", e)
