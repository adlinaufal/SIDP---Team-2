import re
import os
import fcntl
import time
import sys

# Reference information of the GPGSA format:
# The detail info, please see https://docs.novatel.com/OEM7/Content/Logs/GPGSA.htm?tocpath=Commands%20%2526%20Logs%7CLogs%7CGNSS%20Logs%7C_____63

# Reference information of the GPGGA format:
# The detail info, please see https://docs.novatel.com/OEM7/Content/Logs/GPGGA.htm?tocpath=Commands%20%2526%20Logs%7CLogs%7CGNSS%20Logs%7C_____59

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

uart_port = "/dev/ttyS0"

# Determine whether the GPS data conforms to the UTC format
def time_format(time):
    RE = re.compile(r"^\d{6}.\d{2}$")
    return bool(RE.search(time))

# Determine whether the GPS data conforms to the latitude format
def latitude_format(lat):
    RE = re.compile(r"^\d{4}.\d{5}$")
    return bool(RE.search(lat))

# Determine whether the GPS data conforms to the longitude format
def longitude_format(lon):
    RE = re.compile(r"^\d{5}.\d{5}$")
    return bool(RE.search(lon))

def IsValidGpsinfo(gps_fd):
    data = os.read(gps_fd, 1024)
    if not data:
        return
    
    # Convert the data to string
    msg_str = data.decode('utf-8')
    # Split string with ","
    msg_list = msg_str.split(",")

    # Parse the GPGSA message
    if msg_list[GPGSA_dict["msg_id"]] == "$GPGSA":
        print()
        # Check if the positioning is valid
        if msg_list[GPGSA_dict["mode2"]] == "1":
            print("!!!!!!Positioning is invalid!!!!!!")
        else:
            print("*****The positioning type is {}D *****".format(msg_list[GPGSA_dict["mode2"]]))
            print("The Satellite ID of channel {} : {}")
            # Parse the channel information of the GPGSA message
            if len(msg_list) == 18:
                for id in range(0, 12):
                    key_name = list(GPGSA_dict.keys())[id + 3]
                    value_id = GPGSA_dict[key_name]
                    if msg_list[value_id]:
                        print("                           {} : {}".format(key_name, msg_list[value_id]))
            else:
                print("GPGSA data invalid")

    # Parse the GPGGA message
    if msg_list[GPGGA_dict["msg_id"]] == "$GPGGA":
        print()
        print("*****The GGA info is as follows: *****")
        for key, value in GPGGA_dict.items():
            # Parse the utc information
            if key == "utc":
                utc_str = msg_list[GPGGA_dict[key]]
                if time_format(utc_str):
                    h = int(utc_str[0:2])
                    m = int(utc_str[2:4])
                    s = float(utc_str[4:])
                    print(" utc time: {}:{}:{}".format(h, m, s))
                    print(" {} time: {} (format: hhmmss.sss)".format(key, msg_list[GPGGA_dict[key]]))
                else:
                    print(" UTC data invalid")
            # Parse the latitude information
            elif key == "latitude":
                lat_str = msg_list[GPGGA_dict[key]]
                if latitude_format(lat_str):
                    Len = len(lat_str.split(".")[0])
                    d = int(lat_str[0:Len - 2])
                    m = float(lat_str[Len - 2:])
                    print(" latitude: {} degree {} minute".format(d, m))
                    print(" {}: {} (format: dddmm.mmmmm)".format(key, msg_list[GPGGA_dict[key]]))
                else:
                    print(" Latitude data invalid")
            # Parse the longitude information
            elif key == "longitude":
                lon_str = msg_list[GPGGA_dict[key]]
                if longitude_format(lon_str):
                    Len = len(lon_str.split(".")[0])
                    d = int(lon_str[0:Len - 2])
                    m = float(lon_str[Len - 2:])
                    print(" longitude: {} degree {} minute".format(d, m))
                    print(" {}: {} (format: dddmm.mmmmm)".format(key, msg_list[GPGGA_dict[key]]))
                else:
                    print(" Longitude data invalid")
            else:
                print(" {}: {}".format(key, msg_list[GPGGA_dict[key]]))

def main():
    gps_fd = os.open(uart_port, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    fcntl.fcntl(gps_fd, fcntl.F_SETFL, os.O_NONBLOCK)
    while True:
        try:
            IsValidGpsinfo(gps_fd)
        except KeyboardInterrupt:
            break
        time.sleep(1)

    os.close(gps_fd)

if __name__ == "__main__":
    sys.exit(main())
