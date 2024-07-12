import sys
import serial
import time

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

def IsValidGpsinfo(gps):
    data = gps.readline()
    msg_str = str(data, encoding="utf-8")
    msg_list = msg_str.split(",")
    
    latitude = None
    longitude = None

    if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
        print()
        if msg_list[GPGSA_dict['mode2']] == "1":
            print("!!!!!!Positioning is invalid!!!!!!")
            return None, None

    if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
        print()
        print("*****The GGA info is as follows: *****")
        for key, value in GPGGA_dict.items():
            if key == "latitude":
                lat_str = msg_list[GPGGA_dict[key]]
                if lat_str != '':
                    Len = len(lat_str.split(".")[0])
                    d = int(lat_str[0:Len-2])
                    m = float(lat_str[Len-2:])
                    latitude = lat_str
                    #latitude = (d, m, msg_list[GPGGA_dict['NorS']])
            elif key == "longitude":
                lon_str = msg_list[GPGGA_dict[key]]
                if lon_str != '':
                    Len = len(lon_str.split(".")[0])
                    d = int(lon_str[0:Len-2])
                    m = float(lon_str[Len-2:])
                    longitude = lon_str
                    #longitude = (d, m, msg_list[GPGGA_dict['EorW']])
    
    return latitude, longitude

def main():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        latitude, longitude = IsValidGpsinfo(gps)
        if latitude and longitude:
            print("\nExtracted Coordinates:")
            print("Latitude: {} degrees {} minutes {}".format(latitude[0], latitude[1], latitude[2]))
            print("Longitude: {} degrees {} minutes {}".format(longitude[0], longitude[1], longitude[2]))
            break
    
if __name__ == "__main__":
    sys.exit(main())
