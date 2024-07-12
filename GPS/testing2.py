'''
Please make sure the NEO-6M is connected to the correct pins.
The following table describes how to connect NEO-6M to the 40-pin header
-----------------------------------------
Passive Buzzer___Pin Number_____Pin Name
 VCC 4 5 V Power
 GND 6 GND
 TXD 10 UART RX
 RXD 8 UART TX
----------------------------------------
'''
import sys
import time
import os
import fcntl
import termios

# Reference information of the GPGSA format.
'''
Example 1 (GPS only):
$GPGSA,M,3,17,02,30,04,05,10,09,06,31,12,,,1.2,0.8,0.9*35
Example 2 (Combined GPS and GLONASS):
$GNGSA,M,3,17,02,30,04,05,10,09,06,31,12,,,1.2,0.8,0.9*2B
$GNGSA,M,3,87,70,,,,,,,,,,,1.2,0.8,0.9*2A
----------------------------------------------------------
SN Field
 Description
 Symbol
 Example
----------------------------------------------------------
1 $GPGSA
 Log header. For information about the log headers, see ASCII, Abbreviated ASCII or Binary.
 N/A
 $GPGSA
2 mode MA
 Mode: 1 = Fix not available; 2 = 2D; 3 = 3D
 x
 3
3 mode 123
 Latitude (DDmm.mm)
 llll.ll
 5106.9847
4-15 prn
 PRN numbers of satellites used in solution (null for unused fields), total of 12 fields
 GPS = 1 to 32
 SBAS = 33 to 64 (add 87 for PRN number)
 GLO = 65 to 96
 xx,xx,.....
 18,03,13,25,16,24,12,20,,,,
The detail info, please see 
 https://docs.novatel.com/OEM7/Content/Logs/GPGSA.htm?tocpath=Commands%20%2526%20Logs%7CLogs%7CGNSS%20Logs%7C_
____63
'''
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
'''
Example 1 (GPS only):
$GPGSA,M,3,17,02,30,04,05,10,09,06,31,12,,,1.2,0.8,0.9*35
Example 2 (Combined GPS and GLONASS):
$GNGSA,M,3,17,02,30,04,05,10,09,06,31,12,,,1.2,0.8,0.9*2B
$GNGSA,M,3,87,70,,,,,,,,,,,1.2,0.8,0.9*2A
---------------------------------------------------------
SN Field
 Description
 Symbol
 Example
---------------------------------------------------------
1 $GPGGA
 Log header. For information about the log headers, see ASCII, Abbreviated ASCII or Binary.
 N/A
 $GPGGA
2 utc
 UTC time status of position (hours/minutes/seconds/ decimal seconds)
 hhmmss.ss
 202134.00
3 lat
 Latitude (DDmm.mm)
 llll.ll
 5106.9847
4 lat dir
 Latitude direction (N = North, S = South)
 a
 N
5 lon
 Latitude direction (N = North, S = South)
 yyyyy.yy
 11402.2986
6 lon dir
 Longitude direction (E = East, W = West)
 a
 W
7 quality
 refer to Table: GPS Quality Indicators
 x
 1
8 # sats
 Number of satellites in use. May be different to the number in view
 xx
 10
The detail info, please see 
 https://docs.novatel.com/OEM7/Content/Logs/GPGGA.htm?tocpath=Commands%20%2526%20Logs%7CLogs%7CGNSS%20Logs%7C_
____59
'''
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
baudrate = 9600

def set_serial_config(fd, speed):
    iflag = 0
    oflag = 0
    cflag = 0
    lflag = 0

    if speed == 230400:
        cflag |= termios.B230400
    elif speed == 115200:
        cflag |= termios.B115200
    elif speed == 57600:
        cflag |= termios.B57600
    elif speed == 38400:
        cflag |= termios.B38400
    elif speed == 19200:
        cflag |= termios.B19200
    elif speed == 9600:
        cflag |= termios.B9600
    elif speed == 4800:
        cflag |= termios.B4800
    elif speed == 2400:
        cflag |= termios.B2400
    elif speed == 1200:
        cflag |= termios.B1200
    elif speed == 300:
        cflag |= termios.B300

    cflag |= termios.CS8 | termios.CLOCAL | termios.CREAD
    lflag &= ~(termios.ECHO | termios.ICANON)
    iflag = termios.IGNPAR
    oflag = 0
    oflag &= ~(termios.OPOST)

    newtio = [cflag, iflag, oflag, lflag, 0, [0] * termios.NCCS]
    newtio[4] = 5
    newtio[5] = 0

    termios.tcsetattr(fd, termios.TCSANOW, newtio)

def read_gps_data(fd):
    rcv_buf = ""
    while True:
        try:
            data = os.read(fd, 2048)
            rcv_buf += data.decode('utf-8')
            if rcv_buf.endswith('\r\n'):
                break
        except Exception as e:
            print(f"Read error: {e}")
            break
    return rcv_buf

def parse_gps_data(data):
    msg_list = data.split(",")
    
    if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
        print()
        if msg_list[GPGSA_dict['mode2']] == "1":
            print("!!!!!!Positioning is invalid!!!!!!")
        else:
            print("*****The positioning type is {}D *****".format(msg_list[GPGSA_dict['mode2']]))
            for id in range(0, 12):
                key_name = list(GPGSA_dict.keys())[id + 3]
                value_id = GPGSA_dict[key_name]
                if msg_list[value_id]:
                    print(" {} : {}".format(key_name, msg_list[value_id]))

    if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
        print()
        print("*****The GGA info is as follows: *****")
        for key, value in GPGGA_dict.items():
            if key == "utc":
                utc_str = msg_list[GPGGA_dict[key]]
                if utc_str:
                    h = int(utc_str[0:2])
                    m = int(utc_str[2:4])
                    s = float(utc_str[4:])
                    print(" utc time: {}:{}:{}".format(h,m,s))
                print(" {} time: {} (format: hhmmss.sss)".format(key, msg_list[GPGGA_dict[key]]))
            elif key == "latitude":
                lat_str = msg_list[GPGGA_dict[key]]
                if lat_str:
                    Len = len(lat_str.split(".")[0])
                    d = int(lat_str[0:Len-2])
                    m = float(lat_str[Len-2:])
                    print(" latitude: {} degree {} minute".format(d, m))
                print(" {}: {} (format: dddmm.mmmmm)".format(key, msg_list[GPGGA_dict[key]]))
            elif key == "longitude":
                lon_str = msg_list[GPGGA_dict[key]]
                if lon_str:
                    Len = len(lon_str.split(".")[0])
                    d = int(lon_str[0:Len-2])
                    m = float(lon_str[Len-2:])
                    print(" longitude: {} degree {} minute".format(d, m))
                print(" {}: {} (format: dddmm.mmmmm)".format(key, msg_list[GPGGA_dict[key]]))
            else:
                print(" {}: {}".format(key, msg_list[GPGGA_dict[key]]))

def main():
    fd = os.open(uart_port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    set_serial_config(fd, baudrate)
    print("UART1 is opened!")
    print("Starting GPS data parsing...")
    
    while True:
        gps_data = read_gps_data(fd)
        if gps_data:
            parse_gps_data(gps_data)

if __name__ == "__main__":
    main()