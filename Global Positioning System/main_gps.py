import sys
from gps_utils import GetGPSData

gps_data_file = "gps_data.txt"  # Path to the file containing GPS data



if __name__ == "__main__":
    with open(gps_data_file, 'r') as gps:
        utc_time, latitude, longitude = GetGPSData(gps)
        print("UTC Time:", utc_time)
        print("Latitude:", latitude)
        print("Longitude:", longitude)
