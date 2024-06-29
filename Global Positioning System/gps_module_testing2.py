import sys

# Reference information of the GPGSA format.
GPGSA_dict = {
    "msg_id": 0,
    "mode1": 1,
    "mode2": 2,
    "ch1": 3,
    "ch2": 4,
    "ch3": 5,
    "ch4": 6,
    "ch5": 7,
    "ch6": 8,
    "ch7": 9,
    "ch8": 10,
    "ch9": 11,
    "ch10": 12,
    "ch11": 13,
    "ch12": 14,
}

# Reference information of the GPGGA format.
GPGGA_dict = {
    "msg_id": 0,
    "utc": 1,
    "latitude": 2,
    "NorS": 3,
    "longitude": 4,
    "EorW": 5,
    "pos_indi": 6,
    "total_Satellite": 7,
}

gps_data_file = "gps_data.txt"  # Path to the file containing GPS data

def IsValidGpsinfo(gps):
    utc_time = None
    latitude = None
    longitude = None

    for data in gps:
        # Convert the data to string.
        msg_str = data.strip()
        # Split string with ",".
        msg_list = msg_str.split(",")
        # Parse the GPGSA message.
        if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
            print()
            # Check if the positioning is valid.
            if msg_list[GPGSA_dict['mode2']] == "1":
                print("!!!!!!Positioning is invalid!!!!!!")
            else:
                print("**The positioning type is {}D **".format(msg_list[GPGSA_dict['mode2']]))
        # Parse the GPGGA message.
        if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
            print()
            print("**The GGA info is as follows: **")
            for key, value in GPGGA_dict.items():
                # Parse the utc information.
                if key == "utc":
                    utc_str = msg_list[GPGGA_dict[key]]
                    if not utc_str == '':
                        h = int(utc_str[0:2])
                        m = int(utc_str[2:4])
                        s = float(utc_str[4:])
                        utc_time = "{}:{}:{}".format(h, m, s)
                        print(" utc time: {}".format(utc_time))
                # Parse the latitude information.
                elif key == "latitude":
                    lat_str = msg_list[GPGGA_dict[key]]
                    if not lat_str == '':
                        Len = len(lat_str.split(".")[0])
                        d = int(lat_str[0:Len - 2])
                        m = float(lat_str[Len - 2:])
                        latitude = "{} degree {} minute".format(d, m)
                    print(" {}: {}".format(key, msg_list[GPGGA_dict[key]]))  # (format: ddmm.mmmmm)
                # Parse the longitude information.
                elif key == "longitude":
                    lon_str = msg_list[GPGGA_dict[key]]
                    if not lon_str == '':
                        Len = len(lon_str.split(".")[0])
                        d = int(lon_str[0:Len - 2])
                        m = float(lon_str[Len - 2:])
                        longitude = "{} degree {} minute".format(d, m)
                    print(" {}: {}".format(key, msg_list[GPGGA_dict[key]]))  # (format: ddmm.mmmmm)
            
            # Once we have the data, we can break the loop
            if utc_time and latitude and longitude:
                break

    return utc_time, latitude, longitude

def main():
    with open(gps_data_file, 'r') as gps:
        utc_time, latitude, longitude = IsValidGpsinfo(gps)
        print("UTC Time:", utc_time)
        print("Latitude:", latitude)
        print("Longitude:", longitude)

if __name__ == "__main__":
    sys.exit(main())
