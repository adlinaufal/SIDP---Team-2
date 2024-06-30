import sys
from gps_utils import GetGPSData

gps_data_file = "gps_data.txt"                      # Path to the file containing GPS data

if __name__ == "__main__":
    with open(gps_data_file, 'r') as gps:           # Open the GPS data file as read-only
        latitude, longitude = GetGPSData(gps)       # Call GetGPSData with the file object to get the GPS coordinates
        print("Latitude:", latitude)
        print("Longitude:", longitude)
