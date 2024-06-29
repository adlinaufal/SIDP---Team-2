from gps_utils_testing import GetGPSData

if __name__ == "__main__":
    latitude, longitude = GetGPSData()
    if latitude is not None and longitude is not None:
        print("Latitude:", latitude)
        print("Longitude:", longitude)
    else:
        print("Failed to retrieve GPS coordinates.")
