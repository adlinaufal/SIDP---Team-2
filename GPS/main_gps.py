import sys
from gps_utils import GetGPSData

gps_data_file = "gps_data.txt"  # Path to the file containing GPS data

if __name__ == "__main__":
    with open(gps_data_file, 'r') as gps:
        latitude, longitude = GetGPSData(gps)
        print("Latitude:", latitude)
        print("Longitude:", longitude)
