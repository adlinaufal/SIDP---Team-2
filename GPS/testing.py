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

def is_valid_gpsinfo(gps):
    data = gps.readline()
    msg_str = str(data, encoding="utf-8")
    msg_list = msg_str.split(",")

    if (msg_list[GPGSA_dict['msg_id']] == "$GPGSA"):
        if msg_list[GPGSA_dict['mode2']] == "1":
            return None, None

    if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
        latitude = None
        longitude = None
        if msg_list[GPGGA_dict["latitude"]]:
            latitude = msg_list[GPGGA_dict["latitude"]]
        if msg_list[GPGGA_dict["longitude"]]:
            longitude = msg_list[GPGGA_dict["longitude"]]
        return latitude, longitude

    return None, None
