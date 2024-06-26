import sys
import time

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
                print("The Satellite ID of channel {} : {}".format("N/A", "N/A"))  # Placeholder
                # Parse the channel information of the GPGSA message.
                for id in range(0, 12):
                    key_name = list(GPGSA_dict.keys())[id + 3]
                    value_id = GPGSA_dict[key_name]
                    if not (msg_list[value_id] == ''):
                        print(" {} : {}".format(key_name, msg_list[value_id]))
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
                        print(" utc time: {}:{}:{}".format(h, m, s))
                    print(" {} time: {} (format: hhmmss.sss)".format(key, msg_list[GPGGA_dict[key]]))
                # Parse the latitude information.
                elif key == "latitude":
                    lat_str = msg_list[GPGGA_dict[key]]
                    if not lat_str == '':
                        Len = len(lat_str.split(".")[0])
                        d = int(lat_str[0:Len - 2])
                        m = float(lat_str[Len - 2:])
                        print(" latitude: {} degree {} minute".format(d, m))
                    print(" {}: {} (format: dddmm.mmmmm)".format(key, msg_list[GPGGA_dict[key]]))
                # Parse the longitude information.
                elif key == "longitude":
                    lon_str = msg_list[GPGGA_dict[key]]
                    if not lon_str == '':
                        Len = len(lon_str.split(".")[0])
                        d = int(lon_str[0:Len - 2])
                        m = float(lon_str[Len - 2:])
                        print(" longitude: {} degree {} minute".format(d, m))
                    print(" {}: {} (format: dddmm.mmmmm)".format(key, msg_list[GPGGA_dict[key]]))
                else:
                    print(" {}: {}".format(key, msg_list[GPGGA_dict[key]]))

def main():
    with open(gps_data_file, 'r') as gps:
        while True:
            IsValidGpsinfo(gps)
            time.sleep(1)

if __name__ == "_main_":
    sys.exit(main())